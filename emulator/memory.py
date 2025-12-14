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
        self.data:dict[(int,dict[(int,int)])] = {} # dict of int:frames(dict of int:int)
        self.page_to_frame:dict[(int,int)] = {}

        # frame 0xFE000 is reserved for ports
        self.allocate_page(0xFE000,0xFE000)
        self.ports:list[device.Port] = []

        self.stack_start = None
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
        self.data[frame] = {}
    
    def relocate_page(self, old_page:int, new_page:int):
        try:
            self.page_to_frame[new_page] = self.page_to_frame[old_page]
            del self.page_to_frame[old_page]
        except KeyError:
            self.allocate_page(new_page)

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
            raise pageFault
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
            frame = self.data[frame]
        except KeyError:
            raise pageFault

        try:
            return frame[address]
        except KeyError:
            return 0

    def load_quad(self, address:int, absolute=False):
        return (
            self.load(address+7,absolute) << 56 |
            self.load(address+6,absolute) << 48 |
            self.load(address+5,absolute) << 40 |
            self.load(address+4,absolute) << 32 |
            self.load(address+3,absolute) << 24 |
            self.load(address+2,absolute) << 16 |
            self.load(address+1,absolute) << 8 |
            self.load(address,absolute)
        )
    
    def store_quad(self, address:int, value:int, absolute=False):
        self.store(address,value, absolute)
        self.store(address+1,value >> 8, absolute)
        self.store(address+2,value >> 16, absolute)
        self.store(address+3,value >> 24, absolute)
        self.store(address+4,value >> 32, absolute)
        self.store(address+5,value >> 40, absolute)
        self.store(address+6,value >> 48, absolute)
        self.store(address+7,value >> 56, absolute)

    def load_double(self, address:int, absolute=False):
        return self.load(address+3,absolute) << 24 | self.load(address+2,absolute) << 16 | self.load(address+1,absolute) << 8 | self.load(address,absolute)
    
    def store_double(self, address:int, value:int, absolute=False):
        self.store(address,value, absolute)
        self.store(address+1,value >> 8, absolute)
        self.store(address+2,value >> 16, absolute)
        self.store(address+3,value >> 24, absolute)

    def load_word(self, address:int, absolute=False):
        return self.load(address+1,absolute) << 8 | self.load(address,absolute)
    
    def store_word(self, address:int, value:int, absolute=False):
        self.store(address,value, absolute)
        self.store(address+1,value >> 8, absolute)

    def get_frame(self, frame_id:int):
        try:
            return self.data[frame_id]
        except KeyError:
            return {0:0}
    
    def load_bypass_dev(self, address:int, absolute=False):
        frame, address = self.getaddr_real(address) if absolute else self.getaddr_virtual(address)

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
            try:
                frame = self.data[frame]
            except KeyError:
                raise pageFault
            frame[address] = value
        else:
            try:
                del self.data[frame][address]
            except:
                pass
