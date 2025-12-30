from instructions import *
from memory import *
from device import *
import argparse
import os
import executor
import time
import re
from color import *

# during development, keep this the next unstable or stable version to be released
VERSION = "snapshot7"

class executionError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class Emulator:
    def __init__(self):
        self.registers = [0,0,0]

        self.opcodes = Opcodes(self)
        self.executor = executor.Executor(self)

        self.ram = Ram()
        self.ram.allocate_page(0xFFFF0)

        self.counter = 0
        self.begininst = 0
        self.blocksize = 2

        self.carry = False
        self.zero = False

        self.running = True
        self.halt_type = None
        self.crash_on_unknown = True

        self.time = []

        self.trace = []
        self.do_trace = False
        self.block_recursion = False
        self.recursion_limit = 10000
    
    # Ensure register A is within bounds
    def correct_register(self):
        max_value = (1 << (self.blocksize * 16)) - 1
        new_value = self.registers[0] & max_value
        self.carry = True
        if new_value != self.registers[0]:
            self.registers[0] = new_value
        else:
            self.carry = False
        
        if self.registers[0] == 0:
            self.zero = True
        else:
            self.zero = False
    
    def compare(self, val1:int, val2:int):
        if val1 >= val2:
            self.carry = False
            self.zero = False
        if val1 == val2:
            self.carry = False
            self.zero = True
        if val1 < val2:
            self.carry = True
            self.zero = False

        return

    def main(self, disk:str, stdin):

        # Flash Bios
        bios = bytes()
        try:
            with open(f"{os.path.dirname(__file__)}/bios.bin","rb") as biosfile:
                bios = biosfile.read()
        except FileNotFoundError:
            raise executionError("BIOS binary not found")

        for idx, value in enumerate(bios):
            self.ram.store(idx+0xFFFF_0000, value) # offset 4294901760

        self.counter = 0xFFFF_0000

        # Set to true if debugging the BIOS
        tracing = False

        recursion_table = {}

        # register console
        console = SerialConsole(stdin)
        self.ram.register_device(console)

        # register disk controller
        try:
            diskio = DiskIO(disk)
        except FileNotFoundError:
            raise executionError(f"Disk image \"{disk}\" not found")
        self.ram.register_device(diskio)

        def fetch():
            value = self.ram.load(self.counter)
            self.counter += 1
            return value

        def int_fault(id):
            target = self.ram.find_int(id)
            if target:
                self.ram.push_double(self.counter)
                self.counter = target
            elif target != 0x102:
                int_fault(0x100)

        while self.running:
            prev_time = time.perf_counter_ns()

            self.begininst = self.counter
            opcode = fetch()
            opcode = opcode + (fetch() << 8)
            try:
                info = self.opcodes.OPCODES[opcode]
            except KeyError:
                int_fault(0x101)

            name:str = info["mnemonic"]
            size = info["size"]

            params = []

            for idx in range(size):
                value = 0
                for idk in range(self.blocksize * 2 ): # blocksize is in words, not bytes
                    value = value >> 8
                    value += fetch() << (self.blocksize * 2 * 8)-8
                params.append(value)
            
            prev_addr = self.counter

            # convert first parameter to signed for certain instructions
            if (name.startswith("J") or name.startswith("B") or (name == "CALL")) and not name.endswith("V"):
                param = params[0]
                sign_bit = 1 << (self.blocksize * 16 - 1)
                if param & sign_bit:
                    param = param - (1 << (self.blocksize * 16))
                params[0] = param
            if name == "INTR":
                param = params[1]
                sign_bit = 1 << (self.blocksize * 16 - 1)
                if param & sign_bit:
                    param = param - (1 << (self.blocksize * 16))
                params[1] = param

            try:
                self.executor.execute(name,params)
            except pageFault:
                int_fault(0x102)
            except ivtOverflow:
                int_fault(0x103)
            except undefinedInt:
                int_fault(0x100)

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
                ram_revalence = r"(^(?:ST|LD)[AXY]|^MOV)?[WDQ]"
                jumped = self.counter != prev_addr
                try:
                    rammed = (params[0], self.ram.load_bypass_dev(params[0])) if re.match(ram_revalence, name) else (self.registers[1], self.ram.load_bypass_dev(self.registers[1])) if (name.startswith("LDV") or name.startswith("STV")) else None
                except pageFault:
                    rammed = (params[0], 0) if re.match(ram_revalence, name) else (self.registers[1], self.ram.load_bypass_dev(self.registers[1])) if (name.startswith("LDV") or name.startswith("STV")) else None
                try:
                    self.trace.append((
                        self.begininst,
                        opcode, name,
                        params.copy() + [0]*(2-len(params)),
                        self.registers.copy(),
                        rammed,
                        jumped
                    ))
                except IndexError:
                    print(f"{opcode:X} {name} {params} {prev_addr:X}")
                    raise IndexError
            if self.do_trace and self.counter == 0: # begin tracing on the true start of the program
                tracing = True
            
            if self.block_recursion:
                if self.counter not in recursion_table:
                    recursion_table[self.counter] = 0
                recursion_table[self.counter] += 1
                if recursion_table[self.counter] > self.recursion_limit:
                    raise executionError(f"Recursion/Infinite loop blocked: instruction at x{self.counter:X} executed too many times")

        return


    def core_dump(self):
        print(f"Stopped at x{self.counter:X}")

        if self.dump_state() == -1:
            return

        self.dump_registers()

        if self.blocksize == 2:
            self.dump_ram()
        else:
            self.dump_ram(True)
    
    def dump_registers(self):
        print("\n<--- REGISTER DUMP --->")
        # dump register
        print(f"A: {self.registers[0]:03}  (x{self.registers[0]:02X})")
        print(f"X: {self.registers[1]:03}  (x{self.registers[1]:02X})")
        print(f"Y: {self.registers[2]:03}  (x{self.registers[2]:02X})")

    def dump_ram(self, long=False):
        pages = dict(sorted(self.ram.page_to_frame.items()))
        del pages[0xFE000]
        print("\n<--- RAM DUMP --->")
        for page, frame in pages.items():
            frame = dict(sorted(self.ram.get_frame(frame).items()))

            for idx, (key, value) in enumerate(frame.items()):
                if not long:
                    char = ascii(chr(value))
                    print(f"{page:05X}{key:03X}: {value:02X} : {char}{' '*(8-len(char))}{'\n' if (idx % 4) == 3 else ''}",end="")
                else:
                    print(f"{key:016X}: {value:02X}")
            print("\n")
    
    def dump_state(self):
        print("\n<--- STATE DUMP --->")

        if emulator.halt_type == None:
            print("Interrupted")
        elif emulator.halt_type == 1:
            print("Halted via 0xFF (HALT)")
        elif emulator.halt_type == 2:
            print("Halted via 0x00 (HALTZ)")
        elif emulator.halt_type == -1:
            print("Internal emulation error")
            return -1
        
        print("")

        print(f"Stack Top     : {emulator.ram.stack_start:8X}")
        print(f"Stack Position: {emulator.ram.stack_pos:8X}")
        print(f"IVT zero      : {emulator.ram.int_start:8X}")

    pass

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":

    emulator = Emulator()

    parser = argparse.ArgumentParser(description="gArch64 emulator")

    parser.add_argument("source", help="path to disk image", default="main.bin", nargs="?")
    parser.add_argument("-v", "--verbose", help="print extra info before and after execution", action="store_true")
    parser.add_argument("-t", "--time", help="print max/mid/min/median execution time on halt", action="store_true")
    parser.add_argument("-d", "--trace", help="trace execution and dump to .trace in the current directory (not recommended without --stdin)", action="store_true")
    parser.add_argument("-m", "--dump", help="dump memory to console", action="store_true")
    parser.add_argument("-M", "--dump-file", help="dump memory to .dump in the current directory", action="store_true")
    parser.add_argument("-r", "--dump-raw", help="dump first contiguous pages in ram as a raw binary file", action="store_true")
    parser.add_argument("-g", "--graph", help="shows graph of execution time on halt", action="store_true")
    parser.add_argument("-s", "--stdin", help="the stdin exposed to the system, prompt for one if empty. use \\ as newline", default=None, const="", action="store", nargs="?")
    
    parser.add_argument("--block-small-recursion", help="halt execution when a certain address is executed 1,000 times", action="store_true")
    parser.add_argument("-R", "--block-recursion", help="halt execution when a certain address is executed 10,000 times", action="store_true")
    parser.add_argument("--block-large-recursion", help="halt execution when a certain address is executed 1,000,000 times", action="store_true")
    args = parser.parse_args()
    source = args.source
    
    eprint(color.fg.GRAY,end="")
    stdin = args.stdin

    dumpr = bool(args.dump_raw)
    verbose = bool(args.verbose)
    if verbose:
        eprint(f"v.{VERSION}")
        eprint(f"python v.{".".join([str(item) for item in sys.version_info[:3]])}")
        eprint(f"{os.cpu_count()} logical processors available")

    if stdin == "":
        stdin = input("stdin> ")
    if stdin:
        stdin = (stdin+"\\").replace("\\", "\n")
    
    if verbose or stdin:
        eprint("")
    print(color.RESET,end="")

    emulator.do_trace = bool(args.trace)
    emulator.block_recursion = bool(args.block_recursion)
    if bool(args.block_small_recursion):
        emulator.block_recursion = True
        emulator.recursion_limit = 1000
    if bool(args.block_large_recursion):
        emulator.block_recursion = True
        emulator.recursion_limit = 1000000
    
    if (bool(args.block_recursion) + bool(args.block_small_recursion) + bool(args.block_large_recursion)) > 1:
        sys.exit("Cannot use multiple recursion block flags at once")

    try:
        emulator.main(source,stdin)
    except KeyboardInterrupt:
        print(color.fg.YELLOW+"INT"+color.RESET)
    except executionError as E:
        eprint(color.fg.RED + str(E) + color.RESET)
        emulator.halt_type = -1

    finally:
        if verbose:
            eprint(color.fg.GRAY)

        if bool(args.dump):
            emulator.core_dump()
        if bool(args.dump_file):
            if verbose:
                eprint("Writing dump log")
            oldstdout = sys.stdout
            sys.stdout = open(".dump","w")
            emulator.core_dump()
            sys.stdout = oldstdout

        if bool(args.time):
            def reduce_list(original_list, target_size):
                if target_size >= len(original_list):
                    return original_list
                step = len(original_list) // target_size

                reduced_list = original_list[::step]
                return reduced_list
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
            if verbose:
                eprint("Graphing")
            import plot_time
            plot_time.main()
        if bool(args.trace):
            if verbose:
                eprint("Writing traceback")
            with open(".trace","w") as tracefile:
                for idx, entry in enumerate(emulator.trace):
                    if emulator.trace[idx-1][6]:
                        tracefile.write(f"> ")
                    else:
                        tracefile.write(f"  ")

                    tracefile.write(f"{entry[0]:08X}: [{entry[1]:02X}] {entry[2].ljust(5)} {', '.join([f"{param:8X}" for param in entry[3]])}   //   A: {entry[4][0]:8X} , X: {entry[4][1]:8X} , Y: {entry[4][2]:8X}   //")
                    if entry[5]:
                        tracefile.write(f"    x{entry[5][0]:08X} =       {entry[5][1]:2X}")
                    tracefile.write(f"\n")
        if dumpr:
            if verbose:
                eprint("Writing raw dump")
            def get_contiguous_pages():
                pages = 0
                for p in range(len(emulator.ram.page_to_frame)):
                    try:
                        emulator.ram.page_to_frame[p]
                        pages += 1
                    except KeyError:
                        break
                return pages
            with open(".ram","wb") as rawdump:
                buffer = bytearray()
                for idx in range(get_contiguous_pages()*0x1000):
                    buffer.append(emulator.ram.load(idx))
                rawdump.write(buffer)

        if verbose:
            eprint(color.RESET,end="")