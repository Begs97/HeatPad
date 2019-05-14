import time
import math
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

thermistor = AnalogIn(ads, ADS.P0)
R = 10000 / (65535/thermistor.value - 1)

while True:
    
        steinhart = math.log(R / 10000) / 3950      # log(R/Ro) / beta
        steinhart += 1.0 / (25 + 273.15)         # log(R/Ro) / beta + 1/To
        steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
        Print ("Steinhart=", steinhart)
        time.sleep(0.5)
