import pynput
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
                print(key.char,end="",flush=True)
            except AttributeError:
                if key == pynput.keyboard.Key.enter:
                    print()
                    self.buffer.append(10)
                elif key == pynput.keyboard.Key.space:
                    print(" ",flush=True,end="")
                    self.buffer.append(32)
                elif key == pynput.keyboard.Key.backspace:
                    print("\x08 \x08",end="",flush=True)
                    self.buffer.append(8)

    def write(self, data:int):
        #print(f"{"Writing" if self.writemode else ""}{" and " if self.writemode and self.listen else ""}{"Listening" if self.listen else ""}",end="")
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