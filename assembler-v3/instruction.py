from parameter import *

class Instruction:
    def __init__(self,args:list[BaseParameter]):
        self.args = args
    def __repr__(self):
        return f"Instruction(args={self.args})"
    def get(self,size=4):
        raise NotImplementedError(f"get() not implemented for {self.__class__.__name__}")

    @classmethod
    def from_str(cls, name:str, args:list[BaseParameter]) -> "Instruction":
        if name not in map:
            raise SyntaxError(f"unknown instruction '{name}'")
        return map[name](args)

class Mov(Instruction):
    def __repr__(self):
        return f"MovInstruction(args={self.args})"
    
    def get(self,size=4):
        if isinstance(self.args[0], Register): # STORE
            if isinstance(self.args[1], Immediate):
                if self.args[0].value == 0:
                    return b"\0\x47" + self.args[1].get(size)
                if self.args[0].value == 1:
                    return b"\0\x48" + self.args[1].get(size)
                if self.args[0].value == 2:
                    return b"\0\x49" + self.args[1].get(size)

class Int(Instruction):
    def get(self, size=4):
        if not isinstance(self.args[0], Immediate):
            raise SyntaxError(f"parameter of `int` must be an immediate value")
        return b"\0\x80" + self.args[0].get(size)

map = {
    "mov": Mov,
    "int": Int
}