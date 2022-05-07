class Connection:
    
    def __init__(self, input : str, output : str, signal_power : float) -> None:
        self.input = input
        self.output = output
        self.signal_power = signal_power
        self.latency = 0.0
        self.snr = 0.0
    
    def setLatency(self, latency : float) -> None:
        self.latency = latency
    
    def setSNR(self, snr : float) -> None:
        self.snr = snr