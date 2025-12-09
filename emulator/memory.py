import device
import color

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
        self.data:dict[(int,dict[(int,int)])] = {} # dict of int:frames(dict of int:int)
        self.page_to_frame:dict[(int,int)] = {}

        # frame 0xFE000 is reserved for ports
        self.allocate_page(0xFE000,0xFE000)
        self.ports:list[device.Port] = []
    
    def allocate_page(self, page:int, frame:int=None):
        def find_lowest_free(numbers):
            number_set = set(numbers)
            
            current_num = 0
            while current_num in number_set:
                current_num += 1
            
            return current_num
        if frame is None:
            frame = find_lowest_free(self.page_to_frame.values())

        self.page_to_frame[page] = frame
    
    def free_page(self,page:int):
        try:
            del self.page_to_frame[page]
        except KeyError:
            pass
    
    def getaddr_real(self,addr:int):
        frame = (addr & 0xFFFF_F000) >> 12
        address = addr & 0xFFF
        return frame, address

    def getaddr_virtual(self,virtualaddr:int):
        page = (virtualaddr & 0xFFFF_F000 )>> 12
        address = virtualaddr & 0xFFF
        try:
            frame = self.page_to_frame[page]
        except KeyError:
            frame = page
        return frame, address

    def register_port(self, port:device.Port):
        self.ports.append(port)

    def register_device(self,device:device.Device):
        device.set_port(self.register_port)

    def load(self, address:int, absolute=False):
        frame, address = self.getaddr_real(address) if absolute else self.getaddr_virtual(address)

        try:
            if frame == 0xFE000:
                device = self.ports[address]
                return device.read()
        except IndexError:
            pass

        try:
            return self.data[frame][address]
        except KeyError:
            return 0

    def store(self, address:int, value:int, absolute=False):
        frame, address = self.getaddr_real(address) if absolute else self.getaddr_virtual(address)
        value = value & 0xFF
        # device
        if frame == 0xFE000:
            try:
                device = self.ports[address]
                device.write(value)
                return
            except IndexError:
                pass

        if value != 0:
            if not self.data.get(frame):
                self.data[frame] = {}
            self.data[frame][address] = value
        else:
            try:
                del self.data[frame][address]
            except:
                pass
