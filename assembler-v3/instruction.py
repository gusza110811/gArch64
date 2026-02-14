from parameter import *

class Err:
    def __init__(self,
            msg:str,
            pos:int,
            hint:str="",):
        self.msg = msg
        self.pos = pos
        self.hint = hint

        if msg == "not implemented":
            self.hint += "\ncome back to writing the assembler you donkey"

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
        return b"\x37\0"
register("ret",Ret)

class Halt(Instruction):
    def get(self, pc, size=4):
        return b"\xff\0"
register("halt",Halt)

class Mov(Instruction):
    def get(self, pc:int, size=4):
        dest = self.args[0]
        source = self.args[1]

        srclength = source.length
        destlength = dest.length
        sizetochr = list("bwdq")
        if srclength is None:
            srclength = destlength
        elif destlength is None:
            destlength = srclength
        if srclength is None:
            return Err("parameter size ambiguous",0,"try adding b, w, d or q in one of the dereferences")
        if (srclength != destlength):
            if isinstance(source, Register):
                length = destlength
            elif isinstance(dest, Register):
                length = srclength
            else:
                return Err("size mismatch between source and destination",0, f"size of the two parameters are not compatible ({sizetochr[destlength]} vs {sizetochr[srclength]})")
        else:
            length = srclength

        if isinstance(dest,Immediate):
            return Err("immediate is not a valid destination",0,"only register A, X, Y and memory are valid destinations")

        elif isinstance(dest, Register):
            if isinstance(source, Immediate): # load immediate
                if dest.value == 0:
                    return b"\x47\0" + source.get(size)
                elif dest.value == 1:
                    return b"\x48\0" + source.get(size)
                elif dest.value == 2:
                    return b"\x49\0" + source.get(size)
                else:
                    return Err("invalid register for loading immediate",0,"only A, X and Y accept immediate values")
            elif isinstance(source, Dereference): # load
                addr = source.get(size)
                reg = dest.value
                if dest.value > 2:
                    return Err("invalid register for loading value",1,"only A, X and Y accept value from memory")
                return (0x81 + (length*0x10) + reg).to_bytes(2,byteorder='little') + addr
        
        elif isinstance(dest, Dereference):
            if isinstance(source, Immediate):
                return Err("cannot store immediate value to memory",1,"only register A, X and Y accept immediate values")
            if isinstance(source, Register): # store
                addr = dest.get(size)
                reg = source.value
                if source.value > 2:
                    return Err("invalid register for storing value",1,"only registers A, X and Y can be stored to memory")
                return (0x84 + (length*0x10) + reg).to_bytes(2,byteorder='little') + addr
            if isinstance(source, Dereference): # mov
                destaddr = dest.get(size)
                srcaddr = source.get(size)
                return (0x89 + (length*0x10)).to_bytes(2,byteorder='little') + destaddr + srcaddr

        return Err("not implemented",0,f"no case implemented for {type(dest)}, {type(source)}")
register("mov",Mov)

class Int(Instruction):
    def get(self, pc:int, size=4):
        if not isinstance(self.args[0], Immediate):
            raise SyntaxError(f"parameter of `int` must be an immediate value")
        return b"\x80\0" + self.args[0].get(size)
register("int",Int)