from __future__ import annotations
from typing import Literal, TYPE_CHECKING
import math

class Executor:
    def __init__(self,emulator:emulator.Emulator):
        self.emulator = emulator
        pass

    def execute(self, instruction:str, params:list[int]):
        emulator = self.emulator
        ram = emulator.ram
        registers = emulator.registers
        carry = emulator.carry
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

        if instruction == "HALT": emulator.running = False; emulator.halt_type = 1
        if instruction == "HALTZ": emulator.running = False; emulator.halt_type = 2

        elif instruction == "SETST": ram.stack_start = registers[0]
        elif instruction == "SETIV": ram.int_start = registers[0]

        elif instruction == "LDAI": registers[0] = params[0]
        elif instruction == "LDXI": registers[1] = params[0]
        elif instruction == "LDYI": registers[2] = params[0]

        elif instruction == "ADD": registers[0] = registers[1] + registers[2] ; emulator.correct_register()
        elif instruction == "SUB": registers[0] = registers[1] - registers[2] ; emulator.correct_register()
        elif instruction == "MUL": registers[0] = registers[1] * registers[2] ; emulator.correct_register()
        elif instruction == "DIV": registers[0] = registers[1] // registers[2] ; emulator.correct_register()
        elif instruction == "MOD": registers[0] = registers[1] % registers[2] ; emulator.correct_register()
        elif instruction == "SXTW": registers[0] = sign_extend_word(registers[0])
        elif instruction == "SXTD": registers[0] = sign_extend_double(registers[0])
        elif instruction == "SXTQ": registers[0] = sign_extend_quad(registers[0])

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

        elif instruction == "RET": emulator.counter = ram.pop_double()
        elif instruction == "ACALL": ram.push_double(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABZ" and registers[0] == 0: ram.push_double(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABNZ" and registers[0] != 0: ram.push_double(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABC" and carry: ram.push_double(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABNC" and (not carry): ram.push_double(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABEQ" and registers[1]==registers[2]: ram.push_double(emulator.counter); emulator.counter = params[0]
        elif instruction == "ABNE" and registers[1]==registers[2]: ram.push_double(emulator.counter); emulator.counter = params[0]

        elif instruction == "JMP": emulator.counter = emulator.begininst + params[0]
        elif instruction == "JZ" and registers[0] == 0: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JNZ" and registers[0] != 0: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JC" and carry: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JNC" and (not carry): emulator.counter = emulator.begininst + params[0]
        elif instruction == "JEQ" and registers[1]==registers[2]: emulator.counter = emulator.begininst + params[0]
        elif instruction == "JNE" and registers[1]==registers[2]: emulator.counter = emulator.begininst + params[0]

        elif instruction == "CALL": ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BZ" and registers[0] == 0: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BNZ" and registers[0] != 0: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BC" and carry: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BNC" and (not carry): ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BEQ" and registers[1]==registers[2]: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]
        elif instruction == "BNE" and registers[1]==registers[2]: ram.push_double(emulator.counter); emulator.counter = emulator.begininst + params[0]

        elif instruction == "JMPV": emulator.counter = registers[0]
        elif instruction == "CALLV": ram.push_double(emulator.counter); emulator.counter = registers[0]

        elif instruction == "MVAX": registers[1] = registers[0]
        elif instruction == "MVAY": registers[2] = registers[0]
        elif instruction == "MVXA": registers[0] = registers[1]
        elif instruction == "MVXY": registers[2] = registers[1]
        elif instruction == "MVYA": registers[0] = registers[2]
        elif instruction == "MVYX": registers[1] = registers[2]

        elif instruction == "PUSHA": ram.push_double(registers[0])
        elif instruction == "POPA": registers[0] = ram.pop_double()
        elif instruction == "PUSHX": ram.push_double(registers[1])
        elif instruction == "POPX": registers[1] = ram.pop_double()
        elif instruction == "PUSHY": ram.push_double(registers[2])
        elif instruction == "POPY": registers[2] = ram.pop_double()
        elif instruction == "PUSHR":
            ram.push_double(registers[0])
            ram.push_double(registers[1])
            ram.push_double(registers[2])
        elif instruction == "POPR":
            registers[2] = ram.pop_double()
            registers[1] = ram.pop_double()
            registers[0] = ram.pop_double()

        elif instruction == "INT":
            address = ram.find_int(params[0])
            ram.push_double(emulator.counter)
            emulator.counter = address

        elif instruction == "LDAA": registers[0] = ram.load(params[0])
        elif instruction == "LDXA": registers[1] = ram.load(params[0])
        elif instruction == "LDYA": registers[2] = ram.load(params[0])

        elif instruction == "STAA": ram.store(params[0],registers[0])
        elif instruction == "STXA": ram.store(params[0],registers[1])
        elif instruction == "STYA": ram.store(params[0],registers[2])

        elif instruction == "LDV": registers[0] = ram.load(registers[1])
        elif instruction == "STV": ram.store(registers[1],registers[0])
        elif instruction == "MOV": ram.store(params[0],ram.load(params[1]))

        elif instruction == "LDADA": registers[0] = ram.load_double(params[0])
        elif instruction == "LDXDA": registers[1] = ram.load_double(params[0])
        elif instruction == "LDYDA": registers[2] = ram.load_double(params[0])

        elif instruction == "STADA": ram.store_double(params[0],registers[0])
        elif instruction == "STXDA": ram.store_double(params[0],registers[1])
        elif instruction == "STYDA": ram.store_double(params[0],registers[2])

        elif instruction == "LDVD": registers[0] = ram.load_double(registers[1])
        elif instruction == "STVD": ram.store_double(registers[1],registers[0])
        elif instruction == "MOVDA": ram.store_double(params[0],ram.load_double(params[1]))

        elif instruction == "LDAQA": registers[0] = ram.load_quad(params[0])
        elif instruction == "LDXQA": registers[1] = ram.load_quad(params[0])
        elif instruction == "LDYQA": registers[2] = ram.load_quad(params[0])

        elif instruction == "STAQA": ram.store_quad(params[0],registers[0])
        elif instruction == "STXQA": ram.store_quad(params[0],registers[1])
        elif instruction == "STYQA": ram.store_quad(params[0],registers[2])

        elif instruction == "LDVQ": registers[0] = ram.load_quad(registers[1])
        elif instruction == "STVQ": ram.store_quad(registers[1],registers[0])
        elif instruction == "MOVQA": ram.store_quad(params[0],ram.load_quad(params[1]))

        elif instruction == "LDAWA": registers[0] = ram.load_word(params[0])
        elif instruction == "LDXWA": registers[1] = ram.load_word(params[0])
        elif instruction == "LDYWA": registers[2] = ram.load_word(params[0])

        elif instruction == "STAWA": ram.store_word(params[0],registers[0])
        elif instruction == "STXWA": ram.store_word(params[0],registers[1])
        elif instruction == "STYWA": ram.store_word(params[0],registers[2])

        elif instruction == "LDVW": registers[0] = ram.load_word(registers[1])
        elif instruction == "STVW": ram.store_word(registers[1],registers[0])
        elif instruction == "MOVWA": ram.store_word(params[0],ram.load_word(params[1]))

        elif instruction == "INTR":
            ram.register_int(params[0],emulator.begininst+params[1])

        elif instruction == "PAGE": ram.allocate_page(params[0])
        elif instruction == "FREE": ram.free_page(params[0])
        elif instruction == "MOVE": ram.relocate_page(params[0],params[1])

        elif instruction == "REDC": emulator.blocksize = max(1, emulator.blocksize * 2)
        elif instruction == "EXTN": emulator.blocksize = min(4, emulator.blocksize * 2)

if TYPE_CHECKING:
    import emulator