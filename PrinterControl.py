import numpy as np
import random
import time
import serial
import csv
import imageio as iio
import matplotlib.pyplot as plt
from scipy import interpolate

# NOTE THAT THE Y AXIS DOES NOT HOME AUTOMATICALLY (SINCE IT'S PLUGGED INTO THE EXTRUDER DRIVER)
# POSITION THE Y AXIS AT ITS ENDSTOP BEFORE RUNNING THIS PROGRAM

# Run CalibrateForces.py if time has passed since last tests, or if setup has been changed

centreposition = (114, 90, 7.5)
presstime = 10  # How long to hold in position?
retractheight = 10
presentheight = 3

target_forces = np.arange(0.5, 3.0, 0.5)
target_temps = np.arange(30, 45, 1)

# Load measured forces and create interpolation function
with open('ForceCalibration.csv', 'r') as f:
    reader = csv.reader(f)
    data = list(reader)
known_forces = np.array(data, dtype=float)
plt.plot(data_array[:, 0], data_array[:, 1])
getzfromforce = interpolate.interp1d(data_array[:, 1], data_array[:, 0])

# Connect to peripherals
Ender = serial.Serial("COM4", 250000)
Forces = serial.Serial("COM17", 115200)
time.sleep(2)
camera = iio.get_reader("<video1>")


def waitforposition():
    Ender.flush()
    Ender.write(str.encode("M114\r\n"))
    while True:
        line = Ender.readline()
        if line.find(b'Count') != -1:
            break
    return


def setup():
    Ender.write(str.encode("M92 E80\r\n"))  # Calibrate steps for Y axis
    Ender.write(str.encode("M302 P1\r\n"))  # Allow extruder driver to run without temperature checks
    Ender.write(str.encode("G92 E0\r\n")) # Run relative to this Y position
    Ender.write(str.encode("G28 X Y\r\n"))  # Home X
    Ender.write(str.encode("G0 E130\r\n"))  # Go to Y position for homing
    Ender.write(str.encode("G28 X Z\r\n"))  # Home Z

    Ender.write(str.encode("G1 Z"+str(centreposition[2]+retractheight)+" F400\r\n"))  # Go to starting Z position
    Ender.write(str.encode("G1 X "+str(centreposition[0])+" E "+str(centreposition[1])+" F1000\r\n"))  # Go to starting X/Y position
    waitforposition()


setup()

# Loop through target temperatures
for i in range(len(target_temps)):
    Ender.write(str.encode("M104 S"+ string(target_temps(i)) + "\r\n"))  # Set temperature
    time.sleep(120)  # Wait 2 minutes for everything to homogenise

    # Loop through target forces
    for j in range(len(target_forces)):

        # Ensure printer is still close to target temperature before proceeding
        actualtemp = 0
        while np.round(actualtemp) != target_temps(i):
            Ender.flush()
            Ender.write(str.encode("M105\r\n"))
            line = Ender.readline()
            if out != '' and ':' in s and 'S' not in s:  # Makes sure only to use temperature reading lines
                colon = s.find('T:')  # Finds the reported temperature
                actualtemp = float(s[(colon + 2):(colon + 7)])  # Extracts temperature

        # Go to position and wait specified time
        Ender.write(str.encode("G1 Z" + str(centreposition[2] - getzfromforce(target_forces[j])) + " F400\r\n"))
        waitforposition()
        time.sleep(presstime)

        # Get force
        Forces.flushInput()
        actualforce = float(Forces.readline())

        # Lift up and present to camera
        Ender.write(str.encode("G1 Z" + str(centreposition[2] + presentheight) + " F10000\r\n"))
        Ender.write(str.encode("G1 E" + str(centreposition[1] + 50) + " F10000\r\n"))

        # Save photos every second for 30 seconds
        t0 = time.time()
        frame = camera.get_data(0)
        iio.imwrite(string(target_temps[i])+"_"+string(target_forces[j]) + '_0.png', frame)
        for t in range(1, 30, 1):
            while time.time() - t0 < t:
                pass
            frame = camera.get_data(0)
            iio.imwrite(string(target_temps[i]) + "_" + string(target_forces[j]) + "_" + string(t) + '.png', frame)

        # Log actual measured force and temperature
        f = open("log.txt", "a")
        f.write(str(actualtemp) + ", " + str(actualforce) + "\n")
        f.close()


Ender.write(str.encode("M18\r\n"))  # Disable steppers