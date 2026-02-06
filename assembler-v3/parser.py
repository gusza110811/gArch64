from __future__ import annotations
from typing import TYPE_CHECKING
from lark import Lark, Transformer as t
import lark
import os, sys
from context import Context

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
        def __init__(self, value:lark.Token):
            self.value = value.value
        
        def eval(self):
            return self.value
        
        def __repr__(self):
            return f"{self.__class__.__name__} {self.value}"

    class start(Branch):
        def __repr__(self):
            return " ".join([repr(value) for value in self.children])
        
        def eval(self, context):
            codegens = [child for child in self.children if isinstance(child,Transformer.codegen_block)]
            non_codegens = [child for child in self.children if child not in codegens]

            for child in non_codegens:
                child.eval(context)
            
            for child in codegens:
                child.eval(context)
        
        def emit(self,context:Context):
            functions = [child for child in self.children if isinstance(child,Transformer.code_block)]
            data = [child for child in self.children if isinstance(child,Transformer.data_block)]
            main = None
            for func in functions:
                print(func.name)
                if func.name == "main":
                    main = func
                    break
            else:
                raise SyntaxError("No main defined")
            
            out = []
            
            #out.append(main.emit(context))

            #for func in functions:
            #    out.append(func.emit(context))
            for part in data:
                out.append(part.emit(context))
            
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
            self.codegens = [child for child in self.children if isinstance(child,Transformer.codegen)]
            self.non_codegens = [child for child in self.children if child not in self.codegens]

            for child in self.non_codegens:
                child.eval(context)
            
            for child in self.codegens:
                child.eval(context)
        
        def emit(self, context):
            out = b""
            for item in self.children:
                out += item.emit(context)
            return out
    class codegen(Branch):
        def __init__(self, value):
            super().__init__(value)
            self.value = self.children[0]

        def eval(self, context:Context):
            pass
        
        def emit(self,context):
            return b""

    class code_block(codegen_block):

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
            context.inc_pc(2+len(self.args)*4)
        
        def emit(self, context):
            return b"\xEA" + b"".join([arg.eval(context) for arg in self.args]) # \xEA is placeholder

        def __repr__(self):
            return f"{self.command}({", ".join([repr(value) for value in self.args])})"

    class text(codegen):
        value:Transformer.STRING
        def __repr__(self):
            return f".ascii {self.children[0]}"
        def eval(self, context):
            self.text = self.value.eval()
            context.inc_pc(len(self.text))
        def emit(self,context):
            return self.text.encode('utf-8')
    
    class text_nulterm(text):
        def __repr__(self):
            return f".asciiz {self.children[0]}"
        def eval(self, context):
            super().eval(context)
            self.text = self.text + "\0"
            context.inc_pc(1)
        def emit(self,context):
            return self.text.encode('utf-8')
    
    class byte(codegen):
        value:Transformer.Leaf
        def __repr__(self):
            return f".byte {self.value}"
        def eval(self, context):
            context.inc_pc(1)
        def emit(self, context):
            return self.value.eval(context).to_bytes(1)

    class word(codegen):
        def __repr__(self):
            return f".word {self.value}"
        def eval(self, context):
            context.inc_pc(2)
        def emit(self, context):
            return self.value.eval(context).to_bytes(2)
    class double(codegen):
        def __repr__(self):
            return f".double {self.value}"
        def eval(self, context):
            context.inc_pc(4)
        def emit(self, context):
            return self.value.eval(context).to_bytes(4)
    class quad(codegen):
        def __repr__(self):
            return f".quad {self.value}"
        def eval(self, context):
            context.inc_pc(8)
        def emit(self, context):
            return self.value.eval(context).to_bytes(8)

    class register(Branch):
        def __init__(self, value):
            value[0] = value[0].lower()
            super().__init__(value)
        def __repr__(self):
            return f"register {self.children[0]}"
    class immediate(Branch):
        def __repr__(self):
            return f"immediate {self.children[0]}"
    class direct_addr(Branch):
        def __repr__(self):
            return f"deref {self.children[0]}"
    class indirect_addr(Branch):
        def __repr__(self):
            return f"deref indirect"

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

    class expr(Branch):pass

    class or_op(expr):
        def __repr__(self):
            return f"({self.children[0]} | {self.children[1]})"
    class xor_op(expr):
        def __repr__(self):
            return f"({self.children[0]} ^ {self.children[1]})"
    class and_op(expr):
        def __repr__(self):
            return f"({self.children[0]} & {self.children[1]})"
    class not_op(expr):
        def __repr__(self):
            return f"(~ {self.children[0]})"
    
    class shiftr(expr):
        def __repr__(self):
            return f"({self.children[0]} >> {self.children[1]})"
    class shiftl(expr):
        def __repr__(self):
            return f"({self.children[0]} << {self.children[1]})"
    
    class add(expr):
        def __repr__(self):
            return f"({self.children[0]} + {self.children[1]})"
    class sub(expr):
        def __repr__(self):
            return f"({self.children[0]} - {self.children[1]})"
    
    class mul(expr):
        def __repr__(self):
            return f"({self.children[0]} * {self.children[1]})"
    class div(expr):
        def __repr__(self):
            return f"({self.children[0]} / {self.children[1]})"
    
    class unary_sub(expr):
        def __repr__(self):
            return f"(- {self.children[0]})"

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

    class IDENTIFIER(Leaf):
        def __repr__(self):
            return f"identifer {self.value}"
    
    class INST(Leaf):
        def __repr__(self):
            return self.value

    class STRING(Leaf):
        def __repr__(self):
            return self.value
        def __init__(self,value:str):
            self.value = value[1:-1]
        def eval(self):
            self.value = self.value.replace(r"\n","\n").replace(r"\t","\t").replace(r"\\","\\").replace(r"\"","\"")
            return self.value
    class CHAR(STRING):
        def __repr__(self):
            return self.value

        def eval(self):
            super().eval()
            if len(self.value) != 1:
                raise ValueError("CHAR must be a single character")
            self.value = ord(self.value)
            return self.value

    class DECIMAL(Leaf):
        def __init__(self, value):
            self.value = int(value)
    class BINARY(Leaf):
        def __init__(self, value):
            self.value = int(value,base=2)
    class OCTAL(Leaf):
        def __init__(self, value):
            self.value = int(value,base=8)
    class HEX(Leaf):
        def __init__(self, value):
            self.value = int(value,base=16)


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
            sys.exit(1)

        tree = transformer.transform(parsedTree)

        return tree