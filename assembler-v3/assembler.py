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

        if tree is None:
            return

        out = self.constructor.main(tree,filename)
        print("\n")

        for space in self.constructor.locals:
            print(space.get_all())
        return out

def test():
    test = open(os.path.join(__dir__,"small_test.asm")).read()

    assembler = Assembler()
    out = assembler.main(test)
    if out is not None:
        print("Output bytes:", out.hex(" ", 2))

if __name__ == "__main__":
    test()