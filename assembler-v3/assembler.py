from lark import Lark
from nodes import Transformer
import os

__dir__ = os.path.dirname(__file__)

class Assembler:
    def __init__(self):
        self.grammar = open(os.path.join(__dir__,"grammar.lark")).read()
        self.parser = Lark(self.grammar)
        self.transformer = Transformer()

    def main(self, code:str, filename="<main>"):
        transformer = self.transformer
        parser = self.parser

        parsedTree = parser.parse(code)

        tree = transformer.transform(parsedTree)

        print("\n".join([repr(item) for item in tree.value]))

if __name__ == "__main__":
    test= open(os.path.join(__dir__,"main.asm")).read()

    assembler = Assembler()
    assembler.main(test)