import time
import math
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
thermistor = AnalogIn(ads, ADS.P0)


def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
    import math
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart


while True:
    R = ((26407 / thermistor.value) - 1) * 10000
    S = steinhart_temperature_C(R)
    print('ADC =', thermistor.value, 'Temp = ', format(S, '.2f), 'Resistance = ', format(R, '.2f'))
    time.sleep(.5)
  

    
