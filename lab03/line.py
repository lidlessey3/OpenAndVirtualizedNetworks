from typing import TYPE_CHECKING
from segnale import Signal_information

if TYPE_CHECKING:
    from node import Node


class Line:

    def __init__(self, label, length) -> None:
        self.label = label
        self.length = length
        self.successive = {}
        self.state = True

    def connect(self, begin, end) :
        self.successive["begin"] = begin
        self.successive["end"] = end

    def noise_generation(self, signal_power : float) -> float:
        return 1e-9 * signal_power * self.length

    def latency_generation(self) -> float:
        speed = 2/3 * 3 * 10**8
        return self.length / speed

    def propagate(self, signal : Signal_information):
        signal.inc_noise_pow(self.noise_generation(signal.get_signal_pow()))
        signal.inc_latency(self.latency_generation())
        self.successive["end"].propagate(signal)

    def occupy(self) -> bool:
        if(self.state):
            self.state = False
            return True
        return False

    def free(self) -> None:
        if (not self.state):
            self.state = True
