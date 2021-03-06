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

# Set Pins 17, 22, 23, and 27 as inputs for the pushbuttons
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

#################  Push Button Callbacks  #####################

increment_mode = 1
IM = "^"
        
def cb17(channel):
    print("GPIO 17 Detected")
        
def increase_sp_callback(channel):
    global SP
    global increment_mode
    if SP >= 69:
        print("Set Point is at max value")
        print("SP=", SP)
    elif increment_mode == 1:
        SP += 1
        print("increase detected")
        print("SP=", SP)
    elif increment_mode == 2:
        SP += .1
        print("increase detected")
        print("SP=", SP)
    elif increment_mode == 3:
        SP += .01
        print("increase detected")
        print("SP=", SP)

def decrease_sp_callback(channel):
    global SP
    global increment_mode
    if SP <= 20:
        print("Set Point is at minimum value")
        print("SP=", SP)
    elif increment_mode == 1:
        SP -= 1
        print("decrease detected")
        print("SP=", SP)
    elif increment_mode == 2:
        SP -= .1
        print("decrease detected")
        print("SP=", SP)
    elif increment_mode == 3:
        SP -= .01
        print("decrease detected")
        print("SP=", SP)

def cb27(channel):
    global increment_mode
    global IM
    if increment_mode == 1:
        increment_mode = 2
        IM = "    ^"
        print("Increment Mode Changed to 0.10")
    elif increment_mode == 2:
        increment_mode = 3
        IM = "     ^"
        print("Increment Mode Changed to 0.01")
    elif increment_mode == 3:
        increment_mode = 1
        IM = "^"
        print("Increment Mode Changed to 1.00")

GPIO.add_event_detect(17, GPIO.FALLING, callback=cb17)
GPIO.add_event_detect(22, GPIO.FALLING, callback=increase_sp_callback)
GPIO.add_event_detect(23, GPIO.FALLING, callback=decrease_sp_callback)
GPIO.add_event_detect(27, GPIO.FALLING, callback=cb27)

################  Create Figure for Plotting  #################

x_len = 200
y_range = [20, 50]

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.yaxis.tick_right()
xs = list(range(0, 200))
ys = [0] * x_len
y2 = [0] * x_len
ax.set_ylim(y_range)

# Set the text size for x and y ticks
matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('ytick', labelsize=12)

#################### Style for Plotting #######################

LARGE_FONT= ("Verdana", 12)
SMALL_FONT= ("Helvetica", 10)
style.use("ggplot")

###################  Animation Function  ######################

def animate(i, xs, ys, y2):
    # Convert thermistor resistance to temperature for the point value
    R = ((26407 / chan0.value) - 1) * 10000
    PV = steinhart_temperature_C(R)
    
    # Update PID values SP, PV, OP
    pid.SetPoint = SP
    pid.update(PV)
    OP = pid.output
    OP = max(min( int(OP), 100 ),0)
    
    # Start the output of the PID controller
    p.start(OP)
    
    #Create two Lines
    line, = ax.plot(xs, ys)
    line2, = ax.plot(xs, y2)    
    
    # Add y and y2 to lists
    ys.append(PV)
    y2.append(SP)
    ys = ys[-x_len:]
    y2 = y2[-x_len:]
    
    line.set_ydata(ys)
    line2.set_ydata(y2)
        
    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys, '-b', label='PV = %.2f\u2103' %PV)
    ax.plot(xs, y2, 'r--', label='SP = %.2f\u2103' %SP)
    ax.plot([],[],' ', label='          %s' %IM)
    ax.legend(framealpha=1, frameon=True, loc = 'upper left', fontsize=12)
    
    # Format plot
    #plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Heat Pad Controller', fontsize=18)
    plt.ylabel("Temperature \u2103", fontsize=16)
    
    return(line, line2)

##############  PID Controller Configuration #################

SP = 20
P = 85
I = 0
D = 0.005
pid = PID.PID(P, I, D)

pid.SetPoint = SP
pid.setSampleTime(0.25)  # a second

pointvalue_list = []
setpoint_list = []
time_list = []

#####################  Main Loop  ############################

class HeatPadapp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        # Set the Title, Icon, and zoom the window for linux
        tk.Tk.wm_title(self, "Heat Pad Controller")
        #tk.Tk.iconbitmap(self, '@HeatPadIcon.xbm')
        #tk.Tk.attributes(self, '-zoomed')
        tk.Tk.geometry(self, "720x480")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)
        
    def show_frame(self, cont):
        
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button = ttk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree))
        button3.pack()

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Temperature", font=LARGE_FONT)
        label.grid(pady=10,padx=10,row=0,column=1)
        button1 = ttk.Button(self, text="Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(pady=2,padx=5,row=6,column=1)

        button2 = ttk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.grid(pady=2,padx=5,row=7,column=1)
        

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page One",
                            command=lambda: controller.show_frame(PageOne))
        button2.pack()


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        #label = tk.Label(self, text="PV:", font=LARGE_FONT)
        #label.pack(pady=2,padx=2)
        
        #label1 = tk.Label(self, text="HeLLo", font=LARGE_FONT)
        #label1.pack(pady=2,padx=2)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(side=tk.BOTTOM)
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)       
      
###############################################################

print('PID controller is running..')
    
# Print the PID values
#print("Target: %.1f C | Current: %.1f C | PWM: %s %%"%(SP, PV, OP))

###############################################################

app = HeatPadapp()
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, y2), interval=50, blit=True)
app.mainloop()
GPIO.cleanup()

