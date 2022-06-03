from segnale import Signal_information

class Lightpath(Signal_information):
    def __init__(self, signal_power: float, path: list[str], channel : int) -> None:
        super().__init__(signal_power, path)
        self.channel = channel
    
    def getChannel(self) -> int:
        return self.channel