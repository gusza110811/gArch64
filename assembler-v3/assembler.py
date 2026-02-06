import parser, constructor
import os, sys

__dir__ = os.path.dirname(__file__)

class Assembler:
    def __init__(self):
        self.parser = parser.Parser()
        self.constructor = constructor.Constructor()

    def main(self, code:str, filename="<main>"):
        tree = self.parser.parse(code,filename)
        print("\n".join([repr(item) for item in tree.children]))

        out = self.constructor.main(tree,filename)
        print("\n")

        for space in self.constructor.locals:
            print(space.get_all())
        
        print(self.constructor.globals.pc)

        print(out)

def test():
    test = open(os.path.join(__dir__,"main.asm")).read()

    assembler = Assembler()
    assembler.main(test)

if __name__ == "__main__":
    test()