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
    def define(self,op, code, operands, desc):
        self.OPCODES[code] = {
            'mnemonic': op,
            'opcode': code,
            'operands': operands,
            'desc': desc
        }

    def definitions(self):
        # --- Special Register ---
        self.define('BP', 0x10, [], 'RW top of stack')
        self.define('IVIP', 0x11, [], 'W beginning of IVT or R instruction pointer')
        self.define('SP', 0x12, [], 'RW stack pointer')

        # --- Arithmetic ---
        self.define('ADD', 0x20, [], 'A = X + Y')
        self.define('SUB', 0x21, [], 'A = X - Y')
        self.define('MUL', 0x22, [], 'A = X * Y')
        self.define('DIV', 0x23, [], 'A = X // Y')

        # --- Bitwise Logic ---
        self.define('AND', 0x24, [], 'A = X & Y')
        self.define('OR',  0x25, [], 'A = X | Y')
        self.define('XOR', 0x26, [], 'A = X ^ Y')
        self.define('NOT', 0x27, [], 'A = ~X')
        self.define('SHL', 0x28, [], 'A = X << Y')
        self.define('SHR', 0x29, [], 'A = X >> Y')
        self.define('SHLB', 0x2A, [], 'A = X << 8')
        self.define('SHRB', 0x2B, [], 'A = X >> 8')

        # --- Extended Arithmetic ---
        self.define("MOD",  0x2C, [], 'A = X % Y')
        self.define("SXTW", 0x2D, [], 'A (i8) -> A (i16)')
        self.define("SXTD", 0x2E, [], 'A (i16) -> A (i32)')
        self.define("SXTQ", 0x2F, [], 'A (i32) -> A (i64)')

        # --- Comparison ---
        self.define('CMPA', 0x35, ['imm'], 'A ? imm')
        self.define('CMPX', 0x36, ['imm'], 'X ? imm')
        self.define('CMPY', 0x3D, ['imm'], 'Y ? imm')

        self.define('CMAX', 0x75, [], 'A ? X')
        self.define('CMAY', 0x76, [], 'A ? Y')
        self.define('CMXY', 0x77, [], 'X ? Y')
        self.define('CMXA', 0x7D, [], 'X ? A')
        self.define('CMYA', 0x7E, [], 'Y ? A')
        self.define('CMYX', 0x7F, [], 'Y ? X')

        # --- Absolute Control Flow ---
        self.define('AJMP', 0x30, ['addr'], 'Jump to address')
        self.define('AJZ',  0x31, ['addr'], 'Jump if Z flag set')
        self.define('AJNZ', 0x32, ['addr'], 'Jump if Z flag not set')
        self.define('AJC',  0x33, ['addr'], 'Jump if Carry')
        self.define('AJNC', 0x34, ['addr'], 'Jump if not Carry')

        # --- Absolute Function Flow ---
        self.define("ACALL", 0x38, ['addr'], "Jump to address, pushing current line to stack")
        self.define('ABZ',   0x39, ['addr'], 'Call if Z flag set')
        self.define('ABNZ',  0x3A, ['addr'], 'Call if Z flag not set')
        self.define('ABC',   0x3B, ['addr'], 'Call if Carry')
        self.define('ABNC',  0x3C, ['addr'], 'Call if not Carry')

        # Indirect Flow Control
        self.define('JMPV' , 0x3F, [], 'Jump to address stored in register A')
        self.define('CALLV', 0x3E, [], 'Call function at address stored in register A')

        # Other Flow Control
        self.define('HALT',  0xFF, [], 'Stop execution')
        self.define('HALTZ', 0x00, [], 'Stop execution')
        self.define("RET",   0x37, [], "Pop from stack, and jump to that address")

        # --- Register-register ---
        self.define("MVAX", 0x50, [], "Copy Register A to X")
        self.define("MVAY", 0x51, [], "Copy Register A to Y")
        self.define("MVXY", 0x52, [], "Copy Register X to Y")
        self.define("MVXA", 0x53, [], "Copy Register X to A")
        self.define("MVYX", 0x54, [], "Copy Register Y to X")
        self.define("MVYA", 0x55, [], "Copy Register Y to A")

        # --- Load immediate ---
        self.define("LDAI", 0x47, ["imm"], "Load immediate value into A")
        self.define("LDXI", 0x48, ["imm"], "Load immediate value into X")
        self.define("LDYI", 0x49, ["imm"], "Load immediate value into Y")

        # --- Stack ---
        self.define("PUSHA", 0x60, [], "Push Register A to stack")
        self.define("POPA",  0x61, [], "Pop from stack to Register A")
        self.define("PUSHX", 0x62, [], "Push Register X to stack")
        self.define("POPX",  0x63, [], "Pop from stack to Register X")
        self.define("PUSHY", 0x64, [], "Push Register Y to stack")
        self.define("POPY",  0x65, [], "Pop from stack to Register Y")
        self.define("PUSHR", 0x66, [], "Push every Register to stack")
        self.define("POPR",  0x67, [], "Pop from stack to every Register")

        # --- Relative Control Flow ---
        self.define('JMP', 0x70, ['addr'], 'Jump to address')
        self.define('JZ',  0x71, ['addr'], 'Call if Z flag set')
        self.define('JNZ', 0x72, ['addr'], 'Call if Z flag not set')
        self.define('JC',  0x73, ['addr'], 'Jump if Carry')
        self.define('JNC', 0x74, ['addr'], 'Jump if not Carry')

        # --- Relative Function Flow ---
        self.define("CALL", 0x78, ['addr'], "Jump to address, pushing current line to stack")
        self.define('BZ',   0x79, ['addr'], 'Call if Z flag set')
        self.define('BNZ',  0x7A, ['addr'], 'Call if Z flag not set')
        self.define('BC',   0x7B, ['addr'], 'Call if Carry')
        self.define('BNC',  0x7C, ['addr'], 'Call if not Carry')

        # --- Interrupt ---
        self.define("INT", 0x80, ["Command"], "Raise interrupt to do a certain task")
        self.define('INTR', 0x90, ['int_id','subroutine_address'], 'Map [int_id] to [subroutine_address]')

        # --- RAM ---
        self.define('LDA', 0x81, ['addr'], 'Load from address(ram) into A')
        self.define('LDX', 0x82, ['addr'], 'Load from address(ram) into X')
        self.define('LDY', 0x83, ['addr'], 'Load from address(ram) into Y')

        self.define('STA', 0x84, ['addr'], 'Store A into address(ram)')
        self.define('STX', 0x85, ['addr'], 'Store X into address(ram)')
        self.define('STY', 0x86, ['addr'], 'Store Y into address(ram)')

        self.define('LDV', 0x87, [], 'Load value from ram into register A, using X as address')
        self.define('STV', 0x88, [], 'Store value in register A to ram, using X as address')
        self.define('MOV', 0x89, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        # --- Word RAM load/store ---
        self.define('LDAW', 0x91, ['addr'], 'Load from address(ram) into A')
        self.define('LDXW', 0x92, ['addr'], 'Load from address(ram) into X')
        self.define('LDYW', 0x93, ['addr'], 'Load from address(ram) into Y')

        self.define('STAW', 0x94, ['addr'], 'Store A into address(ram)')
        self.define('STXW', 0x95, ['addr'], 'Store X into address(ram)')
        self.define('STYW', 0x96, ['addr'], 'Store Y into address(ram)')

        self.define('LDVW', 0x97, [], 'Load value from ram into register A, using X as address')
        self.define('STVW', 0x98, [], 'Store value in register A to ram, using X as address')
        self.define('MOVW', 0x99, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        # --- Double-word RAM load/store ---
        self.define('LDAD', 0xA1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXD', 0xA2, ['addr'], 'Load from address(ram) into X')
        self.define('LDYD', 0xA3, ['addr'], 'Load from address(ram) into Y')

        self.define('STAD', 0xA4, ['addr'], 'Store A into address(ram)')
        self.define('STXD', 0xA5, ['addr'], 'Store X into address(ram)')
        self.define('STYD', 0xA6, ['addr'], 'Store Y into address(ram)')

        self.define('LDVD', 0xA7, [], 'Load value from ram into register A, using X as address')
        self.define('STVD', 0xA8, [], 'Store value in register A to ram, using X as address')
        self.define('MOVD', 0xA9, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        # --- Quad-word RAM load/store ---
        self.define('LDAQ', 0xB1, ['addr'], 'Load from address(ram) into A')
        self.define('LDXQ', 0xB2, ['addr'], 'Load from address(ram) into X')
        self.define('LDYQ', 0xB3, ['addr'], 'Load from address(ram) into Y')

        self.define('STAQ', 0xB4, ['addr'], 'Store A into address(ram)')
        self.define('STXQ', 0xB5, ['addr'], 'Store X into address(ram)')
        self.define('STYQ', 0xB6, ['addr'], 'Store Y into address(ram)')

        self.define('LDVQ', 0xB7, [], 'Load value from ram into register A, using X as address')
        self.define('STVQ', 0xB8, [], 'Store value in register A to ram, using X as address')
        self.define('MOVQ', 0xB9, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst (ram)')

        return


if TYPE_CHECKING:
    import emulator as em