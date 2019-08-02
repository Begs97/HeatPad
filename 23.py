# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 15:59:21 2019

@author: jwb97
"""

import matplotlib
matplotlib.use('Agg')
import board
import busio
import math
import PID
import time
import matplotlib.pyplot as plt
import numpy as np
#from scipy.interpolate import spline
from scipy.interpolate import BSpline, make_interp_spline
import RPi.GPIO as GPIO

####################  GPIO Configuration  ######################

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
p = GPIO.PWM(16,100)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#######################  ADC Configuration  #####################

# Establish communication to ADS1115
i2c = busio.I2C(board.SCL, board.SDA)

# Import ADS1115 driver and define it
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
ads = ADS.ADS1115(i2c)

# Define single ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
ads.gain = 1

############  Thermistor to Temperature Conversion  ################

def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart

###################  Push Button Callbacks  ########################

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

###################  PID Controller Configuration ###########################

SP = 20
P = 1.4
I = 1
D = 0.001
pid = PID.PID(P, I, D)

pid.SetPoint = 0.0
pid.setSampleTime(0.25)  # a second

total_sampling = 100
sampling_i = 0
measurement = 0
feedback = 0

feedback_list = []
time_list = []
setpoint_list = []

#####################  Main Loop  ###############################

print('PID controller is running..')
try:
    while 1:
        pid.SetPoint = SP
        R = ((26407 / chan0.value) - 1) * 10000
        temperature = steinhart_temperature_C(R)
        pid.update(feedback)
        output = pid.output

        if temperature is not None:
            if pid.SetPoint > 0:
                feedback += temperature + output

            print('i={0} desired.temp={1:0.1f}*C temp={2:0.1f}*C pid.out={3:0.1f} feedback={4:0.1f}'
                  .format(sampling_i, pid.SetPoint, temperature, output, feedback))
            
            elif output > 0:
                print('turn on heater')
            elif output < 0:
                print('turn on cooler')

        time.sleep(0.5)
        sampling_i += 1

        feedback_list.append(feedback)
        setpoint_list.append(pid.SetPoint)
        time_list.append(sampling_i)

        elif sampling_i >= total_sampling:
            break

except KeyboardInterrupt:
    print("exit")


print("pid controller done.")
print("generating a report...")
time_sm = np.array(time_list)
time_smooth = np.linspace(time_sm.min(), time_sm.max(), 300)
helper_x3 = make_interp_spline(time_list, feedback_list)
feedback_smooth = helper_x3(time_smooth)

fig1 = plt.gcf()
fig1.subplots_adjust(bottom=0.15, left=0.1)

plt.plot(time_smooth, feedback_smooth, color='red')
plt.plot(time_list, setpoint_list, color='blue')
plt.xlim((0, total_sampling))
plt.ylim((min(feedback_list) - 0.5, max(feedback_list) + 0.5))
plt.xlabel('time (s)')
plt.ylabel('PID (PV)')
plt.title('Temperature PID Controller')


plt.grid(True)
fig1.savefig('pid_temperature.png', dpi=100)
print("finish")
