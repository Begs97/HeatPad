# HeatPad

This code was written in Python for a Raspberry Pi 3 B+ with 2.8" Adafruit Capacitive Touch Screen.  The Rpi has Raspbian Stretch Version 8 installed.  The code could easily be modified for other applications.

The Rpi is set to boot directly into the Tkinter GUI via autostart using a .desktop file.

The Tkinter GUI provides an interface to the supplied PID controller plotting the set point and point value on a Matplotlib graph.

The output of the PID controller is 0 - 100% PWM at a default 100Hz frequency this is used to control the gate of a MOSFET allowing current to flow through a heating pad.  The temperature is read back with a 10k NTC thermistor.  The thermistor is connected to an ADS1115 16-bit ADC. The ADC counts are converted to resistance and then to temperature with use of the Steinhart equation.


