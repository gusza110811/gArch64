import pynput
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
        listener = pynput.keyboard.Listener(on_press=self.keyboard)
        listener.start()
        self.writemode = False
        self.listen = False
        self.buffer:deque[int] = deque()
        super().__init__()

    def keyboard(self, key:pynput.keyboard.KeyCode):
        if self.listen:
            try:
                self.buffer.append(ord(key.char))
            except AttributeError:
                if key == pynput.keyboard.Key.enter:
                    self.buffer.append(10)
                elif key == pynput.keyboard.Key.space:
                    self.buffer.append(32)

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