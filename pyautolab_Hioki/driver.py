import pyautolab.api as api
from serial import Serial
from typing_extensions import Literal

_DISPLAY = {True: ":DISP ON", False: ":DISP OFF"}
_MEASURE_OUTPUT_AUTO = {True: ":MEAS:OUTP:AUTO ON", False: "MEAS:OUTP:AUTO OFF"}
_MODE = {"LCR": ":MODE LCR", "CONTINUOUS": ":MODE CONT"}
_SPEED = {"FAST": ":SPEE FAST", "MEDIUM": ":SPEE MED", "SLOW": ":SPEE SLOW", "SLOW2": ":SPEE SLOW2"}
_TRIGGER_EXTERNAL = {True: ":TRIG EXT", False: ":TRIG INT"}
PARAMETERS = {
    "OFF": "OFF",
    "Z    (Impedance)": "Z",
    "Y    (Admittance)": "Y",
    "θ    (Phase angle)": "PHASE",
    "X    (Reactance)": "X",
    "G    (Conductance)": "G",
    "B    (Susceptance)": "B",
    "Q    (Q-factor)": "Q",
    "Rdc  (DC resistance)": "RDC",
    "Rs   (Equivalent series resistance)": "RS",
    "Rp   (Equivalent parallel resistance)": "RP",
    "Ls   (Equivalent series inductance)": "LS",
    "Lp   (Equivalent parallel inductance)": "LP",
    "Cs   (Equivalent series Capacitance)": "CS",
    "Cp   (Equivalent parallel capacitance)": "CP",
    "D    (Loss factor tanδ)": "D",
    "σ    (Conductivity)": "S",
    "ε    (Permittivity)": "E",
}
_UNITS = {
    "OFF": "",
    "Z": "Ω",
    "Y": "S",
    "PHASE": "°",
    "X": "Ω",
    "G": "S",
    "B": "S",
    "Q": "",
    "RDC": "Ω",
    "RS": "Ω",
    "RP": "Ω",
    "LS": "H",
    "LP": "H",
    "CS": "F",
    "CP": "F",
    "D": "",
    "S": "",
    "E": "",
}
_MONITOR_INFO = {"AC V monitor": "V", "AC I monitor": "A", "DC V monitor": "V", "DC I monitor": "I"}


class _IM3536Serial(Serial):
    def __init__(self) -> None:
        super().__init__(timeout=0)
        self._delimiter = "\r\n"

    def send_message(self, message: str) -> None:
        self.write(bytes(message + self._delimiter, "utf-8"))

    def receive_message(self) -> str:
        return self.readline().decode("utf-8").strip().rstrip()

    def send_query_message(self, message: str) -> str:
        self.send_message(message)
        return self.receive_message()


class IM3536(api.Device):
    PORT_FILTER = ""

    def __init__(self) -> None:
        super().__init__()
        self._ser = _IM3536Serial()
        self._output_auto = False
        self._is_monitor = False
        self._cache_parameters = []

    def open(self) -> None:
        self._ser.port = self.port
        self._ser.baudrate = self.baudrate
        self._ser.timeout = 0.1
        self._ser.open()
        self.set_enable_trigger_external(True)

    def close(self) -> None:
        if self._ser.is_open:
            self.set_enable_trigger_external(False)
            self.set_enable_measure_output_auto(False)
            self.set_enable_display_monitor(True)
        self._ser.close()

    def receive(self) -> str:
        return self._ser.receive_message()

    def send(self, message: str) -> None:
        self._ser.send_message(message)

    def reset_buffer(self) -> None:
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

    def set_enable_monitor_value(self, enable) -> None:
        self._is_monitor = enable

    def set_parameters(self, parameters: tuple[str, str, str, str]) -> None:
        commands = [f":PAR{i+1} {param}" for i, param in enumerate(parameters)]
        self._ser.send_message(";".join(commands))

    def get_parameters(self) -> dict[str, str]:
        results = {}
        for i in range(4):
            parameter = self._ser.send_query_message(f":PAR{i+1}?")
            results[parameter] = _UNITS[parameter]
        if self._is_monitor:
            results.update(_MONITOR_INFO)
        results.pop("OFF", None)
        self._cache_parameters = [parameter for parameter, _ in results.items()]
        return results

    def get_frequency(self) -> float:
        return float(self._ser.send_query_message(":FREQ?"))

    def set_frequency(self, frequency: float) -> None:
        self._ser.send_message(f":FREQ {frequency}")

    def trigger(self) -> None:
        return self._ser.send_message("*TRG")

    def measure(self) -> dict[str, float]:
        self.trigger()
        text = self._ser.receive_message() if self._output_auto else self._ser.send_query_message("MEAS?")
        measurements = [float(elem) for elem in text.split(",")]
        if self._is_monitor:
            measurements += self.get_monitor_values()
        if len(self._cache_parameters) == 0:
            self.get_parameters()
        parameters = self._cache_parameters
        return {param: value for param, value in zip(parameters, measurements)}

    def reset_current_settings(self) -> None:
        self._ser.send_message(":PRES")

    def reset_all(self) -> None:
        self._ser.send_message("*RST")

    def get_monitor_values(self) -> list[float]:
        values = self._ser.send_query_message(":MONI?").split(",")
        return [float(value) for value in values]

    def set_enable_trigger_external(self, is_enable: bool) -> None:
        self._ser.send_message(_TRIGGER_EXTERNAL[is_enable])

    def set_mode(self, mode: Literal["LCR", "CONTINUOUS"]) -> None:
        self._ser.send_message(_MODE[mode])

    def set_enable_measure_output_auto(self, is_enable: bool) -> None:
        self._ser.send_message(_MEASURE_OUTPUT_AUTO[is_enable])
        self._output_auto = is_enable

    def set_enable_display_monitor(self, is_enable: bool) -> None:
        self._ser.send_message(_DISPLAY[is_enable])

    def set_speed(self, mode: Literal["FAST", "MEDIUM", "SLOW", "SLOW2"]) -> None:
        self._ser.send_message(_SPEED[mode])
