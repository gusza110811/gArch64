from __future__ import annotations

class Command:
    def __init__(self):
        pass

    def get_value(self, params:list["Parameter"]=None):
        return

    def encode_params(self, params:list[Parameter]) -> bytes:
        """Encode all params as 4-byte big-endian values."""
        return b''.join(p.value.to_bytes(4, "big") for p in params)

class Halt(Command):
    def get_value(self, params=None):
        return bytes([0x00])

class Mov(Command):
    def get_value(self, params = None):
        return super().get_value(params)

# Arithmetic
class Add(Command):
    def get_value(self, params=None):
        return (0x20).to_bytes(2, "big")

class Sub(Command):
    def get_value(self, params=None):
        return (0x21).to_bytes(2, "big")

class Mul(Command):
    def get_value(self, params=None):
        return (0x22).to_bytes(2, "big")

class Div(Command):
    def get_value(self, params=None):
        return (0x23).to_bytes(2, "big")

class Mod(Command):
    def get_value(self, params=None):
        return (0x28).to_bytes(2, "big")

# Bitwise logic
class And(Command):
    def get_value(self, params=None):
        return (0x24).to_bytes(2, "big")

class Or(Command):
    def get_value(self, params=None):
        return (0x25).to_bytes(2, "big")

class Xor(Command):
    def get_value(self, params=None):
        return (0x26).to_bytes(2, "big")

class Not(Command):
    def get_value(self, params=None):
        return (0x27).to_bytes(2, "big")

# Control flow
class Jmp(Command):
    def get_value(self, params):
        return bytes([0x00, 0x30]) + self.encode_params(params)

class Jz(Command):
    def get_value(self, params):
        return bytes([0x00, 0x31]) + self.encode_params(params)

class Jnz(Command):
    def get_value(self, params):
        return bytes([0x00, 0x32]) + self.encode_params(params)

class Jc(Command):
    def get_value(self, params):
        return bytes([0x00, 0x33]) + self.encode_params(params)

class Jnc(Command):
    def get_value(self, params):
        return bytes([0x00, 0x34]) + self.encode_params(params)

class Jeq(Command):
    def get_value(self, params):
        return bytes([0x00, 0x35]) + self.encode_params(params)

class Jne(Command):
    def get_value(self, params):
        return bytes([0x00, 0x36]) + self.encode_params(params)

# Function flow
class Ret(Command):
    def get_value(self, params=None):
        return bytes([0x00, 0x37])

class Call(Command):
    def get_value(self, params):
        return bytes([0x00, 0x38]) + self.encode_params(params)

class Bz(Command):
    def get_value(self, params):
        return bytes([0x00, 0x39]) + self.encode_params(params)

class Bnz(Command):
    def get_value(self, params):
        return bytes([0x00, 0x3A]) + self.encode_params(params)

class Bc(Command):
    def get_value(self, params):
        return bytes([0x00, 0x3B]) + self.encode_params(params)

class Bnc(Command):
    def get_value(self, params):
        return bytes([0x00, 0x3C]) + self.encode_params(params)

class Be(Command):
    def get_value(self, params):
        return bytes([0x00, 0x3D]) + self.encode_params(params)

class Bne(Command):
    def get_value(self, params):
        return bytes([0x00, 0x3E]) + self.encode_params(params)

# Stack
class Push(Command):
    def get_value(self, params):
        if not isinstance(params[0],Register):
            raise ValueError("Must only Push to registers")
        return bytes([0x00, 0x60]) + self.encode_params(params)

class Pop(Command):
    def get_value(self, params):
        if not isinstance(params[0],Register):
            raise ValueError("Must only Pop to registers")
        return bytes([0x00, 0x61]) + self.encode_params(params)

class Pushr(Command):
    def get_value(self, params=None):
        return bytes([0x00, 0x66])

class Popr(Command):
    def get_value(self, params=None):
        return bytes([0x00, 0x67])

# x32
class Int(Command):
    def get_value(self, params):
        return bytes([0x00, 0x80]) + self.encode_params(params)

class Sys(Command):
    def get_value(self, params):
        return bytes([0x00, 0x80]) + self.encode_params(params)

class Intr(Command):
    def get_value(self, params):
        return bytes([0x00, 0x90]) + self.encode_params(params)

class Reduce(Command):
    def get_value(self, params):
        return bytes([0x00, 0xA0]) + self.encode_params(params)

class Extend(Command):
    def get_value(self, params):
        return bytes([0x00, 0xA1]) + self.encode_params(params)


class Parameter:
    def __init__(self,value:0):
        self.value = value
        pass

class Immediate(Parameter): # prefix %
    def __init__(self, value):
        super().__init__(value)

class Register(Parameter): # prefix $
    def __init__(self, value):
        super().__init__(value)

class AbstractRegister(Register): # prefix @ ; only for STV LDV STVR and LDVR
    def __init__(self, value):
        super().__init__(value)

class CacheAddr(Parameter): # prefix *
    def __init__(self, value):
        super().__init__(value)

class RamAddr(Parameter): # no prefix
    def __init__(self, value):
        super().__init__(value)