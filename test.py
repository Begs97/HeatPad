import numpy as np
import time
import math
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
GPIO.setup(12, GPIO.OUT)
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use('fivethirtyeight')

fig = plt.figure()
ax = plt.axes(xlim=(0, 10), ylim=(0, 70))
line, = ax.plot([], [], lw=3)

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
thermistor = AnalogIn(ads, ADS.P0)

p = GPIO.PWM(12, 50)  # channel=12 frequency=50Hz
p.start(50)
# p.ChangeDutyCycle(dc)
# p.ChangeFrequency(freq)

def init():
    line.set_data([], [])
    return line

def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart

def animate(i):
    x = np.linspace(0, 4, 1000)
    y = S
    line.set_data(x, y)
    return line
    
    plt.xlabel('Time (S)')
    plt.ylabel('Temperature (C)')
    plt.title('Heating Pad')
    
ani = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=200, interval=1000, blit=True)

plt.show()

while True:
    R = ((26407 / thermistor.value) - 1) * 10000
    S = steinhart_temperature_C(R)
    print('ADC =', thermistor.value, 'Temp = ', format(S, '.2f'), 'Resistance = ', format(R, '.2f'))
    time.sleep(.5)
  
    
