from typing import Literal, TYPE_CHECKING

class Executor:
    def __init__(self,emulator:"Emulator"):
        self.emulator = emulator

    def execute(self, instruction:str, variant:int, params:list[int]):
        emulator = self.emulator
        ram = emulator.ram
        registers = emulator.registers
        carry = emulator.carry
        zero = emulator.zero
        # extend 8 bit to 16 bit
        def sign_extend_word(value):
            value = value & 0xFF
            return value + (value & 0x80)*0x1FE
        # extend 16 bit to 32 bit
        def sign_extend_double(value):
            value = value & 0xFFFF
            return value + (value & 0x8000)*0x1FFFE
        # extend 32 bit to 64 bit
        def sign_extend_quad(value):
            value = value & 0xFFFF_FFFF
            return value + (value & 0x8000_0000)*0x1FFFF_FFFE
        
        def sys_register_variant_get():
            read = bool(variant&0x8000 >> 15)
            working_register = variant&0x6000 >> 13

            return read, working_register

        if instruction in ["BP","IVIP","SP"]:
            read, register = sys_register_variant_get()
            match instruction:

                case "BP":
                    if read:
                        registers[register] = register
                    else:
                        ram.stack_start = registers[register]
                case "IVIP":
                    if read:
                        registers[register] = emulator.begininst
                    else:
                        ram.int_start = registers[register]
                case "SP":
                    if read:
                        registers[register] = ram.stack_pos
                    else:
                        ram.stack_pos = registers[register]
        if instruction.startswith("LD") or instruction.startswith("ST") or instruction.startswith("MOV"):
            match instruction:
                case "LDA": registers[0] = ram.load(params[0])
                case "LDX": registers[1] = ram.load(params[0])
                case "LDY": registers[2] = ram.load(params[0])

                case "STA": ram.store(params[0],registers[0])
                case "STX": ram.store(params[0],registers[1])
                case "STY": ram.store(params[0],registers[2])

                case "LDV": registers[0] = ram.load(registers[1])
                case "STV": ram.store(registers[1],registers[0])
                case "MOV": ram.store(params[0],ram.load(params[1]))

                case "LDAD": registers[0] = ram.load_double(params[0])
                case "LDXD": registers[1] = ram.load_double(params[0])
                case "LDYD": registers[2] = ram.load_double(params[0])

                case "STAD": ram.store_double(params[0],registers[0])
                case "STXD": ram.store_double(params[0],registers[1])
                case "STYD": ram.store_double(params[0],registers[2])

                case "LDVD": registers[0] = ram.load_double(registers[1])
                case "STVD": ram.store_double(registers[1],registers[0])
                case "MOVD": ram.store_double(params[0],ram.load_double(params[1]))

                case "LDAQ": registers[0] = ram.load_quad(params[0])
                case "LDXQ": registers[1] = ram.load_quad(params[0])
                case "LDYQ": registers[2] = ram.load_quad(params[0])

                case "STAQ": ram.store_quad(params[0],registers[0])
                case "STXQ": ram.store_quad(params[0],registers[1])
                case "STYQ": ram.store_quad(params[0],registers[2])

                case "LDVQ": registers[0] = ram.load_quad(registers[1])
                case "STVQ": ram.store_quad(registers[1],registers[0])
                case "MOVQ": ram.store_quad(params[0],ram.load_quad(params[1]))

                case "LDAW": registers[0] = ram.load_word(params[0])
                case "LDXW": registers[1] = ram.load_word(params[0])
                case "LDYW": registers[2] = ram.load_word(params[0])

                case "STAW": ram.store_word(params[0],registers[0])
                case "STXW": ram.store_word(params[0],registers[1])
                case "STYW": ram.store_word(params[0],registers[2])

                case "LDVW": registers[0] = ram.load_word(registers[1])
                case "STVW": ram.store_word(registers[1],registers[0])
                case "MOVW": ram.store_word(params[0],ram.load_word(params[1]))

                case "LDAI": registers[0] = params[0]
                case "LDXI": registers[1] = params[0]
                case "LDYI": registers[2] = params[0]
        else:
            match instruction:
                case "HALT": emulator.running = False; emulator.halt_type = 1
                case "HALTZ": emulator.running = False; emulator.halt_type = 2
                case "ADD":
                    registers[0] = registers[1] + registers[2]
                    emulator.correct_register()
                case "SUB":
                    registers[0] = registers[1] - registers[2]
                    emulator.correct_register()
                case "MUL":
                    registers[0] = registers[1] * registers[2]
                    emulator.correct_register()
                case "DIV":
                    registers[0] = registers[1] // registers[2]
                    emulator.correct_register()
                case "MOD":
                    registers[0] = registers[1] % registers[2]
                    emulator.correct_register()
                case "SXTW": registers[0] = sign_extend_word(registers[0])
                case "SXTD": registers[0] = sign_extend_double(registers[0])
                case "SXTQ": registers[0] = sign_extend_quad(registers[0])

                case "AND": registers[0] = registers[1] & registers[2]
                case "OR": registers[0] = registers[1] | registers[2]
                case "XOR": registers[0] = registers[1] ^ registers[2]
                case "NOT": registers[0] = ~registers[1]
                case "SHL":
                    registers[0] = registers[1] << registers[2]
                    emulator.correct_register()
                case "SHR":
                    registers[0] = registers[1] >> registers[2]
                    emulator.correct_register()
                case "SHLB": registers[0] = registers[1] << 8
                case "SHRB": registers[0] = registers[1] >> 8

                case "CMPA": emulator.compare(registers[0],params[0])
                case "CMPX": emulator.compare(registers[1],params[0])
                case "CMPY": emulator.compare(registers[2],params[0])

                case "CPAX": emulator.compare(registers[0],registers[1])
                case "CPAY": emulator.compare(registers[0],registers[2])
                case "CPXY": emulator.compare(registers[1],registers[2])
                case "CPXA": emulator.compare(registers[1],registers[0])
                case "CPYA": emulator.compare(registers[2],registers[0])
                case "CPYX": emulator.compare(registers[2],registers[1])

                case "AJMP": emulator.counter = params[0]
                case "AJZ":
                    if zero: emulator.counter = params[0]
                case "AJNZ":
                    if not zero: emulator.counter = params[0]
                case "AJC":
                    if carry: emulator.counter = params[0]
                case "AJNC":
                    if (not carry): emulator.counter = params[0]

                case "RET": emulator.counter = ram.pop_double()
                case "ACALL": ram.push_double(emulator.counter); emulator.counter = params[0]
                case "ABZ":
                    if zero: ram.push_double(emulator.counter); emulator.counter = params[0]
                case "ABNZ":
                    if not zero: ram.push_double(emulator.counter); emulator.counter = params[0]
                case "ABC":
                    if carry: ram.push_double(emulator.counter); emulator.counter = params[0]
                case "ABNC":
                    if not carry: ram.push_double(emulator.counter); emulator.counter = params[0]

                case "JMP": emulator.counter = emulator.begininst + params[0]
                case "JZ":
                    if zero: emulator.counter = emulator.begininst + params[0]
                case "JNZ":
                    if not zero: emulator.counter = emulator.begininst + params[0]
                case "JC":
                    if carry: emulator.counter = emulator.begininst + params[0]
                case "JNC":
                    if not carry: emulator.counter = emulator.begininst + params[0]

                case "CALL": ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
                case "BZ":
                    if zero: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
                case "BNZ":
                    if not zero: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
                case "BC":
                    if carry: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
                case "BNC":
                    if (not carry): ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]

                case "JMPV": emulator.counter = registers[0]
                case "CALLV": ram.push_double(emulator.counter); emulator.counter = registers[0]

                case "MVAX": registers[1] = registers[0]
                case "MVAY": registers[2] = registers[0]
                case "MVXA": registers[0] = registers[1]
                case "MVXY": registers[2] = registers[1]
                case "MVYA": registers[0] = registers[2]
                case "MVYX": registers[1] = registers[2]

                case "PUSHA": ram.push_double(registers[0])
                case "POPA": registers[0] = ram.pop_double()
                case "PUSHX": ram.push_double(registers[1])
                case "POPX": registers[1] = ram.pop_double()
                case "PUSHY": ram.push_double(registers[2])
                case "POPY": registers[2] = ram.pop_double()
                case "PUSHR":
                    ram.push_double(registers[0])
                    ram.push_double(registers[1])
                    ram.push_double(registers[2])
                case "POPR":
                    registers[2] = ram.pop_double()
                    registers[1] = ram.pop_double()
                    registers[0] = ram.pop_double()

                case "INT":
                    address = ram.find_int(params[0])
                    ram.push_double(emulator.counter)
                    emulator.counter = address

                case "INTR":
                    ram.register_int(params[0],emulator.begininst+params[1])

                case "REDC": emulator.blocksize = max(1, emulator.blocksize * 2)
                case "EXTN": emulator.blocksize = min(4, emulator.blocksize * 2)

if TYPE_CHECKING:
    from main import Emulator