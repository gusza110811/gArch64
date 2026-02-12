from __future__ import annotations

class Command:
    def __init__(self):
        pass

    def get_value(self, params:list["Parameter"]=None, size=4, position=0) -> bytes:
        return

    def encode_immediate(self, params:list[Parameter], size=4, signed=False, params_count=1) -> bytes:
        """Encode all params as little-endian byte values."""
        result = b''.join(p.value.to_bytes(size, "little",signed=signed) for p in params)
        if len(result) < (params_count*size):
            raise SyntaxError("Not Enough paramters")
        return result

class Halt(Command):
    def get_value(self, params=None, size=4, position=0):
        return bytes([0xFF,0x00])

class Mov(Command):
    def get_value(self, params = None, size=4, position=0) -> bytes:
        if len(params) < 2:
            raise SyntaxError("Not enough parameters")
        if len(params) > 2:
            raise SyntaxError("Too many parameters")
        destination = params[0]
        source = params[-1]
        if isinstance(destination,Immediate):
            raise ValueError("Can't store value to an immediate value")
        
        if isinstance(source,Immediate) and isinstance(destination,RamAddr):
            raise ValueError("Can't directly store immediate value to ram")

        # MOV
        elif isinstance(destination,RamAddr) and isinstance(source,RamAddr):
            return 0x89.to_bytes(2,"little") + self.encode_immediate([destination,source],size,params_count=2)
        # Load
        if isinstance(destination,Register) and isinstance(source,RamAddr):
            return (0x81 + destination.value).to_bytes(2,"little") + source.value.to_bytes(size,byteorder="little")
        # Store
        elif isinstance(destination,RamAddr) and isinstance(source,Register):
            return (0x84 + source.value).to_bytes(2,"little") + destination.value.to_bytes(size,byteorder="little")
        
        # Register-Register
        elif isinstance(destination,Register) and isinstance(source,Register):
            destreg = destination.value
            sourcereg = source.value
            # there wasnt a meaningful pattern so it had to be hard coded, oops
            if sourcereg == 0:
                if destreg == 1:
                    return 0x50.to_bytes(2,"little")
                if destreg == 2:
                    return 0x51.to_bytes(2,"little")
            if sourcereg == 1:
                if destreg == 2:
                    return 0x52.to_bytes(2,"little")
                if destreg == 0:
                    return 0x53.to_bytes(2,"little")
            if sourcereg == 2:
                if destreg == 1:
                    return 0x54.to_bytes(2,"little")
                if destreg == 0:
                    return 0x55.to_bytes(2,"little")
        
        # immediate value
        elif isinstance(destination,Register) and isinstance(source,Immediate):
            return (0x47+destination.value).to_bytes(2,byteorder="little") + source.value.to_bytes(size,byteorder="little")

class Movd(Command):
    def get_value(self, params = None, size=4, position=0) -> bytes:
        destination = params[0]
        source = params[-1]
        # Load ram
        if isinstance(destination,Register) and isinstance(source,RamAddr):
            return (0xA1 + destination.value).to_bytes(2,"little") + source.value.to_bytes(size,byteorder="little")
        # Store ram
        elif isinstance(destination,RamAddr) and isinstance(source,Register):
            return (0xA4 + source.value).to_bytes(2,"little") + destination.value.to_bytes(size,byteorder="little")
        # MOV
        elif isinstance(destination,RamAddr) and isinstance(source,RamAddr):
            return 0xA9.to_bytes(2,"little") + self.encode_immediate([destination,source],size,params_count=2)
        else:
            raise SyntaxError("Movd is only for register-memory and memory-memory operations, for other operations, use Mov")

class Movq(Command):
    def get_value(self, params = None, size=4, position=0) -> bytes:
        destination = params[0]
        source = params[-1]
        # Load ram
        if isinstance(destination,Register) and isinstance(source,RamAddr):
            return (0xB1 + destination.value).to_bytes(2,"little") + source.value.to_bytes(size,byteorder="little")
        # Store ram
        elif isinstance(destination,RamAddr) and isinstance(source,Register):
            return (0xB4 + source.value).to_bytes(2,"little") + destination.value.to_bytes(size,byteorder="little")
        # MOV
        elif isinstance(destination,RamAddr) and isinstance(source,RamAddr):
            return 0xB9.to_bytes(2,"little") + self.encode_immediate([destination,source],size,params_count=2)
        else:
            raise SyntaxError("Movq is only for register-memory and memory-memory operations, for other operations, use Mov")

class Movw(Command):
    def get_value(self, params = None, size=4, position=0) -> bytes:
        destination = params[0]
        source = params[-1]
        # Load ram
        if isinstance(destination,Register) and isinstance(source,RamAddr):
            return (0x91 + destination.value).to_bytes(2,"little") + source.value.to_bytes(size,byteorder="little")
        # Store ram
        elif isinstance(destination,RamAddr) and isinstance(source,Register):
            return (0x94 + source.value).to_bytes(2,"little") + destination.value.to_bytes(size,byteorder="little")
        # MOV
        elif isinstance(destination,RamAddr) and isinstance(source,RamAddr):
            return 0x99.to_bytes(2,"little") + self.encode_immediate([destination,source],size,params_count=2)
        else:
            raise SyntaxError("Movw is only for register-memory and memory-memory operations, for other operations, use Mov")


# Special Registers
class Setst(Command):
    def get_value(self, params = None, size=4, position=0):
        return 0x10.to_bytes(2,'little')

class Setiv(Command):
    def get_value(self, params = None, size=4, position=0):
        return 0x11.to_bytes(2,'little')

# Arithmetic
class Add(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x20).to_bytes(2, "little")

class Sub(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x21).to_bytes(2, "little")

class Mul(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x22).to_bytes(2, "little")

class Div(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x23).to_bytes(2, "little")

class Mod(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x2C).to_bytes(2, "little")

class Sxtw(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x2D).to_bytes(2, "little")

class Sxtd(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x2E).to_bytes(2, "little")

class Sxtq(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x2F).to_bytes(2, "little")

# Bitwise logic
class And(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x24).to_bytes(2, "little")

class Or(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x25).to_bytes(2, "little")

class Xor(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x26).to_bytes(2, "little")

class Not(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x27).to_bytes(2, "little")

class Shl(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x28).to_bytes(2, "little")
class Shr(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x29).to_bytes(2, "little")
class Shlb(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x2A).to_bytes(2, "little")
class Shrb(Command):
    def get_value(self, params=None, size=4, position=0):
        return (0x2B).to_bytes(2, "little")

class Cmp(Command):
    def get_value(self, params = None, size=4, position=0):
        if isinstance(params[0], RamAddr) or isinstance(params[1], RamAddr):
            raise ValueError(f"Cannot compare memory")
        if isinstance(params[0], Immediate):
            raise ValueError(f"Cannot compare immediates to register, try swapping the operands")

        if isinstance(params[1], Immediate):
            if isinstance(params[0], Immediate):
                raise ValueError(f"Cannot compare immediate to immediate")
            
            if params[0].value == 0:
                return 0x35.to_bytes(2,"little") + params[1].value.to_bytes(size,"little")
            elif params[0].value == 1:
                return 0x36.to_bytes(2,"little") + params[1].value.to_bytes(size,"little")
            elif params[0].value == 2:
                return 0x3D.to_bytes(2,"little") + params[1].value.to_bytes(size,"little")
        
        if isinstance(params[0],Register) and isinstance(params[1],Register):
            reg1 = params[0].value
            reg2 = params[1].value

            if reg1 == 0:
                if reg2 == 1:
                    return 0x75.to_bytes(2,"little")
                elif reg2 == 2:
                    return 0x76.to_bytes(2,"little")
                else:
                    raise ValueError("Cannot compare register to itself")
            elif reg1 == 1:
                if reg2 == 2:
                    return 0x77.to_bytes(2,"little")
                elif reg2 == 0:
                    return 0x7D.to_bytes(2,"little")
                else:
                    raise ValueError("Cannot compare register to itself")
            elif reg1 == 2:
                if reg2 == 0:
                    return 0x7E.to_bytes(2,"little")
                elif reg2 == 1:
                    return 0x7F.to_bytes(2,"little")
                else:
                    raise ValueError("Cannot compare register to itself")


# Absolute Control flow
class Ajmp(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if not params[0].literal:
                raise SyntaxError("Cannot use constants/label in absolute jumps")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x30,0x00]) + self.encode_immediate(params,size)

class Ajz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if not params[0].literal:
                raise SyntaxError("Cannot use constants/label in absolute jumps")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x31,0x00]) + self.encode_immediate(params,size)

class Ajnz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if not params[0].literal:
                raise SyntaxError("Cannot use constants/label in absolute jumps")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x32,0x00]) + self.encode_immediate(params,size)

class Ajc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if not params[0].literal:
                raise SyntaxError("Cannot use constants/label in absolute jumps")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x33,0x00]) + self.encode_immediate(params,size)

class Ajnc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if not params[0].literal:
                raise SyntaxError("Cannot use constants/label in absolute jumps")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x34,0x00]) + self.encode_immediate(params,size)

# Absolute Function flow
class Ret(Command):
    def get_value(self, params=None, size=4, position=0):
        return bytes([0x37,0x00])

class Acall(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if not params[0].literal:
                raise SyntaxError("Cannot use constants/label in absolute call")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x38,0x00]) + self.encode_immediate(params,size)

class Abz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if (not params[0].literal) and not isinstance(params[0],RamAddr):
                raise SyntaxError("Cannot use label in absolute branch")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x39,0x00]) + self.encode_immediate(params,size)

class Abnz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if (not params[0].literal) and not isinstance(params[0],RamAddr):
                raise SyntaxError("Cannot use label in absolute branch")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x3A,0x00]) + self.encode_immediate(params,size)

class Abc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if (not params[0].literal) and not isinstance(params[0],RamAddr):
                raise SyntaxError("Cannot use label in absolute branch")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x3B,0x00]) + self.encode_immediate(params,size)

class Abnc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            if (not params[0].literal) and not isinstance(params[0],RamAddr):
                raise SyntaxError("Cannot use label in absolute branch")
        except IndexError:
            raise SyntaxError("Not enough parameter!")
        return bytes([0x3C,0x00]) + self.encode_immediate(params,size)

class Jmpv(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0x3F,0x00])

class Callv(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0x3E,0x00])


# Control flow
class Jmp(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative jump")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x70,0x00]) + self.encode_immediate(params,size,True)

class Jz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative jump")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x71,0x00]) + self.encode_immediate(params,size,True)

class Jnz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative jump")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x72,0x00]) + self.encode_immediate(params,size,True)

class Jc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative jump")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x73,0x00]) + self.encode_immediate(params,size,True)

class Jnc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative jump")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x74,0x00]) + self.encode_immediate(params,size,True)

# Function flow
class Ret(Command):
    def get_value(self, params=None, size=4, position=0):
        return bytes([0x37,0x00])

class Call(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative call")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x78,0x00]) + self.encode_immediate(params,size,True)

class Bz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative branch")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x79,0x00]) + self.encode_immediate(params,size,True)

class Bnz(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative branch")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x7A,0x00]) + self.encode_immediate(params,size,True)

class Bc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative branch")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x7B,0x00]) + self.encode_immediate(params,size,True)

class Bnc(Command):
    def get_value(self, params, size=4, position=0):
        try:
            params[0].value = params[0].value - position
            if params[0].literal:
                raise SyntaxError("Cannot use literal value in relative branch")
        except IndexError:
            raise SyntaxError("Not Enough Parameter")
        return bytes([0x7C,0x00]) + self.encode_immediate(params,size,True)

# Stack
class Push(Command):
    def get_value(self, params, size=4, position=0):
        if not isinstance(params[0],Register):
            raise ValueError("Must only Push to registers")
        register = params[0]
        return bytes([[0x6,0x000,0x62,0x64][register]])

class Pop(Command):
    def get_value(self, params, size=4, position=0):
        if not isinstance(params[0],Register):
            raise ValueError("Must only Pop to registers")
        register = params[0]
        return bytes([[0x6,0x001,0x63,0x65][register]])

class Pushr(Command):
    def get_value(self, params=None, size=4, position=0):
        return bytes([0x66,0x00])

class Popr(Command):
    def get_value(self, params=None, size=4, position=0):
        return bytes([0x67,0x00])

# Variable Load/Store

class Ldv(Command):
    def get_value(self, params, size=4, position=0):
        return 0x4087.to_bytes(2,byteorder="little")

class Stv(Command):
    def get_value(self, params, size=4, position=0):
        return 0x1088.to_bytes(2,byteorder="little")

class Ldvd(Command):
    def get_value(self, params, size=4, position=0):
        return 0x40B7.to_bytes(2,byteorder="little")

class Stvd(Command):
    def get_value(self, params, size=4, position=0):
        return 0x10B8.to_bytes(2,byteorder="little")

# x32
class Int(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0x80,0x00]) + self.encode_immediate(params,size)

class Intr(Command):
    def get_value(self, params, size=4, position=0):
        params = self.encode_immediate(params,size)
        return bytes([0x90,0x00]) + params

class Page(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0x9A,0x00]) + self.encode_immediate(params,size)

class Free(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0x9B,0x00]) + self.encode_immediate(params,size)

class Move(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0x9C,0x00]) + self.encode_immediate(params,size)

class Reduce(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0xA0,0x00])

class Extend(Command):
    def get_value(self, params, size=4, position=0):
        return bytes([0xA1,0x00])


class Parameter:
    def __init__(self,value=0, literal=False):
        self.literal = literal
        self.value = value
        pass

class Immediate(Parameter): # prefix %
    def __init__(self, value, literal=False):
        super().__init__(value, literal)

class Register(Parameter): # prefix $
    def __init__(self, value):
        if not (0 <= value <= 2):
            raise ValueError(f"{value} is not a valid register")
        super().__init__(value)

class RamAddr(Parameter): # no prefix
    def __init__(self, value, literal=False):
        super().__init__(value, literal)
