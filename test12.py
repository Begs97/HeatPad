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
set_point = 45
SP = set_point
#PV = S


# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
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
    R = ((26407 / chan0.value) - 1) * 10000
    S = steinhart_temperature_C(R)
    
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(S)
    y2.append(SP)

    # Limit x and y lists to 20 items
    xs = xs[-10:]
    ys = ys[-10:]
    y2 = y2[-10:]

    # set the limit on the y-axis
    plt.ylim(20,70)

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys, y2, 'r--')

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('ADS1115 Temperature over Time')
    plt.ylabel('Temperature (deg C)')

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, y2), interval=50)
plt.show()
    
