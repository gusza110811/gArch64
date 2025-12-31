import parser, constructor
import os, sys

__dir__ = os.path.dirname(__file__)

class Assembler:
    def __init__(self):
        self.parser = parser.Parser()
        self.constructor = constructor.Constructor()

    def main(self, code:str, filename="<main>"):
        tree = self.parser.parse(code,filename)
        print("\n".join([repr(item) for item in tree.value]))

        self.constructor.main(tree,filename)

        print("\n\n"+"\n".join([repr(item) for item in tree.value]))

if __name__ == "__main__":
    test= open(os.path.join(__dir__,"main.asm")).read()

    assembler = Assembler()
    assembler.main(test)