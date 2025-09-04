class Cache:
    def __init__(self):
        self.data = [0] * (2**16)
        self.stackstart = 0xFF00
        self.stackaddr = 0
        return

    def load(self,address:int):
        return self.data[address]

    def store(self,address:int,value:int):
        self.data[address] = value

    def push(self,value:int):
        self.data[self.stackstart+self.stackaddr] = value
        self.stackaddr += 1
    
    def pop(self):
        self.stackaddr -= 1
        return self.data[self.stackstart+self.stackaddr]

class Ram:
    def __init__(self):
        self.data:dict[(int,int)] = {}
    
    def load(self,address:int):
        try:
            return self.data[address]
        except KeyError:
            return 0
    
    def store(self,address:int,value:int):
        if value != 0:
            self.data[address] = value
        else:
            try:
                del self.data[address]
            except:
                pass