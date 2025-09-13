import sys
import threading
import os
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
        self.error = ""
        self.databuffer = deque()
        self.sector = 0
        self.SECTORSIZE = 256 # bytes
        self.disk = open("disk.img","rb+")
        super().__init__()

    def set_port(self, register_port):
        command = Port()
        command.write = self.get_command

        data = Port()
        data.read = self.read
        data.write = self.write

        status = Port()
        status.read = self.status

        register_port(command)
        register_port(data)
        register_port(status)
    
    def get_size(self,file_object):
        original_position = file_object.tell()
        file_object.seek(0, os.SEEK_END)
        size = file_object.tell()
        file_object.seek(original_position)  # Restore original position
        return size

    def get_command(self, data:int):
        if self.command:
            return

        if data == 0x10:
            self.command = "SET_SECTOR"
        elif data == 0x20:
            self.command = "READ"
            self.disk.seek(self.SECTORSIZE*self.sector)
            self.databuffer = deque(self.disk.read(self.SECTORSIZE))
        elif data == 0x21:
            self.command = "WRITE"
            self.disk.seek(self.SECTORSIZE*self.sector)


        elif data == 0x30: # error ACK
            self.error = ""
        elif data == 0xFF: # abort
            self.command = ""
            self.error = ""
            self.databuffer = deque()

        else:
            self.error = "INVALID_COMMAND"

    def status(self):
        if self.error == "INVALID_COMMAND":
            return 0x30
        elif self.error == "SECTOR_ID_TOO_LARGE":
            return 0x31


        if self.command == "READ":
            return 0x20
        elif self.command == "WRITE":
            return 0x21
        elif self.command == "SET_SECTOR":
            return 0x22
        elif not self.command:
            return 0

    def read(self):
        if self.error:
            return 0

        if self.command == "READ":
            try:
                if len(self.databuffer) == 1:
                    self.command = ""
                return self.databuffer.popleft()
            except IndexError:
                return 0
        
        else:
            return 0
    
    def write(self, data):
        if self.error:
            return

        if self.command == "WRITE":
            self.databuffer.append(data)
            if len(self.databuffer) == self.SECTORSIZE:
                self.command == ""
                self.disk.write(bytearray(self.databuffer))
        elif self.command == "SET_SECTOR":
            self.databuffer.append(data)
            if len(self.databuffer) == 4:
                self.sector = int.from_bytes(bytes(self.databuffer),byteorder="little")
                if (self.sector*self.SECTORSIZE) > self.get_size(self.disk):
                    self.error = "SECTOR_ID_TOO_LARGE"
                self.command = ""