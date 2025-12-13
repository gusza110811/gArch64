from typing import Literal, TYPE_CHECKING
import __future__
import math

class Executor:
    def __init__(self,emulator:"emulator.Emulator"):
        self.emulator = emulator
        pass

    def execute(self, instruction:str, params:list[int]):
        emulator = self.emulator
        ram = emulator.ram
        cache = emulator.cache
        registers = emulator.registers
        carry = emulator.carry

        if instruction == "HALT": emulator.running = False

        elif instruction == "LDA": registers[0] = cache.load(params[0])
        elif instruction == "LDX": registers[1] = cache.load(params[0])
        elif instruction == "LDY": registers[2] = cache.load(params[0])

        elif instruction == "STA": cache.store(params[0],registers[0])
        elif instruction == "STX": cache.store(params[0],registers[1])
        elif instruction == "STY": cache.store(params[0],registers[2])

        elif instruction == "MOV": cache.store(params[0],cache.load(params[1]))

        elif instruction == "LDAI": registers[0] = params[0]
        elif instruction == "LDXI": registers[1] = params[0]
        elif instruction == "LDYI": registers[2] = params[0]

        elif instruction == "LDV":registers[0] = cache.load(registers[1])
        elif instruction == "STV": cache.store(registers[1], registers[0])

        elif instruction == "ADD": registers[0] = registers[1] + registers[2] ; emulator.correct_register()
        elif instruction == "SUB": registers[0] = registers[1] - registers[2] ; emulator.correct_register()
        elif instruction == "MUL": registers[0] = registers[1] * registers[2] ; emulator.correct_register()
        elif instruction == "DIV": registers[0] = registers[1] // registers[2] ; emulator.correct_register()
        elif instruction == "MOD": registers[0] = registers[1] % registers[2] ; emulator.correct_register()

        elif instruction == "AND": registers[0] = registers[1] & registers[2]
        elif instruction == "OR": registers[0] = registers[1] | registers[2]
        elif instruction == "XOR": registers[0] = registers[1] ^ registers[2]
        elif instruction == "NOT": registers[0] = ~registers[1]
        elif instruction == "SHL": registers[0] = registers[1] << registers[2]; emulator.correct_register()
        elif instruction == "SHR": registers[0] = registers[1] >> registers[2]; emulator.correct_register()
        elif instruction == "SHLB": registers[0] = registers[1] << 8
        elif instruction == "SHRB": registers[0] = registers[1] >> 8

        elif instruction == "AJMP": emulator.counter = params[0]
        elif instruction == "AJZ" and registers[0] == 0: emulator.counter = params[0]
        elif instruction == "AJNZ" and registers[0] != 0: emulator.counter = params[0]
        elif instruction == "AJC" and carry: emulator.counter = params[0]
        elif instruction == "AJNC" and (not carry): emulator.counter = params[0]
        elif instruction == "AJEQ" and registers[1]==registers[2]: emulator.counter = params[0]
        elif instruction == "AJNE" and registers[1]==registers[2]: emulator.counter = params[0]

        elif instruction == "RET": emulator.counter = cache.pop()
        elif instruction == "ACALL": cache.push(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABZ" and registers[0] == 0: cache.push(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABNZ" and registers[0] != 0: cache.push(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABC" and carry: cache.push(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABNC" and (not carry): cache.push(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABEQ" and registers[1]==registers[2]: cache.push(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABNE" and registers[1]==registers[2]: cache.push(emulator.counter); emulator.counter = params[0]

        elif instruction == "JMP": emulator.counter = emulator.begininst + params[0]
        elif instruction == "JZ" and registers[0] == 0: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JNZ" and registers[0] != 0: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JC" and carry: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JNC" and (not carry): emulator.counter = emulator.begininst + params[0]
        elif instruction == "JEQ" and registers[1]==registers[2]: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JNE" and registers[1]==registers[2]: emulator.counter = emulator.begininst + params[0]

        elif instruction == "CALL": cache.push(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BZ" and registers[0] == 0: cache.push(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BNZ" and registers[0] != 0: cache.push(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BC" and carry: cache.push(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BNC" and (not carry): cache.push(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BEQ" and registers[1]==registers[2]: cache.push(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BNE" and registers[1]==registers[2]: cache.push(emulator.counter); emulator.counter = emulator.begininst + params[0]

        elif instruction == "MVAX": registers[1] = registers[0]
        elif instruction == "MVAY": registers[2] = registers[0]
        elif instruction == "MVXA": registers[0] = registers[1]
        elif instruction == "MVXY": registers[2] = registers[1]
        elif instruction == "MVYA": registers[0] = registers[2]
        elif instruction == "MVYX": registers[1] = registers[2]

        elif instruction == "PUSHA": cache.push(registers[0])
        elif instruction == "POPA": registers[0] = cache.pop()
        elif instruction == "PUSHX": cache.push(registers[1])
        elif instruction == "POPX": registers[1] = cache.pop()
        elif instruction == "PUSHY": cache.push(registers[2])
        elif instruction == "POPY": registers[2] = cache.pop()
        elif instruction == "PUSHR":
            cache.push(registers[0])
            cache.push(registers[1])
            cache.push(registers[2])
        elif instruction == "POPR":
            registers[2] = cache.pop()
            registers[1] = cache.pop()
            registers[0] = cache.pop()


        elif instruction == "INT":
            address = cache.find_int(params[0])
            cache.push(emulator.counter)
            emulator.counter = address

        elif instruction == "LDAR": registers[0] = ram.load(params[0])
        elif instruction == "LDXR": registers[1] = ram.load(params[0])
        elif instruction == "LDYR": registers[2] = ram.load(params[0])

        elif instruction == "STAR": ram.store(params[0],registers[0])
        elif instruction == "STXR": ram.store(params[0],registers[1])
        elif instruction == "STYR": ram.store(params[0],registers[2])

        elif instruction == "LDVR": registers[0] = ram.load(registers[1])
        elif instruction == "STVR": ram.store(registers[1],registers[0])

        elif instruction == "MOVR": ram.store(params[0],ram.load(params[1]))

        elif instruction == "INTR": cache.register_int(params[0],emulator.begininst+params[1])

        elif instruction == "PAGE": ram.allocate_page(params[0])
        elif instruction == "FREE": ram.free_page(params[0])

        elif instruction == "REDUCE": emulator.blocksize = math.ceil(emulator.blocksize / 2)
        elif instruction == "EXTEND": emulator.blocksize *= 2

if TYPE_CHECKING:
    import emulator