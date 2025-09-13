import argparse
from asm_types import *
from collections import deque
import sys
import os
import color

class parsingError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class Assembler:
    def __init__(self, name:str=None, offset=0, verbose=False):
        self.offset = offset
        self.verbose = verbose
        self.name = os.path.abspath(name) if name else "main"
        self.const = {}
        self.mnemonicToClass:dict[(str,Command)] = {
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
            "shl":Shl,
            "shr":Shr,
            "shlb":Shlb,
            "shrb":Shrb,

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
            "beq": Beq,
            "bne": Bne,

            # Move
            "mov": Mov,

            # Stack
            "push": Push,
            "pop": Pop,
            "pushr": Pushr,
            "popr": Popr,

            # Variable load/store
            "ldv": Ldv,
            "ldvr": Ldvr,
            "stv": Stv,
            "stvr": Stvr,

            # x32 system / interrupts
            "int": Int,
            "intr": Intr,

            # Extended operations
            "reduce": Reduce,
            "extend": Extend,
        }

        return

    def get_line(self,rawline:str):
        result = rawline.split(";")[0].strip()
        return result

    def decode(self,word:str):
        if word in self.const:
            return self.const[word]
        elif word.startswith("b"):
            try:
                return int(word[1:],base=2)
            except ValueError:
                raise ValueError(f"Can't decode `{word}` as binary")
        elif word.startswith("x"):
            try:
                return int(word[1:],base=16)
            except ValueError:
                raise ValueError(f"Can't decode `{word}` as hexadecimal")
        elif word.startswith("o"):
            try:
                return int(word[1:],base=8)
            except ValueError:
                raise ValueError(f"Can't decode `{word}` as octal")
        elif word.startswith("'"):
            try:
                return ord(word)
            except TypeError:
                raise SyntaxError(f"`'` prefix only accepts one character")
        else:
            try:
                return int(word)
            except ValueError:
                if not word:
                    return 0
                raise ValueError(f"Can't decode {word} as integer number")

    def parse_parameters(self,parameters:str):
        if len(parameters) == 0:
            return []

        parameters = parameters.split(",")
        result:list[Parameter] = []

        for parameter in parameters:
            parameter = parameter.strip()
            prefix = parameter[0]
            if prefix in list("%$@*"):
                parameter = parameter[1:]
            if prefix == "$":
                name = parameter.lower()
                if name == "a": result.append(Register(0))
                elif name == "x": result.append(Register(1))
                elif name == "y": result.append(Register(2))
                else: raise SyntaxError(f"{name} is not a valid register")
            else:
                value = self.decode(parameter)
                if prefix == "%":
                    result.append(Immediate(value))
                elif prefix == "*":
                    result.append(CacheAddr(value))
                else:
                    result.append(RamAddr(value))

        return result

    def parse_special(self,line:str) -> bytes:
        command = line.split()[0].strip().lower()
        line = line.strip()

        def decode_ascii(text:str):
            text:deque[str] = deque(text)
            result = bytes()
            while text:
                char = text.popleft()
                if char != "\\":
                    result += bytes(char,encoding="ascii")
                    continue
                code = text.popleft()
                if code == "n":
                    result += 0x0A.to_bytes(1)
                elif code == "r":
                    result += 0x0D.to_bytes(1)
                elif code == "t":
                    result += 0x09.to_bytes(1)
                elif code == "0":
                    result += 0x00.to_bytes(1)
                elif code == "\\":
                    result += bytes("\\",encoding="ascii")
                else:
                    raise SyntaxError(f"Line {idx+1} '{line}': Invalid escape code '{char+code}'")
            return result

        if command == ".ascii":
            return decode_ascii(line[7:].strip())

        if command == ".literal":
            return bytes([self.decode(word) for word in line[8:].split()])

        if command == ".zero":
            return bytes(int(line[6:].strip()))


        else:
            raise SyntaxError(f"Invalid dot command `{command}`")

    def parse_line(self,line:str) -> bytes:
        result = bytes()
        words = line.split(";")[0].split()
        if not words:
            return bytes()
        # ignore if const definition, label or . command
        if words[0] == "const": return result
        if words[0].endswith(":"): return result
        try:
            if words[0].startswith("."): return self.parse_special(line)
        except SyntaxError as e:
            raise parsingError(f"SyntaxError: {e}")
        except ValueError as e:
            raise parsingError(f"ValueError: {e}")

        try:
            command:Command = self.mnemonicToClass[words[0].lower()]()
        except KeyError:
            raise parsingError(f"SyntaxError: `{words[0]}` is not a valid instruction")
        try:
            parameters = self.parse_parameters(" ".join(words[1:]))
            result = command.get_value(parameters)
        except SyntaxError as e:
            raise parsingError(f"SyntaxError: {e}")
        except ValueError as e:
            raise parsingError(f"ValueError: {e}")

        if self.verbose:
            print(f"`{line.strip()}` => `{result.hex(sep=" ")}`")

        return result

    def parse_lines(self,lines:list[str]):
        result = bytes()
        for idx, line in enumerate(lines):
            try:
                result += self.parse_line(line)
            except parsingError as e:
                def find_first_non_whitespace(s):
                    for i, char in enumerate(s):
                        if not char.isspace():
                            return i
                    return -1  # Return -1 if no non-whitespace character is found
                print(color.fg.BRIGHT_MAGENTA+f"In file `{self.name}` at line {idx+1}:"+color.RESET)
                print(color.fg.BRIGHT_RED+f"    {line}")
                print(color.fg.RED+f"    {" "*find_first_non_whitespace(line)}{"^"*len(line.strip())}")
                print(color.fg.BRIGHT_MAGENTA+f"{str(e)}"+color.RESET)
                sys.exit(1)

        return result

    def get_const(self, lines:list[str]):
        for line in lines:
            line = self.get_line(line)
            if not line: continue
            words = line.split()
            if words[0] == "const":
                self.const[words[1]] = self.decode(" ".join(words[2:]))
            if words[0].endswith(":") and len(words) == 1:
                name = words[0][:-1]
                self.const[name] = 0 # initialize

    def get_labels(self,lines:list[str]):
        for idx, line in enumerate(lines):
            line = self.get_line(line)
            if not line: continue
            words = line.split()
            if words[0].endswith(":") and len(words) == 1:
                name = words[0][:-1]
                value = len(self.parse_lines(lines[:idx]))+self.offset
                self.const[name] = value

    def main(self,source:str):

        lines = source.splitlines()
        output = bytes()

        self.get_const(lines)
        self.get_labels(lines)
        output = self.parse_lines(lines)

        return output

def is_ascii_printable_byte(byte_value):
    """Checks if an integer byte value is an ASCII printable character."""
    return 32 <= byte_value <= 126

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gArch64 assembler")

    parser.add_argument("source", help="path to source asm", default="main.asm", nargs="?")
    parser.add_argument("-o","--output", help="path to output binary", default="\\/:*?\"<>|")
    parser.add_argument("-O", "--offset", help="offset to labels", default=0, type=int)
    parser.add_argument("-v", "--verbose", help="send assembling info", action="store_true")

    args = parser.parse_args()

    source:str = args.source
    dest = args.output
    assembler = Assembler(source, int(args.offset), args.verbose)

    if dest == "\\/:*?\"<>|":
        dest = ".".join(source.split(".")[:-1]) + ".bin"
    
    with open(source) as sourcefile:
        code = sourcefile.read()

    output = assembler.main(code)
    constants = assembler.const
    print("\nConstants used:")
    maxlen = len(str(len(constants)))
    for idx, (name,value) in enumerate(constants.items()):
        if is_ascii_printable_byte(value):
            print(f"{str(idx).zfill(maxlen)}: {name} = {value} (`{chr(value)}` or {value:02X})")
        else:
            print(f"{str(idx).zfill(maxlen)}: {name} = {value} ({value:02X})")
    print("<","="*len(constants)*2,">",sep="=")

    with open(dest,"wb") as destfile:
        destfile.write(output)
