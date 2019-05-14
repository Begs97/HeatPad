import math
import analogio

class Thermistor:
    """Thermistor driver"""

    def __init__(self, pin, series_resistor, nominal_resistance, nominal_temperature,
                 b_coefficient, *, high_side=True):
        # pylint: disable=too-many-arguments
        self.pin = analogio.AnalogIn(pin)
        self.series_resistor = series_resistor
        self.nominal_resistance = nominal_resistance
        self.nominal_temperature = nominal_temperature
        self.b_coefficient = b_coefficient
        self.high_side = high_side

    @property
    def temperature(self):
        """The temperature of the thermistor in celsius"""
        if self.high_side:
            # Thermistor connected from analog input to high logic level.
            reading = self.pin.value / 64
            reading = (1023 * self.series_resistor) / reading
            reading -= self.series_resistor
        else:
            # Thermistor connected from analog input to ground.
            reading = self.series_resistor / (65535.0/self.pin.value - 1.0)

        steinhart = reading / self.nominal_resistance  # (R/Ro)
        steinhart = math.log(steinhart)               # ln(R/Ro)
        steinhart /= self.b_coefficient                # 1/B * ln(R/Ro)
        steinhart += 1.0 / (self.nominal_temperature + 273.15)  # + (1/To)
        steinhart = 1.0 / steinhart               # Invert
        steinhart -= 273.15                       # convert to C

        return steinhart

