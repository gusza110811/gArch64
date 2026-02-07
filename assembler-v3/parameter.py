class BaseParameter:
    def __init__(self, value: int):
        self.value = value
    
    def get(self,size:int):
        raise NotImplementedError(f"get() is not implemented for {self.__class__.__name__}")

class Immediate(BaseParameter):
    def __repr__(self):
        return f"ImmediateParameter(value={self.value})"
    
    def get(self,size=4):
        return self.value.to_bytes(size, byteorder='little')

class Register(BaseParameter):
    def __init__(self, value):
        super().__init__(value)
    def __repr__(self):
        return f"RegisterParameter(register='{self.value}')"

class Dereference(BaseParameter):
    def __init__(self, value):
        super().__init__(value)
        self.relative = False
    def __repr__(self):
        return f"DereferenceParameter(address={self.value})"
    def get(self,size=4):
        return self.value.to_bytes(size, byteorder='little')

class IndirectDereference(BaseParameter):
    def __repr__(self):
        return "IndirectDereferenceParameter()"