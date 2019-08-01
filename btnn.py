# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 15:47:56 2019

@author: jwb97
"""

import board
import busio
import math
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Establish communication to ADS1115
i2c = busio.I2C(board.SCL, board.SDA)

# Import ADS1115 driver and define it
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
ads = ADS.ADS1115(i2c)

# Define single ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
ads.gain = 1

# Define the temperature controller variables
setpoint = 0
SP = setpoint


def increase_sp_callback(channel):
    global SP
    SP += 1
    print("increase detected")
    print("SP=", SP)

def decrease_sp_callback(channel):
    global SP
    SP -= 1
    print("decrease detected")
    print("SP=", SP)
    
GPIO.add_event_detect(22, GPIO.FALLING, callback=increase_sp_callback)
GPIO.add_event_detect(23, GPIO.FALLING, callback=decrease_sp_callback)

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.yaxis.tick_right()
xs = []
ys = []
y2 = []

# This function performs the steinhart equation
def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart

# This function is called periodically from FuncAnimation
def animate(i, xs, ys, y2):

    # Read temperature (Celsius) from the steinhart equation
    global S
    global SP
    R = ((26407 / chan0.value) - 1) * 10000
    S = steinhart_temperature_C(R)
    
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%I:%M:%S %p'))
    ys.append(S)
    y2.append(SP)

    # Limit x and y lists to 10 items
    xs = xs[-10:]
    ys = ys[-10:]
    y2 = y2[-10:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys, label='PV')
    ax.plot(xs, y2, 'r--', label='SP')    
    
    # set the limit on the y-axis
    plt.ylim(20,70)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('ADS1115 Temperature over Time')
    plt.ylabel('Temperature (deg C)')

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, y2), interval=1000)
plt.show()
    
