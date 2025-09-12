import sys
import threading
from collections import deque

class Port:
    def __init__(self):
        pass

    def write(self, data):
        "When the system attempts to write into the address this port is mapped to"
        return

    def read(self) -> int:
        "When the system attempts to read from the address this port is mapped to"
        return

class Device:
    def __init__(self):
        pass
    def set_port(self, register_port:object):
        pass

class SerialConsole(Device):
    def __init__(self):
        listener = threading.Thread(target=self.keyboard, daemon=True)
        listener.start()
        self.writemode = False
        self.listen = False
        self.buffer:deque[int] = deque()
        super().__init__()

    def set_port(self, register_port):
        self.port = Port()
        self.port.write = self.write
        self.port.read = self.read
        register_port(self.port)

    def keyboard(self):
        while 1:
            try:
                char = ord(sys.stdin.read(1))
            except TypeError:
                continue
            self.buffer.append(char)

    def write(self, data:int):
        print(chr(data),end="",flush=True)

    def read(self):
        try:
            return self.buffer.popleft()
        except IndexError:
            return 0

class DiskIO(Device):
    "Disk controller"
    def __init__(self):
        self.command = ""
        self.databuffer:deque
        self.sector = 0
        self.SECTORSIZE = 256 # bytes
        self.disk = open("disk.img","rb+")
        super().__init__()

    def set_port(self, register_port):
        command = Port()
        command.write = self.get_command
        data = Port()
        data.read = self.read
        status = Port()
        status.read = self.status
        register_port(command)
        register_port(data)
        register_port(status)

    def get_command(self, data:int):
        if data == 0x10:
            self.command = "SET_SECTOR"
        elif data == 0x20:
            self.command = "READ"
            self.disk.seek(self.SECTORSIZE*self.sector)
            self.databuffer = deque(self.disk.read(self.SECTORSIZE))
    
    def status(self):
        if self.command == "READ":
            return 0x20
        elif not self.command:
            return 0

    def read(self):
        try:
            if len(self.databuffer) == 1:
                self.command = ""
            return self.databuffer.popleft()
        except IndexError:
            return 0
