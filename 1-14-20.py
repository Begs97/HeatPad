###############################################################
#                    HeatPad Controller V2                    #
#                      By Joseph Begley                       #
###############################################################

#######################   Libraries  ##########################

import board
import busio
import math
import PID
import time
import datetime as dt
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
import numpy as np
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from scipy.interpolate import make_interp_spline
from tkinter import *
import tkinter as tk
from tkinter import ttk
import threading

####################  GPIO Configuration  #####################

# Set GPIO to broadcom numbering and ignore warnings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Set PWM on pin 12 with a frequency of 100 Hz
GPIO.setup(12, GPIO.OUT)
p = GPIO.PWM(12,100)

# Set Pins 22 & 23 as inputs for the pushbuttons
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#####################  ADC Configuration  #####################

# Establish communication to ADS1115
i2c = busio.I2C(board.SCL, board.SDA)

# Define the ADS1115 driver
ads = ADS.ADS1115(i2c)

# Define single ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
ads.gain = 1

##########  Thermistor to Temperature Conversion  #############

def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart

def get_PV():
    # Read temperature (Celsius) from the steinhart equation
    R = ((26407 / chan0.value) - 1) * 10000
    PV = steinhart_temperature_C(R)

#################  Push Button Callbacks  #####################

def increase_sp_callback(channel):
    global SP
    if SP == 69:
        print("Set Point is at max value")
        print("SP=", SP)
    else:
        SP += 1
        print("increase detected")
        print("SP=", SP)

def decrease_sp_callback(channel):
    global SP
    if SP == 20:
        print("Set Point is at minimum value")
        print("SP=", SP)
    else:   
        SP -= 1
        print("decrease detected")
        print("SP=", SP)
    
GPIO.add_event_detect(22, GPIO.FALLING, callback=increase_sp_callback)
GPIO.add_event_detect(23, GPIO.FALLING, callback=decrease_sp_callback)


################  Create Figure for Plotting  #################

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.yaxis.tick_right()
xs = []
ys = []
y2 = []

#################### Style for Plotting #######################

LARGE_FONT= ("Verdana", 12)
SMALL_FONT= ("Helvetica", 10)
style.use("ggplot")

###################  Animation Function  ######################

def animate(i, xs, ys, y2):    
    
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%I:%M:%S %p'))
    ys.append(PV)
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
    

##############  PID Controller Configuration #################

SP = 20
P = 1.2
I = 2
D = 0.005
pid = PID.PID(P, I, D)

pid.SetPoint = SP
pid.setSampleTime(0.25)  # a second

pointvalue_list = []
setpoint_list = []
time_list = []

#####################  Main Loop  ############################
 


###############################################################


print('PID controller is running..')
    
# Convert thermistor resistance to temperature for the point value and update the PID
pid.SetPoint = SP
R = ((26407 / chan0.value) - 1) * 10000
PV = steinhart_temperature_C(R)
pid.update(PV)
    
# Define the PID output as an integer between 0-100 for PWM
OP = pid.output
OP = max(min( int(OP), 100 ),0)
    
# Start the PWM output 
p.start(OP)
time.sleep(0.5)
    
# Show the animated plot created for the PID
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, y2), interval=1000)
plt.show()

# Print the PID values
print("Target: %.1f C | Current: %.1f C | PWM: %s %%"%(SP, PV, OP))

# Update the animation lists
pointvalue_list.append(PV)
setpoint_list.append(SP)
#time_list.append(sampling_i)


######################################

