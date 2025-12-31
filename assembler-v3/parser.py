from __future__ import annotations
from lark import Lark, Transformer as t
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
        def __init__(self, value:Transformer.Node):
            self.value = value
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.value})"

    class start(Node):
        def __repr__(self):
            return " ".join([repr(value) for value in self.value])

    def transform(self, tree) -> start:
        return super().transform(tree)

    class code_block(Node):
        def length(self):
            return sum([item.length() for item in self.value if isinstance(item,Transformer.instruction)])

        def __repr__(self):
            return repr(self.value[0]) + "{" + "; ".join([repr(value) for value in self.value[1:]]) + "}"

    class data_block(Node):
        def length(self):
            return sum([item.length() for item in self.value if isinstance(item,Transformer.instruction)])

        def __repr__(self):
            return repr(self.value[0]) + "{" + ", ".join([repr(value) for value in self.value[1:]]) + "}"

    class instruction(Node):
        def length(self, blocksize=4):
            "blocksize is in bytes"
            return 2 + (len(self.value) - 1)*blocksize

        def __repr__(self):
            return f"{self.value[0]}({", ".join([repr(value) for value in self.value[1:]])})"

    class register(Node):
        def __init__(self, value):
            value[0] = value[0].lower()
            super().__init__(value)
        def __repr__(self):
            return f"register {self.value[0]}"
    class immediate(Node):
        def __repr__(self):
            return f"immediate {self.value[0]}"
    class direct_addr(Node):
        def __repr__(self):
            return f"deref {self.value[0]}"
    class indirect_addr(Node):
        def __repr__(self):
            return f"deref indirect"

    class constantdef(Node):
        def __repr__(self):
            return f"{self.value[0]} = {self.value[1]}"
        
    class labeldef(Node):
        def __repr__(self):
            return f"label {self.value[0]}"
    
    class text(Node):
        def __repr__(self):
            return f".ascii {self.value[0]}"
    
    class text_nulterm(Node):
        def __repr__(self):
            return f".asciiz {self.value[0]}"
    
    class byte(Node):
        def __repr__(self):
            return f".byte {self.value[0]}"
        def length(self):
            return 1
    class word(Node):
        def __repr__(self):
            return f".word {self.value[0]}"
        def length(self):
            return 2
    class double(Node):
        def __repr__(self):
            return f".double {self.value[0]}"
        def length(self):
            return 4
    class quad(Node):
        def __repr__(self):
            return f".quad {self.value[0]}"
        def length(self):
            return 8

    class or_op(Node):
        def __repr__(self):
            return f"({self.value[0]} | {self.value[1]})"
    class xor_op(Node):
        def __repr__(self):
            return f"({self.value[0]} ^ {self.value[1]})"
    class and_op(Node):
        def __repr__(self):
            return f"({self.value[0]} & {self.value[1]})"
    class not_op(Node):
        def __repr__(self):
            return f"(~ {self.value[0]})"
    
    class shiftr(Node):
        def __repr__(self):
            return f"({self.value[0]} >> {self.value[1]})"
    class shiftl(Node):
        def __repr__(self):
            return f"({self.value[0]} << {self.value[1]})"
    
    class add(Node):
        def __repr__(self):
            return f"({self.value[0]} + {self.value[1]})"
    class sub(Node):
        def __repr__(self):
            return f"({self.value[0]} - {self.value[1]})"
    
    class mul(Node):
        def __repr__(self):
            return f"({self.value[0]} * {self.value[1]})"
    class div(Node):
        def __repr__(self):
            return f"({self.value[0]} / {self.value[1]})"
    
    class unary_sub(Node):
        def __repr__(self):
            return f"(- {self.value[0]})"

    class literal(Node):
        def __repr__(self):
            return f"lit {self.value[0]}"
    
    class symbol(Node):
        def __repr__(self):
            return f"symbol {self.value[0]}"

    class IDENTIFIER(Node):
        def __repr__(self):
            return f"identifer {self.value}"
    
    class Terminal:
        def __init__(self,value:str):
            self.value = value
    
    class INST(Terminal):
        def __init__(self, value):
            super().__init__(value.lower())
        def __repr__(self):
            return self.value

    class STRING(Terminal):
        def __repr__(self):
            return self.value
        def init(self):
            self.value = self.value
    class CHAR(STRING):
        def __repr__(self):
            return self.value

    class DECIMAL(Terminal):
        def __repr__(self):
            return f"{self.value}"
    class BINARY(Terminal):
        def __repr__(self):
            return f"0b{self.value}"
    class OCTAL(Terminal):
        def __repr__(self):
            return f"0o{self.value}"
    class HEX(Terminal):
        def __init__(self, value):
            value = value.lower()
            super().__init__(value)

        def __repr__(self):
            return f"0x{self.value}"


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