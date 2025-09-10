import os
import math
import argparse
import sys
from collections import deque

active_modules = []

class assembler:
    def __init__(self, offset=0):
        self.offset = offset
        self.length = 2
        self.constants:dict[str,bytes] = {}
        self.aliases:dict[str,bytes] = {}
        self.output = b""
        self.code:list[str]
        self.mnemonicToOP = {
        "halt":0x00,
        # Load and store
        "lda":0x10,
        "ldx":0x11,
        "ldy":0x12,
        "sta":0x13,
        "stx":0x14,
        "sty":0x15,
        "mov":0x16,
        "ldv":0x17,
        "stv":0x18,

        # Arithmetic
        "add":0x20,
        "sub":0x21,
        "mul":0x22,
        "div":0x23,
        "mod":0x28,

        # Bitwise logic
        "and":0x24,
        "or" :0x25,
        "xor":0x26,
        "not":0x27,

        # Control flow
        "jmp":0x30,
        "jz" :0x31,
        "jnz":0x32,
        "jc" :0x33,
        "jnc":0x34,
        "jeq":0x35,
        "jne":0x36,

        # Function flow
        "ret" :0x37,
        "call":0x38,
        "bz"  :0x39,
        "bnz" :0x3A,
        "bc"  :0x3B,
        "bnc" :0x3C,
        "be"  :0x3D,
        "bne" :0x3E,

        # Load Immediate
        "ldai":0x47,
        "ldxi":0x48,
        "ldyi":0x49,

        # Register move
        "mvax":0x50,
        "mvay":0x51,
        "mvxy":0x52,
        "mvxa":0x52,
        "mvyx":0x54,
        "mvya":0x55,

        # Stack
        "pusha":0x60,
        "popa" :0x61,
        "pushx":0x62,
        "popx" :0x63,
        "pushy":0x64,
        "popy" :0x65,
        "pushr":0x66,
        "popr":0x67,

        # x32
        "int":0x80,
        "sys":0x80,

        "ldar":0x81,
        "ldxr":0x82,
        "ldyr":0x83,

        "star":0x84,
        "stxr":0x85,
        "styr":0x86,

        "ldvr":0x87,
        "stvr":0x88,
        "movr":0x89,

        "intr":0x90,

        "reduce":0xA0,
        "extend":0xA1,

        }
    
    def labels(self,name):
        # Prelabel
        for idx,line in enumerate(code):
            line = line.strip()
            self.decode_helpers(line,idx)
            if line.lower().startswith("label"):
                words = line.split()[1:]
                self.constants[words[0]] = bytes(self.length*2)
        length = 0
        # Label and stuff
        for idx,line in enumerate(code):
            line = line.strip()

            if line.lower().startswith("label"):
                words = line.split()[1:]
                value = (length+self.offset).to_bytes(self.length*2)
                self.constants[words[0]] = value
            for word in line.split():
                if self.decode_helpers(line,idx):
                    code[idx]=""
                    continue
                if line.startswith("."):
                    length += len(self.decode_literal(line,idx))
                    break
                if word ==  ";":
                    break
                try:
                    length += len(self.decode_value(word,idx,line))
                except ValueError as e:
                    print(f"An Error in {name}:")
                    print(f"    {e}")
                    sys.exit()

    def main(self, code:list[str],modulename="main"):
        self.code = code

        self.labels(modulename)

        # Main
        for idx,line in enumerate(code):

            line = line.strip()
            
            if self.decode_helpers(line,idx):
                continue

            if line.startswith("."):
                self.output += self.decode_literal(line,idx)
                continue

            # Word decoder
            for word in line.split():
                try:
                    result = self.decode_value(word,idx,line)
                except ValueError as e:
                    print(f"An Error in {modulename}:")
                    print(f"    {e}")
                    sys.exit()
                if result:
                    self.output += result
                else:
                    break
        return self.output, self.constants

    def decode_literal(self, line:str, idx:int):
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

        global active_modules
        if line.lower().startswith(".ascii"):
            return decode_ascii(line[7:])
        if line.lower().startswith(".insert"):
            name = line[8:]
            code = []
            with open(f"{name}.asm") as modulefile:
                code = modulefile.readlines()
            return self.main(code,modulename=name)[0]
        if line.lower().startswith(".blank"):
            return bytes(int(line[7:].strip()))
        if line.lower().startswith(".short"):
            self.length = 1
        if line.lower().startswith(".long"):
            self.length = 2
        if line.lower().startswith(".extended"):
            self.length = 4

        return bytes()

    def decode_helpers(self, line:str,idx):
        if line.lower().startswith("const"):
            words = line.split()[1:]
            value:bytes = self.decode_value(words[1],idx,line)
            self.constants[words[0]] = value
            return True
        if line.lower().startswith("label"):
            return True
        if line.lower().startswith(";"):
            return True
        
        return False

    def decode_value(self, word:str,idx=0,line=""):
        if word.lower() in list(self.mnemonicToOP.keys()):
            return self.mnemonicToOP[word.lower()].to_bytes(self.length)
        elif word in list(self.constants.keys()):
            return self.constants[word]
        elif word in list(self.aliases.keys()):
            return self.aliases[word]
        elif word[0] == "'":
            return ord(word[1]).to_bytes(self.length*2)
        elif word[0] == '"':
            return word[1:].encode()
        elif word[0] == "X":
            word.replace("_","")
            try:
                return int(word[1:],base=16).to_bytes(math.ceil(len(word[1:])/2))
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': invalid hex '{word}'")
        elif word[0] == "B":
            word.replace("_","")
            try:
                return int(word[1:],base=2).to_bytes(len(word[1:]))
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': invalid binary '{word}'")
        elif word[0] == "x":
            word.replace("_","")
            try:
                return int(word[1:],base=16).to_bytes(self.length*2)
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': invalid hex '{word}'")
        elif word[0] == "b":
            word.replace("_","")
            try:
                return int(word[1:],base=2).to_bytes(self.length)
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': invalid binary '{word}'")
        elif word[0] == ";":
            return False
        else:
            try:
                return int(word).to_bytes(self.length*2)
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': can't decode `{word}`!")

def is_ascii_printable_byte(byte_value):
    """Checks if an integer byte value is an ASCII printable character."""
    return 32 <= byte_value <= 126

if __name__ == "__main__":
    source = ""
    code:str
    dest = ""
    parser = argparse.ArgumentParser(description="gArch64 assembler")

    parser.add_argument("source", help="Path to source asm", default="main.asm", nargs="?")
    parser.add_argument("-o","--output", help="Path to output binary", default="\\/:*?\"<>|")
    parser.add_argument("-O", "--offset", help="offset to labels", default=0)

    args = parser.parse_args()

    print("! WARNING: This is an older assembler which is deprecated, not every instruction is included. please do not use it in the future")

    source:str = args.source
    dest = args.output

    if dest == "\\/:*?\"<>|":
        dest = ".".join(source.split(".")[:-1]) + ".bin"

    main = assembler(int(args.offset))

    with open(source) as sourcefile:
        code = sourcefile.readlines()

    result,constants = main.main(code,source)

    print("\nConstants used:")
    maxlen = len(str(len(constants)))
    for idx, (name,value) in enumerate(constants.items()):
        if is_ascii_printable_byte(int.from_bytes(value)):
            print(f"{str(idx).zfill(maxlen)}: {name} = {int.from_bytes(value)} (`{value.decode("ascii")}` or {int.from_bytes(value):02X})")
        else:
            print(f"{str(idx).zfill(maxlen)}: {name} = {int.from_bytes(value)} ({int.from_bytes(value):02X})")
    print("<","="*len(constants)*2,">",sep="=")
    with open(dest, "wb") as destfile:
        destfile.write(result)