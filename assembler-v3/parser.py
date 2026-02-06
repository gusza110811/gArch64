from __future__ import annotations
from typing import TYPE_CHECKING
from lark import Lark, Transformer as t
import lark
import os, sys

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
        
        def eval(self, locals:Memory=None):pass

        def __repr__(self):
            return f"<Invalid Node>"

    class Branch(Node):
        def __init__(self, value:list[Transformer.Node]):
            self.children = value
        
        def eval(self, locals:Memory):
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
        
        def eval(self, locals):
            codegens = [child for child in self.children if isinstance(child,Transformer.codegen_block)]
            non_codegens = [child for child in self.children if child not in codegens]

            for child in non_codegens:
                child.eval(locals)
            
            for child in codegens:
                child.eval(locals)

    def transform(self, tree) -> start:
        return super().transform(tree)

    class codegen_block(Branch):
        def __init__(self, value):
            self.name = value[0]
            self.children = value[1:]

        def eval(self, locals):
            self.codegens = [child for child in self.children if isinstance(child,Transformer.codegen)]
            self.non_codegens = [child for child in self.children if child not in self.codegens]

            for child in self.non_codegens:
                child.eval(locals)
    class codegen(Branch):pass

    class code_block(codegen_block):

        def __repr__(self):
            return "code " + repr(self.children[0]) + "{" + "; ".join([repr(value) for value in self.children[1:]]) + "}"

    class data_block(codegen_block):

        def __repr__(self):
            return "data " + repr(self.children[0]) + "{" + ", ".join([repr(value) for value in self.children[1:]]) + "}"

    class instruction(codegen):
        def length(self, blocksize=4):
            "blocksize is in bytes"
            return 2 + (len(self.children) - 1)*blocksize

        def __repr__(self):
            return f"{self.children[0]}({", ".join([repr(value) for value in self.children[1:]])})"

    class text(codegen):
        def __repr__(self):
            return f".ascii {self.children[0]}"
    
    class text_nulterm(codegen):
        def __repr__(self):
            return f".asciiz {self.children[0]}"
    
    class byte(codegen):
        def __repr__(self):
            return f".byte {self.children[0]}"
        def length(self):
            return 1
    class word(codegen):
        def __repr__(self):
            return f".word {self.children[0]}"
        def length(self):
            return 2
    class double(codegen):
        def __repr__(self):
            return f".double {self.children[0]}"
        def length(self):
            return 4
    class quad(codegen):
        def __repr__(self):
            return f".quad {self.children[0]}"
        def length(self):
            return 8

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
        
        def eval(self, locals):
            name = self.name.eval()
            if locals.get_local(name):
                raise SyntaxError(f"{name} already defined in this scope")

            locals.set(name,self.val.eval(locals))
        
    class labeldef(Branch):
        def __repr__(self):
            return f"label {self.children[0]}"
        
        def eval(self, locals):
            return super().eval(locals)

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
        def eval(self, locals):
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
        def init(self):
            self.value = self.value[1:-1]
    class CHAR(STRING):
        def __repr__(self):
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
    
if TYPE_CHECKING:
    from memory import Memory