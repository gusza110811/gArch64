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
        # --- Special Register ---
        self.define('SETST', 0x10, 0, [], 'Set/Change top of stack')
        self.define('SETIV', 0x11, 0, [], 'Set/Change beginning of IVT')

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
        self.define("SXTW", 0x2D, 0, [], 'A (i8) -> A (i16)')
        self.define("SXTD", 0x2E, 0, [], 'A (i16) -> A (i32)')
        self.define("SXTQ", 0x2F, 0, [], 'A (i32) -> A (i64)')

        # --- Comparison ---
        self.define('CMPA', 0x35, 1, ['imm'], 'A ? imm')
        self.define('CMPX', 0x36, 1, ['imm'], 'X ? imm')
        self.define('CMPY', 0x3D, 1, ['imm'], 'Y ? imm')

        self.define('CMAX', 0x75, 0, [], 'A ? X')
        self.define('CMAY', 0x76, 0, [], 'A ? Y')
        self.define('CMXY', 0x77, 0, [], 'X ? Y')
        self.define('CMXA', 0x7D, 0, [], 'X ? A')
        self.define('CMYA', 0x7E, 0, [], 'Y ? A')
        self.define('CMYX', 0x7F, 0, [], 'Y ? X')

        # --- Absolute Control Flow ---
        self.define('AJMP', 0x30, 1, ['addr'], 'Jump to address')
        self.define('AJZ',  0x31, 1, ['addr'], 'Jump if Z flag set')
        self.define('AJNZ', 0x32, 1, ['addr'], 'Jump if Z flag not set')
        self.define('AJC',  0x33, 1, ['addr'], 'Jump if Carry')
        self.define('AJNC', 0x34, 1, ['addr'], 'Jump if not Carry')

        # --- Absolute Function Flow ---
        self.define("ACALL", 0x38, 1, ['addr'], "Jump to address, pushing current line to stack")
        self.define('ABZ',   0x39, 1, ['addr'], 'Call if Z flag set')
        self.define('ABNZ',  0x3A, 1, ['addr'], 'Call if Z flag not set')
        self.define('ABC',   0x3B, 1, ['addr'], 'Call if Carry')
        self.define('ABNC',  0x3C, 1, ['addr'], 'Call if not Carry')

        # Indirect Flow Control
        self.define('JMPV', 0x3F, 0, [], 'Jump to address stored in register A')
        self.define('CALLV', 0x40, 0, [], 'CALL function at address stored in register A')

        # Other Flow Control
        self.define('HALT', 0xFF, 0, [], 'Stop execution')
        self.define('HALTZ', 0x00, 0, [], 'Stop execution')
        self.define("RET",  0x37, 0, [], "Pop from stack, and jump to that address")

        # --- Register-register ---
        self.define("MVAX", 0x50, 0, [], "Copy Register A to X")
        self.define("MVAY", 0x51, 0, [], "Copy Register A to Y")
        self.define("MVXY", 0x52, 0, [], "Copy Register X to Y")
        self.define("MVXA", 0x53, 0, [], "Copy Register X to A")
        self.define("MVYX", 0x54, 0, [], "Copy Register Y to X")
        self.define("MVYA", 0x55, 0, [], "Copy Register Y to A")

        # --- Load immediate ---
        self.define("LDAI", 0x47, 1, ["imm"], "Load immediate value into A")
        self.define("LDXI", 0x48, 1, ["imm"], "Load immediate value into X")
        self.define("LDYI", 0x49, 1, ["imm"], "Load immediate value into Y")

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
        self.define('JZ',  0x71, 1, ['addr'], 'Call if Z flag set')
        self.define('JNZ', 0x72, 1, ['addr'], 'Call if Z flag not set')
        self.define('JC',  0x73, 1, ['addr'], 'Jump if Carry')
        self.define('JNC', 0x74, 1, ['addr'], 'Jump if not Carry')

        # --- Relative Function Flow ---
        self.define("CALL", 0x78, 1, ['addr'], "Jump to address, pushing current line to stack")
        self.define('BZ',   0x79, 1, ['addr'], 'Call if Z flag set')
        self.define('BNZ',  0x7A, 1, ['addr'], 'Call if Z flag not set')
        self.define('BC',   0x7B, 1, ['addr'], 'Call if Carry')
        self.define('BNC',  0x7C, 1, ['addr'], 'Call if not Carry')

        # --- Interrupt ---
        self.define("INT", 0x80, 1, ["Command"], "Raise interrupt to do a certain task")
        self.define('INTR', 0x90, 2, ['int_id','subroutine_address'], 'Map [int_id] to [subroutine_address]')

        # --- RAM ---
        self.define('LDAA', 0x81, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXA', 0x82, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYA', 0x83, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAA', 0x84, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXA', 0x85, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYA', 0x86, 1, ['addr'], 'Store Y into address(ram)')

        self.define('LDV', 0x87, 0, [], 'Load value from ram into register A, using X as address')
        self.define('STV', 0x88, 0, [], 'Store value in register A to ram, using X as address')
        self.define('MOVA', 0x89, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        # --- Relative RAM ---
        self.define('LDA', 0x8A, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDX', 0x8B, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDY', 0x8C, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STA', 0x8D, 1, ['addr'], 'Store A into address(ram)')
        self.define('STX', 0x8E, 1, ['addr'], 'Store X into address(ram)')
        self.define('STY', 0x8F, 1, ['addr'], 'Store Y into address(ram)')

        self.define('MOV', 0x9F, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        # --- Page allocation ---
        self.define('PAGE', 0x9A, 1, ['page'], 'Allocate page to the first available frame')
        self.define('FREE', 0x9B, 1, ['page'], 'Unallocate page')
        self.define('MOVE', 0x9C, 1, ['page_old','page_new'], 'Change ID of a page')

        # --- Block size ---
        self.define('REDC', 0xA0, 0, [], 'Halves the block size and register width, min at 1 words (2 bytes; 16 bit)')
        self.define('EXTN', 0xA1, 0, [], 'Doubles the block size and register width, max at 4 words (8 bytes; 64 bit)')

        # --- Double-word RAM load/store ---
        self.define('LDADA', 0xB1, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXDA', 0xB2, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYDA', 0xB3, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STADA', 0xB4, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXDA', 0xB5, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYDA', 0xB6, 1, ['addr'], 'Store Y into address(ram)')

        self.define('LDVD', 0xB7, 0, [], 'Load value from ram into register A, using X as address')
        self.define('STVD', 0xB8, 0, [], 'Store value in register A to ram, using X as address')
        self.define('MOVDA', 0xB9, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')
        # Relative
        self.define('LDAD', 0xBA, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXD', 0xBB, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYD', 0xBC, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAD', 0xBD, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXD', 0xBE, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYD', 0xBF, 1, ['addr'], 'Store Y into address(ram)')

        self.define('MOVD', 0xB0, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        # --- Quad-word RAM load/store ---
        self.define('LDAQA', 0xC1, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXQA', 0xC2, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYQA', 0xC3, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAQA', 0xC4, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXQA', 0xC5, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYQA', 0xC6, 1, ['addr'], 'Store Y into address(ram)')

        self.define('LDVQ', 0xC7, 0, [], 'Load value from ram into register A, using X as address')
        self.define('STVQ', 0xC8, 0, [], 'Store value in register A to ram, using X as address')
        self.define('MOVQA', 0xC9, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')
        # Relative
        self.define('LDAQ', 0xCA, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXQ', 0xCB, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYQ', 0xCC, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAQ', 0xCD, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXQ', 0xCE, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYQ', 0xCF, 1, ['addr'], 'Store Y into address(ram)')

        self.define('MOVQ', 0xC0, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        # --- Word RAM load/store ---
        self.define('LDAWA', 0xD1, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXWA', 0xD2, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYWA', 0xD3, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAWA', 0xD4, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXWA', 0xD5, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYWA', 0xD6, 1, ['addr'], 'Store Y into address(ram)')

        self.define('LDVW', 0xD7, 0, [], 'Load value from ram into register A, using X as address')
        self.define('STVW', 0xD8, 0, [], 'Store value in register A to ram, using X as address')
        self.define('MOVWA', 0xD9, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')
        # Relative
        self.define('LDAW', 0xDA, 1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXW', 0xDB, 1, ['addr'], 'Load from address(ram) into X')
        self.define('LDYW', 0xDC, 1, ['addr'], 'Load from address(ram) into Y')

        self.define('STAW', 0xDD, 1, ['addr'], 'Store A into address(ram)')
        self.define('STXW', 0xDE, 1, ['addr'], 'Store X into address(ram)')
        self.define('STYW', 0xDF, 1, ['addr'], 'Store Y into address(ram)')

        self.define('MOVW', 0xD0, 2, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')


        return


if TYPE_CHECKING:
    import emulator as em