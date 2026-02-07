from parameter import *

class Instruction:
    def __init__(self,args:list[BaseParameter]):
        self.args = args
    def __repr__(self):
        return f"{self.__class__.__name__}(args={self.args})"
    def get(self, pc:int, size=4):
        raise NotImplementedError(f"get() not implemented for {self.__class__.__name__}")

    @classmethod
    def from_str(cls, name:str, args:list[BaseParameter]) -> "Instruction":
        if name not in map:
            raise SyntaxError(f"unknown instruction '{name}'")
        return map[name](args)

class Jmp(Instruction):
    def get(self, pc:int, size=4):
        if isinstance(self.args[0], Immediate): # relative jump
            self.args[0].value -= pc
            return b"\x70\0" + (self.args[0].get(size,True))
        if isinstance(self.args[0], Dereference): # absolute jump
            return b"\x30\0" + self.args[0].get(size)

class Mov(Instruction):
    def get(self, pc:int, size=4):
        if isinstance(self.args[0], Register): # STORE
            if isinstance(self.args[1], Immediate):
                if self.args[0].value == 0:
                    return b"\x47\0" + self.args[1].get(size)
                if self.args[0].value == 1:
                    return b"\x48\0" + self.args[1].get(size)
                if self.args[0].value == 2:
                    return b"\x49\0" + self.args[1].get(size)

class Int(Instruction):
    def get(self, pc:int, size=4):
        if not isinstance(self.args[0], Immediate):
            raise SyntaxError(f"parameter of `int` must be an immediate value")
        return b"\x80\0" + self.args[0].get(size)

map = {
    "jmp": Jmp,
    "mov": Mov,
    "int": Int,
}