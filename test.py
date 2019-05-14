import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}".format('raw', 'v'))

while True:

    def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
     import math
     steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
     steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
     steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
     return steinhart

print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
time.sleep(0.5)
