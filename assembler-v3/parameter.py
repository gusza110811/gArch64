class BaseParameter:
    def __init__(self, value: int, length=2):
        self.value = value
        self.length= length
        "bytes, in powers of twos"
    
    def get(self,size:int):
        raise NotImplementedError(f"get() is not implemented for {self.__class__.__name__}")

class Immediate(BaseParameter):
    def __repr__(self):
        return f"ImmediateParameter(self.value)"
    
    def get(self,size=4,signed=False):
        return self.value.to_bytes(size, byteorder='little', signed=signed)

class Register(BaseParameter):
    def __init__(self, value, length=2):
        super().__init__(value, length)
    def __repr__(self):
        return f"RegisterParameter({self.value})"

class Dereference(BaseParameter):
    def __init__(self, value:int, length:int):
        super().__init__(value)
        self.length = length
    def __repr__(self):
        return f"DereferenceParameter({self.value})"
    def get(self,size=4):
        return self.value.to_bytes(size, byteorder='little')

class IndirectDereference(BaseParameter):
    def __init__(self, value, length, offset):
        super().__init__(value)
        self.length = length
        self.offset = offset
    def __repr__(self):
        return f"IndirectDereferenceParameter(*{self.value}+{self.offset})"