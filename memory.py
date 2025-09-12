import device

class Cache:
    def __init__(self):
        self.data = [0] * (2**16)
        self.stackstart = 0xFEFF # grows downward to 0xF000 , but no hard limit, it can certainly go beyond 0xF000, but please do not make it happen
        self.stackaddr = 0

        self.INTstart=0xFF00
        return

    def load(self,address:int):
        return self.data[address]

    def store(self,address:int,value:int):
        self.data[address] = value

    def push(self,value:int):
        self.data[self.stackstart-self.stackaddr] = value
        self.stackaddr += 1

    def pop(self):
        self.stackaddr -= 1
        return self.data[self.stackstart-self.stackaddr]
    
    def register_int(self, id:int, target:int):
        self.store(id+self.INTstart,target)

    def find_int(self,id:int):
        return self.load(id+self.INTstart)

class Ram:
    def __init__(self):
        self.data:dict[(int,int)] = {}
        self.DEVICE_ADDRESSES = range(0xFE00_0000,0xFE00_00FF)

        self.ports:list[device.Device] = []
    
    def register_port(self, port:device.Port):
        self.ports.append(port)

    def register_device(self,device:device.Device):
        device.set_port(self.register_port)

    def load(self,address:int):
        try:
            if address in self.DEVICE_ADDRESSES:
                Id = address-0xFE00_0000
                device = self.ports[Id]
                return device.read()
        except IndexError:
            pass

        try:
            return self.data[address]
        except KeyError:
            return 0

    def store(self,address:int,value:int):
        value = value & 0xFF
        # device
        if address in self.DEVICE_ADDRESSES:
            try:
                Id = address-0xFE00_0000
                device = self.ports[Id]
                device.write(value)
                return
            except IndexError:
                pass

        if value != 0:
            self.data[address] = value
        else:
            try:
                del self.data[address]
            except:
                pass