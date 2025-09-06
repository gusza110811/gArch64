from instructions import *
from memory import *
from device import *
import argparse
import os

class Emulator:
    def __init__(self):
        self.registers = [0,0,0]

        self.opcodes = Opcodes(self)

        self.cache = Cache()
        self.ram = Ram()

        self.counter = 0
        self.blocksize = 2

        self.carry = False

        self.running = True
    
    def correct_register(self):
        newvalue = self.registers[0] % 2^(16*self.blocksize)
        if newvalue == self.registers[0]:
            self.carry = False
        else:
            self.carry = True

    def main(self, code:bytes):
        # Flash code to ram
        for idx, value in enumerate(code):
            self.ram.store(idx,value)
        
        # Flash Bios
        bios = bytes()
        with open(f"{os.path.dirname(__file__)}/bios.bin","rb") as biosfile:
            bios = biosfile.read()
        
        for idx, value in enumerate(bios):
            self.ram.store(idx+0xFFFF_0000, value) # offset 4294901760
        
        self.counter = 0xFFFF_0000

        # register console
        console = SerialConsole()
        self.ram.register_device(console)

        def fetch():
            value = self.ram.load(self.counter)
            self.counter += 1
            return value

        while self.running:
            opcode = fetch()
            opcode = (opcode << 8) + fetch()
            info = self.opcodes.OPCODES[opcode]
            name = info["mnemonic"]
            size = info["size"]

            params = []

            for idx in range(size):
                value = 0
                for idk in range(self.blocksize * 2 ): # blocksize is in words, not bytes
                    value = value << 8
                    value += fetch()
                params.append(value)

            self.opcodes.execute(name,params)
        return

    def core_dump(self):
        print("\n\n<--- REGISTER DUMP --->")
        # dump register
        print(f"A: {self.registers[0]:03}  (x{self.registers[0]:02X})")
        print(f"X: {self.registers[1]:03}  (x{self.registers[1]:02X})")
        print(f"Y: {self.registers[2]:03}  (x{self.registers[2]:02X})")

        if self.blocksize == 2:
            self.dump_cache()
            self.dump_ram()
        else:
            self.dump_cache(True)
            self.dump_ram(True)

    def dump_ram(self, long=False):
        print("\n<--- RAM DUMP --->")
        prevkey = 0
        for idx, (key,value) in enumerate(self.ram.data.items()):
            if not long:
                print(f"{key:08X}: {value:02X}   : {chr(value)}")
            else:
                print(f"{key:016X}: {value:02X}")
    
    def dump_cache(self, long=False, start: int = 0, end: int = None):
        print("\n<--- CACHE DUMP --->")
        mem = self.cache.data
        if end is None:
            end = len(mem)

        prev_value = None
        repeat_count = 0
        printed = False

        for i in range(start, end):
            value = mem[i]

            if value == prev_value:
                repeat_count += 1
                printed = False
            else:
                if repeat_count > 0:
                    if not printed:
                        if repeat_count > 1:
                            print(f"... {repeat_count} times")
                        else:
                            print("... repeated")
                        printed = True
                    repeat_count = 0
                if not long:
                    print(f"{i:04X}: x{value:08X}")
                else:
                    print(f"{i:04X}: x{value:016X}")
                prev_value = value

        if repeat_count > 0:
            print(f"... repeated to {(end-1):04X}")

    pass


if __name__ == "__main__":
    emulator = Emulator()

    parser = argparse.ArgumentParser(description="gArch64 emulator")

    parser.add_argument("source", help="path to source binary", default="main.bin", nargs="?")
    parser.add_argument("-v", "--verbose", help="dump Memory on halt", action="store_true")

    args = parser.parse_args()
    source = args.source

    with open(source,'rb') as sourcefile:
        code = sourcefile.read()

    try:
        emulator.main(code)
    except KeyboardInterrupt:
        print("INT")
    
    finally:
        if bool(args.verbose):
            emulator.core_dump()