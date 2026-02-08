from __future__ import annotations
from typing import TYPE_CHECKING
from lark import Lark, Transformer as t
import lark
import os, sys
from context import Context
import parameter
import instruction

__dir__ = os.path.dirname(__file__)

class Transformer(t):
    def __init__(self, visit_tokens = True):
        super().__init__(visit_tokens)
    
    def get_const_or_label(self, name):
        if name in self.constants:
            return self.constants[name]
        elif name in self.labels:
            return self.labels[name]
        else:
            raise NameError(f"`{name}` is not defined")

    class Node:
        def __init__(self, value):pass
        
        def eval(self, context:Context=None):pass

        def __repr__(self):
            return f"<Invalid Node>"

    class Branch(Node):
        def __init__(self, value:list[Transformer.Node]):
            self.children = value
        
        def eval(self, context:Context):
            pass
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.children})"
    
    class Leaf(Node):
        def __init__(self, token:lark.Token):
            self.value = token.value
            self.token = token
        
        def eval(self):
            return self.value

    class start(Branch):
        def __repr__(self):
            return " ".join([repr(value) for value in self.children])
        
        def eval(self, context):
            codegens = [child for child in self.children if isinstance(child,Transformer.codegen_block)]
            non_codegens = [child for child in self.children if child not in codegens]

            for child in non_codegens:
                child.eval(context)

            self.functions = [child for child in self.children if isinstance(child,Transformer.code_block)]
            self.data = [child for child in self.children if isinstance(child,Transformer.data_block)]
            self.main = None
            for func in self.functions:
                print(func.name)
                if func.name.value == "main":
                    self.main = func
                    self.functions.remove(func)
                    break
            else:
                raise SyntaxError("No main defined")

            self.main.eval(context)
            for part in self.data:
                part.eval(context)
            for func in self.functions:
                func.eval(context)
        
        def collect(self, context:Context):
            
            self.main.collect(context)
            for part in self.data:
                part.collect(context)
            for func in self.functions:
                func.collect(context)
        
        def emit(self):
            
            out = []
            
            out.append(self.main.emit())

            for part in self.data:
                out.append(part.emit())
            for func in self.functions:
                out.append(func.emit())
            
            return b"".join(out)

    def transform(self, tree) -> start:
        return super().transform(tree)

    class codegen_block(Branch):
        def __init__(self, value):
            self.name = value[0]
            self.children = value[1:]

        def eval(self, context):
            if self.name:
                self.name = self.name.eval()
                context.add_label(self.name)
            self.codegens = [child for child in self.children if isinstance(child,Transformer.codegen)]
            self.non_codegens = [child for child in self.children if child not in self.codegens]

            for child in self.non_codegens:
                child.eval(context)
            
            for child in self.codegens:
                child.eval(context)
        
        def collect(self, context):
            for item in self.codegens:
                item.collect(context)
        
        def emit(self):
            out = b""
            for item in self.codegens:
                out += item.emit()
            return out
    class codegen(Branch):
        def __init__(self, value):
            super().__init__(value)
            self.value = self.children[0]

        def eval(self, context:Context):
            pass

        def collect(self, context:Context):
            pass
        
        def emit(self):
            return b""

    class code_block(codegen_block):
        def eval(self, context):
            super().eval(context)
            context.inc_pc(2)
        
        def emit(self):
            if self.name == "main":
                return super().emit() + b"\xff\0"
            else:
                return super().emit() + b"\x37\0"

        def __repr__(self):
            return "code " + repr(self.name) + "{" + "; ".join([repr(value) for value in self.children]) + "}"

    class data_block(codegen_block):

        def __repr__(self):
            return "data " + repr(self.name) + "{" + ", ".join([repr(value) for value in self.children]) + "}"

    class instruction(codegen):
        def __init__(self, value):
            super().__init__(value)
            self.command = self.children[0]
            self.args = self.children[1:]

        def eval(self, context):
            self.command = self.command.eval()
            tmp_args = []
            for child in self.args:
                tmp_args.append(child.dry_eval())
            dryinst = instruction.Instruction.from_str(self.command,tmp_args)
            self.position = context.get_pc()
            context.inc_pc(len(dryinst.get(0)))

        def collect(self, context):
            processed_args = []

            for child in self.args:
                processed_args.append(child.eval(context))
            self.out = instruction.Instruction.from_str(self.command, processed_args).get(self.position)
        
        def emit(self):
            return self.out

        def __repr__(self):
            return f"{self.command}({", ".join([repr(value) for value in self.args])})"

    class text(codegen):
        value:Transformer.STRING
        def __repr__(self):
            return f".ascii {self.children[0]}"
        def eval(self, context):
            self.text = self.value.eval()
            context.inc_pc(len(self.text))
        def collect(self, context):
            pass
        def emit(self):
            return self.text.encode('utf-8')
    
    class text_nulterm(text):
        def __repr__(self):
            return f".asciiz {self.children[0]}"
        def eval(self, context):
            super().eval(context)
            self.text = self.text + "\0"
            context.inc_pc(1)
        def emit(self):
            return self.text.encode('utf-8')
    
    class byte(codegen):
        value:Transformer.Leaf
        def __repr__(self):
            return f".byte {self.value}"
        def eval(self, context):
            context.inc_pc(1)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(1)
        def emit(self):
            return self.out

    class word(codegen):
        def __repr__(self):
            return f".word {self.value}"
        def eval(self, context):
            context.inc_pc(2)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(2, byteorder='little')
        def emit(self):
            return self.out
    class double(codegen):
        def __repr__(self):
            return f".double {self.value}"
        def eval(self, context):
            context.inc_pc(4)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(4, byteorder='little')
        def emit(self):
            return self.out
    class quad(codegen):
        def __repr__(self):
            return f".quad {self.value}"
        def eval(self, context):
            context.inc_pc(8)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(8, byteorder='little')
        def emit(self):
            return self.out

    class register(Branch):
        def __init__(self, value):
            value[0] = value[0].lower()
            super().__init__(value)
        def __repr__(self):
            return f"register {self.children[0]}"
        
        def dry_eval(self):
            return parameter.Register(0)

        def eval(self, context):
            if self.children[0] == "a":
                return parameter.Register(0)
            elif self.children[0] == "x":
                return parameter.Register(1)
            elif self.children[0] == "y":
                return parameter.Register(2)
    class immediate(Branch):
        def __repr__(self):
            return f"immediate {self.children[0]}"
        def dry_eval(self):
            return parameter.Immediate(0)
        def eval(self, context):
            return parameter.Immediate(self.children[0].eval(context))
    class direct_addr(Branch):
        def __repr__(self):
            return f"deref {self.children[0]}"
        def dry_eval(self):
            return parameter.Dereference(0)
        def eval(self, context):
            return parameter.Dereference(self.children[0].eval(context))
    class indirect_addr(Branch):
        def __repr__(self):
            return f"deref indirect"
        def dry_eval(self):
            return parameter.IndirectDereference(0)
        def eval(self, context):
            return parameter.IndirectDereference()

    class constantdef(Branch):
        def __init__(self, value):
            super().__init__(value)
            self.name:Transformer.IDENTIFIER = self.children[0]
            self.val:Transformer.expr = self.children[1]
        def __repr__(self):
            return f"{self.name} = {self.val}"
        
        def eval(self, context):
            name = self.name.eval()
            if context.get_local(name):
                raise SyntaxError(f"{name} already defined in this scope")

            context.set(name,self.val.eval(context))
        
    class labeldef(codegen):
        def __repr__(self):
            return f"label {self.children[0]}"
        
        def eval(self, context):
            context.add_label(self.children[0].eval())

    class expr(Branch):
        def __init__(self, value):
            if len(value) == 2:
                self.lhs = value[0]
                self.rhs = value[1]
            else:
                self.rhs = value[0]

    class or_op(expr):
        def __repr__(self):
            return f"({self.lhs} | {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) | self.rhs.eval(context)
    class xor_op(expr):
        def __repr__(self):
            return f"({self.lhs} ^ {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) ^ self.rhs.eval(context)
    class and_op(expr):
        def __repr__(self):
            return f"({self.lhs} & {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) & self.rhs.eval(context)
    class not_op(expr):
        def __repr__(self):
            return f"(~ {self.rhs})"
        def eval(self, context):
            return ~self.rhs.eval(context)
    
    class shiftr(expr):
        def __repr__(self):
            return f"({self.lhs} >> {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) >> self.rhs.eval(context)
    class shiftl(expr):
        def __repr__(self):
            return f"({self.lhs} << {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) << self.rhs.eval(context)
    
    class add(expr):
        def __repr__(self):
            return f"({self.lhs} + {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) + self.rhs.eval(context)
    class sub(expr):
        def __repr__(self):
            return f"({self.lhs} - {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) - self.rhs.eval(context)
    
    class mul(expr):
        def __repr__(self):
            return f"({self.lhs} * {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) * self.rhs.eval(context)
    class div(expr):
        def __repr__(self):
            return f"({self.lhs} / {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) // self.rhs.eval(context)
    
    class unary_sub(expr):
        def __repr__(self):
            return f"(- {self.rhs})"
        def eval(self, context):
            return - self.rhs.eval(context)

    class literal(Branch):
        def __init__(self, value:Transformer.Leaf):
            super().__init__(value)
            self.val = self.children[0]
        def __repr__(self):
            return f"lit {self.val}"
        def eval(self, context):
            return self.val.eval()
    
    class symbol(Branch):
        def __repr__(self):
            return f"symbol {self.children[0]}"
        def eval(self, context):
            name = self.children[0].eval()
            return context.get(name)

    class IDENTIFIER(Leaf):
        def __repr__(self):
            return f"identifer {self.value}"
    
    class INST(Leaf):pass

    class STRING(Leaf):
        def __init__(self,value:str):
            self.value = value[1:-1]
        def eval(self):
            self.value = self.value.replace(r"\n","\n").replace(r"\t","\t").replace(r"\\","\\").replace(r"\"","\"")
            return self.value
    class CHAR(STRING):
        def eval(self):
            super().eval()
            if len(self.value) != 1:
                raise ValueError("CHAR must be a single character")
            self.value = ord(self.value)
            return self.value

    class DECIMAL(Leaf):
        def eval(self):
            return int(self.value)
    class BINARY(Leaf):
        def eval(self):
            return int(self.value,base=2)
    class OCTAL(Leaf):
        def eval(self):
            return int(self.value,base=8)
    class HEX(Leaf):
        def eval(self):
            return int(self.value,base=16)


class Parser:
    def __init__(self):
        self.grammar = open(os.path.join(__dir__,"grammar.lark")).read()
        self.parser = Lark(
            self.grammar,
        )
        self.transformer = Transformer()
    def parse(self, code:str, filename="<main>"):
        transformer = self.transformer
        parser = self.parser

        try:
            parsedTree = parser.parse(code)
        except Exception as pe:
            print(pe)
            return None

        tree = transformer.transform(parsedTree)

        return tree