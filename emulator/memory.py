import device
import color

class pageFault(Exception):
    pass

class ivtOverflow(Exception):
    pass

class undefinedInt(Exception):
    pass

class Ram:
    def __init__(self):
        self.data:dict[(int,list[int])] = {} # dict of int:frames(dict of int:int)

        self.ports:list[device.Port] = []

        self.stack_start = 0
        self.stack_pos = 0

        self.int_start = None

    def push(self,value:int):
        self.store(self.stack_start-self.stack_pos,value)
        self.stack_pos += 1

    def pop_word(self):
        self.stack_pos -= 2
        return self.load_word(self.stack_start-self.stack_pos-1)

    def push_word(self,value:int):
        self.store_word(self.stack_start-self.stack_pos-1,value)
        self.stack_pos += 2

    def pop(self):
        self.stack_pos -= 1
        return self.load(self.stack_start-self.stack_pos)

    def push_double(self,value:int):
        self.store_double(self.stack_start-self.stack_pos-3,value)
        self.stack_pos += 4

    def pop_double(self):
        self.stack_pos -= 4
        return self.load_double(self.stack_start-self.stack_pos-3)

    def register_int(self, id:int, target:int):
        if id > 512:
            raise ivtOverflow

        self.store_double((id*8)+self.int_start,target)

    def find_int(self,id:int):
        addr = self.load_double((id*8)+self.int_start)

        if (addr == 0) and (id < 0x100):
            raise undefinedInt

        return addr

    def getaddr(self,virtualaddr:int):
        page = (virtualaddr & 0xFFFF_F000 )>> 12
        address = virtualaddr & 0xFFF
        if not (page in self.data.keys()):
            self.data[page] = [0]*0x1000
        return page, address

    def register_port(self, port:device.Port):
        self.ports.append(port)

    def register_device(self,device:device.Device):
        device.set_port(self.register_port)

    def load(self, address:int):
        page, address = self.getaddr(address)

        try:
            if page == 0xFE000:
                device = self.ports[address]
                return device.read()
        except IndexError:
            pass
        
        try:
            page = self.data[page]
        except KeyError:
            raise pageFault

        try:
            return page[address]
        except KeyError:
            return 0

    def load_quad(self, address:int):
        return (
            self.load(address+7) << 56 |
            self.load(address+6) << 48 |
            self.load(address+5) << 40 |
            self.load(address+4) << 32 |
            self.load(address+3) << 24 |
            self.load(address+2) << 16 |
            self.load(address+1) << 8 |
            self.load(address)
        )
    
    def store_quad(self, address:int, value:int):
        self.store(address,value,)
        self.store(address+1,value >> 8)
        self.store(address+2,value >> 16)
        self.store(address+3,value >> 24)
        self.store(address+4,value >> 32)
        self.store(address+5,value >> 40)
        self.store(address+6,value >> 48)
        self.store(address+7,value >> 56)

    def load_double(self, address:int):
        return self.load(address+3) << 24 | self.load(address+2) << 16 | self.load(address+1) << 8 | self.load(address)
    
    def store_double(self, address:int, value:int):
        self.store(address,value,)
        self.store(address+1,value >> 8)
        self.store(address+2,value >> 16)
        self.store(address+3,value >> 24)

    def load_word(self, address:int):
        return self.load(address+1) << 8 | self.load(address)
    
    def store_word(self, address:int, value:int):
        self.store(address,value,)
        self.store(address+1,value >> 8)
    
    def load_bypass_dev(self, address:int):
        page, address = self.getaddr(address)

        try:
            return self.data[page][address]
        except KeyError:
            return 0

    def store(self, address:int, value:int):

        page, address = self.getaddr(address)
        value = value & 0xFF
        #print(f"{page:5x} {address:3x} {len(self.data[page])}")
        # device
        if page == 0xFE000:
            try:
                device = self.ports[address]
                device.write(value)
                return
            except IndexError:
                pass

        try:
            page = self.data[page]
        except KeyError:
            raise pageFault
        page[address] = value
