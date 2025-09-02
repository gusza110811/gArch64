from opcodes import *
from memory import *

class Emulator:
    def __init__(self):
        self.opcodes = Opcodes()
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
            
            print(f"{name}", *params)
            if name == "HALT":
                break

        return


if __name__ == "__main__":
    emulator = Emulator()
    demo = bytes([
        0x00, 0x47,  0x00, 0x00, 0xA4, 0x55, # LDAI 42069   0xA455
        0x00, 0x00 # HALT
        ])
    emulator.main(demo)