import typing

class Command:
    def __init__(self,emulator:"em.Emulator"):
        self.emulator = emulator

if typing.TYPE_CHECKING:
    import emulator as em