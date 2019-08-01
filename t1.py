# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 15:47:04 2019

@author: jwb97
"""

import board
import busio
import math
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import PID
import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
p = GPIO.PWM(16,100)
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
SP = 0
P = 10
I = 1
D = 1

pid = PID.PID(P, I, D)
pid.SetPoint = SP
pid.setSampleTime(1)

p.start(0)

def test_pid(P = 0.2,  I = 0.0, D= 0.0, L=100):
    global SP
    global S
    global output
    
    pid.update(S)
    targetPwm = pid.output
    
    p.ChangeDutyCycle(targetPwm)

    print("Set Point=", SP, "Point Value=", S, "PWM=", targetPwm)
    
    

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

def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart

class Main():

    def __init__(self, *args, **kwargs):
        while True:
            test_pid()
            
            
