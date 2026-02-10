from parameter import *
from dataclasses import dataclass

@dataclass
class Err:
    msg:str
    pos:int # param index
    hint:str=""

map = {}

def register(name:str,cls:"Instruction"):
    map[name] = cls

class Instruction:
    def __init__(self,args:list[BaseParameter]):
        self.args = args
    def __repr__(self):
        return f"{self.__class__.__name__}(args={self.args})"
    def get(self, pc:int, size=4) -> bytes|Err:
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
register("jmp",Jmp)

class Call(Instruction):
    def get(self, pc:int, size=4):
        if isinstance(self.args[0], Immediate): # relative
            self.args[0].value -= pc
            return b"\x78\0" + (self.args[0].get(size,True))
        if isinstance(self.args[0], Dereference): # absolute
            return b"\x38\0" + self.args[0].get(size)
register("call",Call)

class Ret(Instruction):
    def get(self, pc, size=4):
        return b"\xff\0"
register("ret",Ret)

class Halt(Instruction):
    def get(self, pc, size=4):
        return b"\x37\0"
register("halt",Halt)

class Mov(Instruction):
    def get(self, pc:int, size=4):
        dest = self.args[0]
        source = self.args[1]

        if isinstance(dest,Immediate):
            return Err("immediate is not a valid destination",0,"only register A, X, Y and memory dereference are valid")

        if isinstance(dest, Register): # load
            if isinstance(source, Immediate):
                if dest.value == 0:
                    return b"\x47\0" + source.get(size)
                elif dest.value == 1:
                    return b"\x48\0" + source.get(size)
                elif dest.value == 2:
                    return b"\x49\0" + source.get(size)
                else:
                    return Err("invalid register for loading immediate",0,"only A, X and Y accept immediate values")
            elif isinstance(source, Dereference): # store
                if self.args[0].value == 0:
                    return b"\x47\0" + source.get(size)
                if self.args[0].value == 1:
                    return b"\x48\0" + source.get(size)
                if self.args[0].value == 2:
                    return b"\x49\0" + source.get(size)
        
        return Err("?",0)
register("mov",Mov)

class Int(Instruction):
    def get(self, pc:int, size=4):
        if not isinstance(self.args[0], Immediate):
            raise SyntaxError(f"parameter of `int` must be an immediate value")
        return b"\x80\0" + self.args[0].get(size)
register("int",Int)