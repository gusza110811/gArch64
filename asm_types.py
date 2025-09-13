from __future__ import annotations

class Command:
    def __init__(self):
        pass

    def get_value(self, params:list["Parameter"]=None) -> bytes:
        return

    def encode_immediate(self, params:list[Parameter], size=4) -> bytes:
        """Encode all params as little-endian byte values."""
        return b''.join(p.value.to_bytes(size, "little") for p in params)

class Halt(Command):
    def get_value(self, params=None, size=4):
        return bytes([0x00,0x00])

class Mov(Command):
    def get_value(self, params = None, size=4) -> bytes:
        if len(params) < 2:
            raise SyntaxError("Not enough parameters")
        if len(params) > 2:
            raise SyntaxError("Too many parameters")
        destination = params[0]
        source = params[-1]
        if isinstance(destination,Immediate):
            raise ValueError("Can't store value to an immediate value")
        if isinstance(source,CacheAddr) and isinstance(destination,RamAddr):
            raise ValueError("Can't directly copy from cache to ram")
        if isinstance(source,RamAddr) and isinstance(destination,CacheAddr):
            raise ValueError("Can't directly copy from ram to cache")
        if isinstance(source,Immediate) and isinstance(destination,RamAddr):
            raise ValueError("Can't directly store immediate value to ram")
        if isinstance(source,Immediate) and isinstance(destination,CacheAddr):
            raise ValueError("Can't directly store immediate value to cache")

        # Load
        if isinstance(destination,Register) and isinstance(source,CacheAddr):
            return (0x10 + destination.value).to_bytes(2,"little") + source.value.to_bytes(size,byteorder="little")
        # Store
        elif isinstance(destination,CacheAddr) and isinstance(source,Register):
            return (0x13 + source.value).to_bytes(2,"little") + destination.value.to_bytes(size,byteorder="little")
        # MOV
        elif isinstance(destination,CacheAddr) and isinstance(source,CacheAddr):
            return 0x16.to_bytes(2,"little") + self.encode_immediate([destination,source],size)
        # Load ram
        if isinstance(destination,Register) and isinstance(source,RamAddr):
            return (0x81 + destination.value).to_bytes(2,"little") + source.value.to_bytes(size,byteorder="little")
        # Store ram
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

# Arithmetic
class Add(Command):
    def get_value(self, params=None, size=4):
        return (0x20).to_bytes(2, "little")

class Sub(Command):
    def get_value(self, params=None, size=4):
        return (0x21).to_bytes(2, "little")

class Mul(Command):
    def get_value(self, params=None, size=4):
        return (0x22).to_bytes(2, "little")

class Div(Command):
    def get_value(self, params=None, size=4):
        return (0x23).to_bytes(2, "little")

class Mod(Command):
    def get_value(self, params=None, size=4):
        return (0x28).to_bytes(2, "little")

# Bitwise logic
class And(Command):
    def get_value(self, params=None, size=4):
        return (0x24).to_bytes(2, "little")

class Or(Command):
    def get_value(self, params=None, size=4):
        return (0x25).to_bytes(2, "little")

class Xor(Command):
    def get_value(self, params=None, size=4):
        return (0x26).to_bytes(2, "little")

class Not(Command):
    def get_value(self, params=None, size=4):
        return (0x27).to_bytes(2, "little")

class Shl(Command):
    def get_value(self, params=None, size=4):
        return (0x28).to_bytes(2, "little")
class Shr(Command):
    def get_value(self, params=None, size=4):
        return (0x29).to_bytes(2, "little")
class Shlb(Command):
    def get_value(self, params=None, size=4):
        return (0x2A).to_bytes(2, "little")
class Shrb(Command):
    def get_value(self, params=None, size=4):
        return (0x2B).to_bytes(2, "little")

# Control flow
class Jmp(Command):
    def get_value(self, params, size=4):
        return bytes([0x30,0x00]) + self.encode_immediate(params,size)

class Jz(Command):
    def get_value(self, params, size=4):
        return bytes([0x31,0x00]) + self.encode_immediate(params,size)

class Jnz(Command):
    def get_value(self, params, size=4):
        return bytes([0x32,0x00]) + self.encode_immediate(params,size)

class Jc(Command):
    def get_value(self, params, size=4):
        return bytes([0x33,0x00]) + self.encode_immediate(params,size)

class Jnc(Command):
    def get_value(self, params, size=4):
        return bytes([0x34,0x00]) + self.encode_immediate(params,size)

class Jeq(Command):
    def get_value(self, params, size=4):
        return bytes([0x35,0x00]) + self.encode_immediate(params,size)

class Jne(Command):
    def get_value(self, params, size=4):
        return bytes([0x36,0x00]) + self.encode_immediate(params,size)

# Function flow
class Ret(Command):
    def get_value(self, params=None, size=4):
        return bytes([0x37,0x00])

class Call(Command):
    def get_value(self, params, size=4):
        return bytes([0x38,0x00]) + self.encode_immediate(params,size)

class Bz(Command):
    def get_value(self, params, size=4):
        return bytes([0x39,0x00]) + self.encode_immediate(params,size)

class Bnz(Command):
    def get_value(self, params, size=4):
        return bytes([0x3A,0x00]) + self.encode_immediate(params,size)

class Bc(Command):
    def get_value(self, params, size=4):
        return bytes([0x3B,0x00]) + self.encode_immediate(params,size)

class Bnc(Command):
    def get_value(self, params, size=4):
        return bytes([0x3C,0x00]) + self.encode_immediate(params,size)

class Beq(Command):
    def get_value(self, params, size=4):
        return bytes([0x3D,0x00]) + self.encode_immediate(params,size)

class Bne(Command):
    def get_value(self, params, size=4):
        return bytes([0x3E,0x00]) + self.encode_immediate(params,size)

# Stack
class Push(Command):
    def get_value(self, params, size=4):
        if not isinstance(params[0],Register):
            raise ValueError("Must only Push to registers")
        register = params[0]
        return bytes([[0x6,0x000,0x62,0x64][register]])

class Pop(Command):
    def get_value(self, params, size=4):
        if not isinstance(params[0],Register):
            raise ValueError("Must only Pop to registers")
        register = params[0]
        return bytes([[0x6,0x001,0x63,0x65][register]])

class Pushr(Command):
    def get_value(self, params=None, size=4):
        return bytes([0x66,0x00])

class Popr(Command):
    def get_value(self, params=None, size=4):
        return bytes([0x67,0x00])

# Variable Load/Store
class Ldv(Command):
    def get_value(self, params, size=4):
        return 0x17.to_bytes(2,byteorder="little")

class Ldvr(Command):
    def get_value(self, params, size=4):
        return 0x87.to_bytes(2,byteorder="little")

class Stv(Command):
    def get_value(self, params, size=4):
        return 0x18.to_bytes(2,byteorder="little")

class Stvr(Command):
    def get_value(self, params, size=4):
        return 0x88.to_bytes(2,byteorder="little")

# x32
class Int(Command):
    def get_value(self, params, size=4):
        return bytes([0x80,0x00]) + self.encode_immediate(params,size)

class Intr(Command):
    def get_value(self, params, size=4):
        return bytes([0x90,0x00]) + self.encode_immediate(params,size)

class Reduce(Command):
    def get_value(self, params, size=4):
        return bytes([0xA0,0x00])

class Extend(Command):
    def get_value(self, params, size=4):
        return bytes([0xA1,0x00])


class Parameter:
    def __init__(self,value:0):
        self.value:int = value
        pass

class Immediate(Parameter): # prefix %
    def __init__(self, value):
        super().__init__(value)

class Register(Parameter): # prefix $
    def __init__(self, value):
        super().__init__(value)

class CacheAddr(Parameter): # prefix *
    def __init__(self, value):
        super().__init__(value)

class RamAddr(Parameter): # no prefix
    def __init__(self, value):
        super().__init__(value)