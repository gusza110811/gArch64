class Cache:
    def __init__(self):
        self.data = [0] * (2**16)
        return

    def load(self,address:int):
        return self.data[address]
    
    def store(self,address:int,value:int):
        self.data[address] = value

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