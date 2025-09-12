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
