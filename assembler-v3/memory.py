class Memory:
    def __init__(self,parent:"Memory"=None):
        self.parent = parent
        self.root = parent is None
        self.data = {}
    
    def get(self, key:str):
        try:
            return self.data[key]
        except KeyError:
            if not self.root:
                self.parent.get(key)
            else:
                raise KeyError(f"{key} is not defined")
    
    def get_local(self, key:str):
        try:
            return self.data[key]
        except KeyError:
            return None
    
    def get_all(self):
        return self.data
    
    def set(self, key:str, value):
        self.data[key] = value