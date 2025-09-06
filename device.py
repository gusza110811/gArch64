import keyboard
from collections import deque

class Device:
    def __init__(self):
        pass

    def write(self, data):
        return

    def read(self) -> int:
        return

class SerialConsole(Device):
    def __init__(self):
        keyboard.on_press(self.keyboard)
        self.writemode = False
        self.listen = False
        self.buffer:deque[int] = deque()
        super().__init__()

    def keyboard(self, event:keyboard.KeyboardEvent):
        if self.listen:
            key = event.name
            if len(key) == 0:
                self.buffer.append(key.encode())

    def write(self, data:int):
        # Command mode
        if not self.writemode:
            if data == 0x10: self.writemode = True
            elif data == 0x12: self.listen = True # start_listen
            elif data == 0x13: self.listen = False # stop_listen
        else:
            if data != 0:
                print(chr(data),end="")
            else:
                self.writemode = False
        return

    def read(self):
        try:
            return self.buffer.popleft()
        except IndexError:
            return 0