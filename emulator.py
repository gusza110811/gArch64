from command import *
from instructions import *
from memory import *

class Emulator:
    def __init__(self):
        self.registers = [0,0,0]

        self.command = Command(self)
        self.opcodes = Opcodes(self,self.command)

        self.cache = Cache()
        self.ram = Ram()

        self.counter = 0
        self.blocksize = 2
    
    def main(self, code:bytes):
        # Flash code to ram
        for idx, value in enumerate(code):
            self.ram.store(idx,value)
        
        def fetch():
            value = self.ram.load(self.counter)
            self.counter += 1
            return value

        while True:
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
            if name == "HALT":
                break

        return

    def core_dump(self):
        print("\n\n<--- REGISTER DUMP --->")
        # dump register
        print(f"A: {self.registers[0]}")
        print(f"X: {self.registers[1]}")
        print(f"Y: {self.registers[2]}")

        self.dump_cache()
        self.dump_ram()

    def dump_ram(self):
        print("<--- RAM DUMP --->")
        for idx, (key,value) in enumerate(self.ram.data.items()):
            print(f"{key:08X}: {value:02X}")

    def dump_cache(self, start: int = 0, end: int = None):
        print("<--- CACHE DUMP --->")
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

                print(f"{i:04X}: x{value:08X}")
                prev_value = value

        if repeat_count > 0:
            print(f"... repeated to {(end-1):04X}")

    pass


if __name__ == "__main__":
    emulator = Emulator()
    demo = bytes([
        0x00, 0x47,  0x00, 0x00, 0x00, 0x41, # LDAI x41   : ascii hex for A (65)
        0x00, 0x48,  0x00, 0x00, 0x00, 0xFF, # LDAX 255
        0x00, 0x84,  0x00, 0x00, 0x00, 0xFF, # STAR 255
        0x00, 0x80,  0x00, 0x00, 0x00, 0x10, # SYS x10   ; or SYS 16
        0x00, 0x00, # HALT
        ])
    emulator.main(demo)

    emulator.core_dump()