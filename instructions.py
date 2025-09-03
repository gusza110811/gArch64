from typing import Literal, TYPE_CHECKING
import __future__

class Opcodes:
    def __init__(self, emulator:"em.Emulator"):
        self.emulator = emulator
        self.sysrq = Sys_requests(self.emulator)
        self.OPCODES:dict[(str,dict[Literal["mnemonic","opcode","size","operands","desc"]])] = {}
        self.definitions()
    
    def execute(self, instruction:str, params:list[int]):
        emulator = self.emulator
        ram = emulator.ram
        cache = emulator.cache
        registers = emulator.registers

        if instruction == "LDAI": registers[0] = params[0]
        elif instruction == "LDXI": registers[1] = params[0]
        elif instruction == "LDYI": registers[2] = params[0]

        elif instruction == "SYS": self.sysrq.execute_sys(params[0])
        elif instruction == "STAR": ram.store(params[0],registers[0])
        elif instruction == "STXR": ram.store(params[1],registers[1])
        elif instruction == "STYR": ram.store(params[2],registers[2])

    # Helper function to insert opcodes into the list
    def define(self,op, code, size, operands, desc):
        self.OPCODES[code] = {
            'mnemonic': op,
            'opcode': code,
            'size': size, # only include parameters, by blocks
            'operands': operands,
            'desc': desc
        }

    def definitions(self):
        # --- System ---
        self.define('HALT', 0x00, 0, [], 'Stop execution')

        # --- Register Loads ---
        self.define('LDA', 0x10, 1, ['addr'], 'Load from address into A')
        self.define('LDX', 0x11, 1, ['addr'], 'Load from address into X')
        self.define('LDY', 0x12, 1, ['addr'], 'Load from address into Y')

        # --- Register Stores ---
        self.define('STA', 0x13, 1, ['addr'], 'Store A into address')
        self.define('STX', 0x14, 1, ['addr'], 'Store X into address')
        self.define('STY', 0x15, 1, ['addr'], 'Store Y into address')

        # --- Cache to Cache ---
        self.define('MOV', 0x16, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst')

        # --- Variable Load/store ---
        self.define('LDV', 0x17, 0, [], 'Load value from cache into register A, using X as address')
        self.define('STV', 0x18, 0, [], 'Load value from cache into register A, using X as address')

        # --- Arithmetic ---
        self.define('ADD', 0x20, 0, [], 'A = X + Y')
        self.define('SUB', 0x21, 0, [], 'A = X - Y')
        self.define('MUL', 0x22, 0, [], 'A = X * Y')
        self.define('DIV', 0x23, 0, [], 'A = X // Y')

        # --- Bitwise Logic ---
        self.define('AND', 0x24, 0, [], 'A = X & Y')
        self.define('OR',  0x25, 0, [], 'A = X | Y')
        self.define('XOR', 0x26, 0, [], 'A = X ^ Y')
        self.define('NOT', 0x27, 0, [], 'A = ~X')

        # --- Control Flow ---
        self.define('JMP', 0x30, 1, ['addr'], 'Jump to address')
        self.define('JZ',  0x31, 1, ['addr'], 'Jump if A == 0')
        self.define('JNZ', 0x32, 1, ['addr'], 'Jump if A != 0')
        self.define('JC',  0x33, 1, ['addr'], 'Jump if Carry')
        self.define('JNC', 0x34, 1, ['addr'], 'Jump if not Carry')
        self.define('JEQ', 0x35, 1, ['addr'], 'Jump if X == Y')
        self.define('JNE', 0x36, 1, ['addr'], 'Jump if X != Y')

        # --- Function Flow ---
        self.define("RET",  0x37, 0, [], "Pop from stack twice, use the top value as lowbyte and bottom value as highbyte, and jump to that address")
        self.define("CALL", 0x38, 1, ['addr'], "Jump to address, pushing current line to stack (high byte first)")
        self.define('BZ',   0x39, 1, ['addr'], 'Call if A == 0')
        self.define('BNZ',  0x3A, 1, ['addr'], 'Call if A != 0')
        self.define('BC',   0x3B, 1, ['addr'], 'Call if Carry')
        self.define('BNC',  0x3C, 1, ['addr'], 'Call if not Carry')
        self.define('BEQ',  0x3D, 1, ['addr'], 'Call if X == Y')
        self.define('BNE',  0x3E, 1, ['addr'], 'Call if X != Y')

        # --- Load immediate ---
        self.define("LDYI", 0x49, 1, ["imm8"], "Load immediate value into Y")
        self.define("LDAI", 0x47, 1, ["imm8"], "Load immediate value into A")
        self.define("LDXI", 0x48, 1, ["imm8"], "Load immediate value into X")

        # --- Register-register ---
        self.define("MVAX", 0x50, 0, [], "Copy Register A to X")
        self.define("MVAY", 0x51, 0, [], "Copy Register A to Y")
        self.define("MVXY", 0x52, 0, [], "Copy Register X to Y")
        self.define("MVXA", 0x53, 0, [], "Copy Register X to A")
        self.define("MVYX", 0x54, 0, [], "Copy Register Y to X")
        self.define("MVYA", 0x55, 0, [], "Copy Register Y to A")

        # --- Stack ---
        self.define("PUSHA", 0x60, 0, [], "Push Register A to stack")
        self.define("POPA",  0x61, 0, [], "Pop from stack to Register A")
        self.define("PUSHX", 0x62, 0, [], "Push Register X to stack")
        self.define("POPX",  0x63, 0, [], "Pop from stack to Register X")
        self.define("PUSHY", 0x64, 0, [], "Push Register Y to stack")
        self.define("POPY",  0x65, 0, [], "Pop from stack to Register Y")


        # --- --- x32 Instructions --- ---
        self.define("SYS", 0x80, 1, ["Command"], "Request the BIOS to do a certain task")
        # --- RAM ---
        self.define('LDAR', 0x81, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXR', 0x82, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYR', 0x83, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAR', 0x84, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXR', 0x85, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYR', 0x86, 1, ['addr'], 'Store Y into address(ram)')

        self.define('LDVR', 0x87, 0, [], 'Load value from ram into register A, using X as address')
        self.define('STVR', 0x88, 0, [], 'Load value from ram into register A, using X as address')

        return

# Register X and Y are the first 2 registers respectively, more parameters will be in stack, top value first
class Sys_requests:
    def __init__(self,emulator:"em.Emulator"):
        self.emulator = emulator
        self.callNumTable = {
            0x10:self.print
        }

    def execute_sys(self, call_number):
        emulator = self.emulator
        registers = emulator.registers[1:]

        instruction = self.callNumTable[call_number]
        instruction(registers)

    def print(self, registers:list[int]): # Command 0x10
        address = registers[0] # use X register
        while 1:
            value = self.emulator.ram.load(address)
            if value != 0:
                print(chr(value),end="")
            else:
                break
            address += 1

if TYPE_CHECKING:
    import emulator as em