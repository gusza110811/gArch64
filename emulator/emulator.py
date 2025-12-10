from instructions import *
from memory import *
from device import *
import argparse
import os
import executor
import time
import re
from color import *

class Emulator:
    def __init__(self):
        self.registers = [0,0,0]

        self.opcodes = Opcodes(self)
        self.executor = executor.Executor(self)

        self.cache = Cache()
        self.ram = Ram()
        self.ram.allocate_page(0x00000)
        self.ram.allocate_page(0xFFFF0)

        self.counter = 0
        self.blocksize = 2

        self.carry = False

        self.running = True

        self.time = []

        self.trace = []
        self.do_trace = False
        self.block_recursion = False
        self.recursion_limit = 10000
    
    # Ensure register A is within bounds
    def correct_register(self):
        max_value = (1 << (self.blocksize * 16)) - 1
        new_value = self.registers[0] & max_value
        if new_value != self.registers[0]:
            self.carry = True
            self.registers[0] = new_value
        else:
            self.carry = False

    def main(self, disk:str):

        # Flash Bios
        bios = bytes()
        with open(f"{os.path.dirname(__file__)}/bios.bin","rb") as biosfile:
            bios = biosfile.read()
        
        for idx, value in enumerate(bios):
            self.ram.store(idx+0xFFFF_0000, value) # offset 4294901760

        self.counter = 0xFFFF_0000

        tracing = False
        prev_addr = self.counter

        recursion_table = {}

        # register console
        console = SerialConsole()
        self.ram.register_device(console)

        # register disk controller
        diskio = DiskIO(disk)
        self.ram.register_device(diskio)

        def fetch():
            value = self.ram.load(self.counter)
            self.counter += 1
            return value

        while self.running:
            prev_time = time.perf_counter_ns()

            opcode = fetch()
            opcode = opcode + (fetch() << 8)
            info = self.opcodes.OPCODES[opcode]
            name = info["mnemonic"]
            size = info["size"]

            params = []

            for idx in range(size):
                value = 0
                for idk in range(self.blocksize * 2 ): # blocksize is in words, not bytes
                    value = value >> 8
                    value += fetch() << (self.blocksize * 2 * 8)-8
                params.append(value)
            
            prev_addr = self.counter
            self.correct_register()

            self.executor.execute(name,params)
            self.time.append(time.perf_counter_ns()-prev_time)
            
            if self.do_trace and tracing:
                # counter,
                # opcode value,
                # opcode name,
                # parameters,
                # registers,
                # (relavent cache address, relavent cache value)
                # (relavent ram address, relavent ram value)
                # was a jump done
                cache_revalence = r"LD(A|X|Y)?!R|MOV?!R"
                ram_revalence = r"LD(A|X|Y)R|MOVR"
                jumped = self.counter != prev_addr
                self.trace.append((
                    self.counter,
                    opcode, name,
                    params.copy() + [0]*(2-len(params)),
                    self.registers.copy(),
                    (params[0], self.cache.load(params[0])) if re.match(cache_revalence, name) else (self.registers[1], self.cache.load(self.registers[1])) if (name == "LDV" or name == "STV") else None,
                    (params[0], self.ram.load_bypass_dev(params[0])) if re.match(ram_revalence, name) else (self.registers[1], self.ram.load_bypass_dev(self.registers[1])) if (name == "LDVR" or name == "STVR") else None,
                    jumped
                ))
            if self.do_trace and self.counter == 0: # begin tracing on the true start of the program
                tracing = True
            
            if self.block_recursion:
                if self.counter not in recursion_table:
                    recursion_table[self.counter] = 0
                recursion_table[self.counter] += 1
                if recursion_table[self.counter] > self.recursion_limit:
                    print(f"{color.fg.RED}Recursion blocked: instruction at x{self.counter:X} executed too many times{color.RESET}")
                    break

        return


    def core_dump(self):
        print(f"Stopped at x{self.counter:X}")
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
        self.ram.data = dict(sorted(self.ram.data.items()))
        print("\n<--- RAM DUMP --->")
        for idf,frame in enumerate(self.ram.data.values()):
            frame = dict(sorted(frame.items()))
            for idx, (key, value) in enumerate(frame.items()):
                if not long:
                    char = ascii(chr(value))
                    print(f"{idf:05X}{key:03X}: {value:02X} : {char}{' '*(8-len(char))}{'\n' if (idx % 4) == 3 else ''}",end="")
                else:
                    print(f"{key:016X}: {value:02X}")
            print("\n")
    
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

    parser.add_argument("source", help="path to disk image", default="main.bin", nargs="?")
    parser.add_argument("-d", "--debug", help="print max/mid/min/median execution time, value of registers, cache and ram on halt", action="store_true")
    parser.add_argument("-D", "--trace", help="trace execution and dump to .trace in the current directory", action="store_true")
    parser.add_argument("-g", "--graph", help="shows graph of execution time on halt", action="store_true")
    parser.add_argument("-r", "--block-small-recursion", help="halt execution when a certain address is executed 1,000 times", action="store_true")
    parser.add_argument("-R", "--block-recursion", help="halt execution when a certain address is executed 10,000 times", action="store_true")
    parser.add_argument("--block-large-recursion", help="halt execution when a certain address is executed 1,000,000 times", action="store_true")

    args = parser.parse_args()
    source = args.source

    emulator.do_trace = bool(args.trace)
    emulator.block_recursion = bool(args.block_recursion)
    if bool(args.block_small_recursion):
        emulator.block_recursion = True
        emulator.recursion_limit = 1000
    if bool(args.block_large_recursion):
        emulator.block_recursion = True
        emulator.recursion_limit = 1000000

    try:
        emulator.main(source)
    except KeyboardInterrupt:
        print(color.fg.YELLOW+"INT"+color.RESET)
    
    finally:
        if bool(args.debug):
            def reduce_list(original_list, target_size):
                if target_size >= len(original_list):
                    return original_list
                step = len(original_list) // target_size

                reduced_list = original_list[::step]
                return reduced_list
            emulator.core_dump()
            emulator.time.sort(reverse=True)
            emulator.time = reduce_list(emulator.time,2000)
            with open(".data","w") as data:
                data.writelines([f"{str(num)}\n" for num in emulator.time])
            emulator.time.sort(reverse=True)
            average_time = sum(emulator.time)/len(emulator.time)
            median_time = emulator.time[len(emulator.time)//2]
            max_time = max(emulator.time)
            min_time = min(emulator.time)
            print("\nTime spent executing instruction")
            print(f"{fg.RED}Max :{RESET} {max_time:,.0f}ns")
            print(f"{fg.GREEN}Mid :{RESET} {median_time:,.0f}ns")
            print(f"{fg.BLUE}Min :{RESET} {min_time:,.0f}ns")
            print(f"{fg.GRAY}Mean:{RESET} {average_time:,.0f}ns")
        if bool(args.graph):
            import plot_time
            plot_time.main()
        if bool(args.trace):
            with open(".trace","w") as tracefile:
                for idx, entry in enumerate(emulator.trace):
                    if emulator.trace[idx-1][7]:
                        tracefile.write(f"> ")
                    else:
                        tracefile.write(f"  ")

                    tracefile.write(f"{entry[0]:08X}: [{entry[1]:02X}] {entry[2].ljust(5)} {', '.join([f"{param:10}" for param in entry[3]])}   //   A: {entry[4][0]:8X} , X: {entry[4][1]:8X} , Y: {entry[4][2]:8X}   //")
                    if entry[5]:
                        tracefile.write(f"   *x{entry[5][0]:04X}     = {entry[5][1]:8X}")
                    try:
                        if entry[6]:
                            tracefile.write(f"    x{entry[6][0]:08X} =       {entry[6][1]:2X}")
                    except:
                        print(entry)
                    tracefile.write(f"\n")