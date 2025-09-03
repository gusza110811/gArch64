from instructions import *
from memory import *

class Emulator:
    def __init__(self):
        self.registers = [0,0,0]

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
                print(f"{key:08X}: {value:02X}")
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
    demo = bytes([
        0x00, 0x47,  0x00, 0x00, 0x00, 0x41, # LDAI x41   : ascii hex for A (65)
        0x00, 0x48,  0x00, 0x00, 0x00, 0xFF, # LDAX 255
        0x00, 0x84,  0x00, 0x00, 0x00, 0xFF, # STAR 255
        0x00, 0x80,  0x00, 0x00, 0x00, 0x10, # SYS x10   ; or SYS 16
        ])
    emulator.main(demo)

    emulator.core_dump()