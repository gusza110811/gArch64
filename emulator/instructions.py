from typing import Literal, TYPE_CHECKING
import __future__
import executor

class Opcodes:
    def __init__(self, emulator:"em.Emulator"):
        self.emulator = emulator
        self.OPCODES:dict[(str,dict[Literal["mnemonic","opcode","size","operands","desc"]])] = {}
        self.executor = executor.Executor(self.emulator)
        self.definitions()

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
        self.define('SHL', 0x28, 0, [], 'A = X << Y')
        self.define('SHR', 0x29, 0, [], 'A = X >> Y')
        self.define('SHLB', 0x2A, 0, [], 'A = X << 8')
        self.define('SHRB', 0x2B, 0, [], 'A = X >> 8')

        # --- Extended Arithmetic ---
        self.define("MOD", 0x2C, 0, [], 'A = X % Y')

        # --- Absolute Control Flow ---
        self.define('AJMP', 0x30, 1, ['addr'], 'Jump to address')
        self.define('AJZ',  0x31, 1, ['addr'], 'Jump if A == 0')
        self.define('AJNZ', 0x32, 1, ['addr'], 'Jump if A != 0')
        self.define('AJC',  0x33, 1, ['addr'], 'Jump if Carry')
        self.define('AJNC', 0x34, 1, ['addr'], 'Jump if not Carry')
        self.define('AJEQ', 0x35, 1, ['addr'], 'Jump if X == Y')
        self.define('AJNE', 0x36, 1, ['addr'], 'Jump if X != Y')

        # --- Absolute Function Flow ---
        self.define("ACALL", 0x38, 1, ['addr'], "Jump to address, pushing current line to stack")
        self.define('ABZ',   0x39, 1, ['addr'], 'Call if A == 0')
        self.define('ABNZ',  0x3A, 1, ['addr'], 'Call if A != 0')
        self.define('ABC',   0x3B, 1, ['addr'], 'Call if Carry')
        self.define('ABNC',  0x3C, 1, ['addr'], 'Call if not Carry')
        self.define('ABEQ',  0x3D, 1, ['addr'], 'Call if X == Y')
        self.define('ABNE',  0x3E, 1, ['addr'], 'Call if X != Y')

        # Indirect Flow Control
        self.define('JMPV', 0x3F, 0, [], 'Jump to address stored in register A')
        self.define('CALLV', 0x40, 0, [], 'CALL function at address stored in register A')

        # Other Flow Control
        self.define('HALT', 0x00, 0, [], 'Stop execution')
        self.define("RET",  0x37, 0, [], "Pop from stack, and jump to that address")

        # --- Register-register ---
        self.define("MVAX", 0x50, 0, [], "Copy Register A to X")
        self.define("MVAY", 0x51, 0, [], "Copy Register A to Y")
        self.define("MVXY", 0x52, 0, [], "Copy Register X to Y")
        self.define("MVXA", 0x53, 0, [], "Copy Register X to A")
        self.define("MVYX", 0x54, 0, [], "Copy Register Y to X")
        self.define("MVYA", 0x55, 0, [], "Copy Register Y to A")

        # --- Load immediate ---
        self.define("LDAI", 0x47, 1, ["immB"], "Load immediate value into A")
        self.define("LDXI", 0x48, 1, ["immB"], "Load immediate value into X")
        self.define("LDYI", 0x49, 1, ["immB"], "Load immediate value into Y")

        # --- Stack ---
        self.define("PUSHA", 0x60, 0, [], "Push Register A to stack")
        self.define("POPA",  0x61, 0, [], "Pop from stack to Register A")
        self.define("PUSHX", 0x62, 0, [], "Push Register X to stack")
        self.define("POPX",  0x63, 0, [], "Pop from stack to Register X")
        self.define("PUSHY", 0x64, 0, [], "Push Register Y to stack")
        self.define("POPY",  0x65, 0, [], "Pop from stack to Register Y")
        self.define("PUSHR", 0x66, 0, [], "Push every Register to stack")
        self.define("POPR",  0x67, 0, [], "Pop from stack to every Register")

        # --- Relative Control Flow ---
        self.define('JMP', 0x70, 1, ['addr'], 'Jump to address')
        self.define('JZ',  0x71, 1, ['addr'], 'Jump if A == 0')
        self.define('JNZ', 0x72, 1, ['addr'], 'Jump if A != 0')
        self.define('JC',  0x73, 1, ['addr'], 'Jump if Carry')
        self.define('JNC', 0x74, 1, ['addr'], 'Jump if not Carry')
        self.define('JEQ', 0x75, 1, ['addr'], 'Jump if X == Y')
        self.define('JNE', 0x76, 1, ['addr'], 'Jump if X != Y')

        # --- Relative Function Flow ---
        self.define("CALL", 0x78, 1, ['addr'], "Jump to address, pushing current line to stack")
        self.define('BZ',   0x79, 1, ['addr'], 'Call if A == 0')
        self.define('BNZ',  0x7A, 1, ['addr'], 'Call if A != 0')
        self.define('BC',   0x7B, 1, ['addr'], 'Call if Carry')
        self.define('BNC',  0x7C, 1, ['addr'], 'Call if not Carry')
        self.define('BEQ',  0x7D, 1, ['addr'], 'Call if X == Y')
        self.define('BNE',  0x7E, 1, ['addr'], 'Call if X != Y')


        # --- --- Extended Instructions --- ---
        self.define("INT", 0x80, 1, ["Command"], "Raise interrupt to do a certain task")
        self.define('INTR', 0x90, 2, ['int_id','subroutine_address'], 'Map [int_id] to [subroutine_address]')

        # --- RAM ---
        self.define('LDA', 0x81, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDX', 0x82, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDY', 0x83, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STA', 0x84, 1, ['addr'], 'Store A into address(ram)')
        self.define('STX', 0x85, 1, ['addr'], 'Store X into address(ram)')
        self.define('STY', 0x86, 1, ['addr'], 'Store Y into address(ram)')

        self.define('LDV', 0x87, 0, [], 'Load value from ram into register A, using X as address')
        self.define('STV', 0x88, 0, [], 'Store value in register A to ram, using X as address')
        self.define('MOV', 0x89, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        self.define('MVCR', 0x8A, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src (cache) to addr_dst (ram)')
        self.define('MVRC', 0x8B, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src (ram) to addr_dst (cache)')

        # --- Page allocation ---
        self.define('PAGE', 0x9A, 1, ['page'], 'Allocate page to the first available frame')
        self.define('FREE', 0x9B, 1, ['page'], 'Unallocate page')

        # --- Block size ---
        self.define('REDUCE', 0xA0, 0, [], 'Halves the block size (do nothing if blocksize is 1 word)')
        self.define('EXTEND', 0xA1, 0, [], 'Doubles the block size')

        # --- Double-word RAM load/store ---
        self.define('LDAD', 0xB1, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXD', 0xB2, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYD', 0xB3, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAD', 0xB4, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXD', 0xB5, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYD', 0xB6, 1, ['addr'], 'Store Y into address(ram)')

        self.define('LDVD', 0xB7, 0, [], 'Load value from ram into register A, using X as address')
        self.define('STVD', 0xB8, 0, [], 'Store value in register A to ram, using X as address')
        self.define('MOVD', 0xB9, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        return


if TYPE_CHECKING:
    import emulator as em