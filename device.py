import sys
import threading
from collections import deque

class Device:
    def __init__(self):
        pass

    def write(self, data):
        "When the system attempts to write into the address this device is mapped to"
        return

    def read(self) -> int:
        "When the system attempts to read from the address this device is mapped to"
        return

class SerialConsole(Device):
    def __init__(self):
        listener = threading.Thread(target=self.keyboard)
        listener.start()
        self.writemode = False
        self.listen = False
        self.buffer:deque[int] = deque()
        super().__init__()

    def keyboard(self):
        while 1:
            char = ord(sys.stdin.read(1))
            if self.listen:
                self.buffer.append(char)

    def write(self, data:int):
        # Command mode
        if not self.writemode:
            if data == 0x10: self.writemode = True
            elif data == 0x12: self.listen = True # start_listen
            elif data == 0x13: self.listen = False # stop_listen
        else:
            if data != 0:
                print(chr(data),end="",flush=True)
            else:
                self.writemode = False
        return

    def read(self):
        try:
            return self.buffer.popleft()
        except IndexError:
            return 0