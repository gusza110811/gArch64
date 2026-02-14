import parser, constructor, color
import os, sys
import lark.exceptions

__dir__ = os.path.dirname(__file__)

class Assembler:
    def __init__(self):
        self.parser = parser.Parser()
        self.constructor = constructor.Constructor()

    def main(self, code:str, filename="<main>"):
        codelns = code.split("\n")
        try:
            tree = self.parser.parse(code,filename)
        except lark.exceptions.UnexpectedCharacters as e:
            line = e.line -1 if e.line > 0 else -1
            col = e.column -1 if e.column > 0 else -1
            print(color.fg.MAGENTA + f"unexpected character at line {line} char {col}")
            print(color.RESET + "  "+codelns[line-1])
            print(color.fg.RED + "  "+" "*(col-1)+"^")
            return None

        if tree is None:
            return

        print("\n".join([repr(item) for item in tree.children]))
        try:
            out = self.constructor.main(tree,filename)
        except parser.ParseErr as e:
            print(color.fg.MAGENTA + e.msg)
            print(f"at line {e.line+1} char {e.col}")
            print(color.RESET + "  " + codelns[e.line])
            print(color.fg.RED + "  " + " "*e.col+"^"*(e.colend-e.col))
            print(color.fg.GRAY + e.hint)
            return None

        print("\n")

        print(self.constructor.globals.get_all())
        return out

def test():
    test = open(os.path.join(__dir__,"main.asm")).read()

    assembler = Assembler()
    out = assembler.main(test)
    if out:
        print("Output bytes:", out.hex(" "))
    
        with open("out.bin","wb") as file:
            file.write(out)

if __name__ == "__main__":
    test()