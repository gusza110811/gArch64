import argparse
from asm_types import *

class Assembler:
    def __init__(self):
        self.const = {}
        self.mnemonicToClass = {
            # Halt
            "halt": Halt,

            # Arithmetic
            "add": Add,
            "sub": Sub,
            "mul": Mul,
            "div": Div,
            "mod": Mod,

            # Bitwise
            "and": And,
            "or": Or,
            "xor": Xor,
            "not": Not,

            # Control flow
            "jmp": Jmp,
            "jz": Jz,
            "jnz": Jnz,
            "jc": Jc,
            "jnc": Jnc,
            "jeq": Jeq,
            "jne": Jne,

            # Function flow
            "ret": Ret,
            "call": Call,
            "bz": Bz,
            "bnz": Bnz,
            "bc": Bc,
            "bnc": Bnc,
            "be": Be,
            "bne": Bne,

            # Register moves (non-RAM)
            "mov": Mov,

            # Stack
            "push": Push,
            "pop": Pop,
            "pushr": Pushr,
            "popr": Popr,

            # x32 system / interrupts
            "int": Int,
            "sys": Sys,
            "intr": Intr,

            # Extended operations
            "reduce": Reduce,
            "extend": Extend,
        }

        return

    def decode(self,word:str):
        if word.startswith("b"):
            return int(word[1:],base=2)
        elif word.startswith("x"):
            return int(word[1:],base=16)
        elif word.startswith("o"):
            return int(word[1:],base=8)
        elif word.startswith("'"):
            return ord(word[1])
        else:
            return int(word)

    def parse_parameters(self,parameters:str):
        parameters = parameters.split(",")
        result:list[Parameter] = []

        for idx, parameter in parameters:
            prefix = parameter[0]
            if prefix in list("%$@*"):
                parameter = parameter[1:]
            if prefix == "$":
                name = parameter[1].lower()
                if name == "a": result.append(Register(0))
                if name == "x": result.append(Register(1))
                if name == "y": result.append(Register(2))
            elif prefix == "@":
                name = parameter[1].lower()
                if name == "a": result.append(AbstractRegister(0))
                if name == "x": result.append(AbstractRegister(1))
                if name == "y": result.append(AbstractRegister(2))
            else:
                value = self.decode(parameter)
                if prefix == "%":
                    result.append(Immediate(value))
                elif prefix == "*":
                    result.append(CacheAddr(value))
                else:
                    result.append(RamAddr(value))

        return result
    
    def parse_line(self,line:str):
        result = bytes()
        words = line.split()
        # ignore if const definition, label or . command
        if words[0] == "const": return result
        if words[0].endswith(":"): return result
        if words[0].startswith("."): return result

        command = words[0]
        parameters = self.parse_parameters(" ".join(words[1:]))
        result = command

        return

    def parse_lines(self,lines:list[str]):
        result = bytes()
        for idx, line in enumerate(lines):
            result += self.parse_line(line)

        return

    def get_const(self, lines:list[str]):
        lines = lines.splitlines()
        for line in lines:
            words = line.split()
            if words[0] == "const":
                self.const[words[1]] = self.parse_line(words[2:])
            if words[0].endswith(":") and len(words) == 1:
                name = words[0][:-1]
                self.const[name] = 0 # initialize

    def get_labels(self,lines:list[str]):
        lines = lines.splitlines()
        for idx, line in enumerate(lines):
            words = line.split()
            if words[0].endswith(":") and len(words) == 1:
                name = words[0][:-1]
                value = self.parse_lines(lines[:idx])
                self.const[name] = value

    def main(self,source:str):
        lines = source.splitlines()
        output = bytes()

        self.get_const(lines)
        output = self.parse_lines(lines)

        return output

if __name__ == "__main__":
    assembler = Assembler()
    parser = argparse.ArgumentParser(description="gArch64 assembler")

    parser.add_argument("source", help="Path to source asm", default="main.asm", nargs="?")
    parser.add_argument("-o","--output", help="Path to output binary", default="\\/:*?\"<>|")
    parser.add_argument("-O", "--offset", help="offset to labels", default=0)

    args = parser.parse_args()

    source:str = args.source
    dest = args.output

    if dest == "\\/:*?\"<>|":
        dest = ".".join(source.split(".")[:-1]) + ".bin"
    
    with open(source) as sourcefile:
        code = sourcefile.read()

    assembler.main(code)