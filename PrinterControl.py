import numpy as np
import random
import time
import serial
import csv
import imageio as iio
import matplotlib.pyplot as plt
from scipy import interpolate

# Run CalibrateForces.py if time has passed since last tests, or if setup has been changed

centreposition = (116, 86, 10)
presstime = 10  # How long to hold in position?
retractheight = 10
presentheight = 3

target_forces = np.arange(0.5, 2.5, 0.5)
target_temps = np.arange(45, 46, 1)

# Load measured forces and create interpolation function
with open('ForceCalibration.csv', 'r') as f:
    reader = csv.reader(f)
    data = list(reader)
known_forces = np.array(data, dtype=float)
getzfromforce = interpolate.interp1d(known_forces[:, 1], known_forces[:, 0])

# Connect to peripherals
Ender = serial.Serial("COM7", 250000)
Forces = serial.Serial("COM17", 115200)
time.sleep(2)
camera = iio.get_reader("<video1>")
n = 0


def waitforposition():
    Ender.flush()
    Ender.write(str.encode("M114\r\n"))
    while True:
        line = Ender.readline()
        if line.find(b'Count') != -1:
            break
    return


def setup():
    Ender.write(str.encode("M302 P1\r\n"))  # Allow extruder driver to run without temperature checks
    Ender.write(str.encode("G28\r\n"))  # Home

    Ender.write(str.encode("G1 Z"+str(centreposition[2]+retractheight)+" F400\r\n"))  # Go to starting Z position
    Ender.write(str.encode("G1 X "+str(centreposition[0])+" Y "+str(centreposition[1])+" F1000\r\n"))  # Go to starting X/Y position
    waitforposition()


setup()

# Loop through target temperatures
for i in range(len(target_temps)):
    Ender.write(str.encode("M104 S" + str(target_temps[i]) + "\r\n"))  # Set temperature
    time.sleep(120)  # Wait 2 minutes for everything to homogenise

    # Loop through target forces
    for j in range(len(target_forces)):

        Ender.write(str.encode("G1 Z" + str(centreposition[2] + retractheight) + " F400\r\n"))  # Go to starting Z position
        Ender.write(str.encode("G1 X " + str(centreposition[0]) + " Y " + str(centreposition[1]) + " F1000\r\n"))  # Go to starting X/Y position

        # Ensure printer is still close to target temperature before proceeding
        actualtemp = 0
        while np.round(actualtemp) != target_temps[i]:
            Ender.flush()
            Ender.write(str.encode("M105\r\n"))
            line = Ender.readline()
            print(line)
            if b'T:' in line and b'S' not in line:  # Makes sure only to use temperature reading lines
                colon = line.find(b'T:')  # Finds the reported temperature
                actualtemp = float(line[(colon + 2):(colon + 7)])  # Extracts temperature
                print(actualtemp)
                colon = line.find(b'B:')  # Finds the reported temperature
                bedtemp = float(line[(colon + 2):(colon + 7)])  # Extracts bed temperature

        # Go to position and wait specified time
        Ender.write(str.encode("G1 Z" + str(centreposition[2] - getzfromforce(target_forces[j])) + " F400\r\n"))
        waitforposition()
        time.sleep(presstime)

        # Get force
        Forces.flushInput()
        actualforce = float(Forces.readline())

        # Lift up and present to camera
        Ender.write(str.encode("G1 Z" + str(centreposition[2] + presentheight) + " F10000\r\n"))
        Ender.write(str.encode("G1 Y" + str(centreposition[1] + 50) + " F10000\r\n"))

        # Save photos every second for 1 minute
        t0 = time.time()
        frame = camera.get_data(n)
        n += 1
        iio.imwrite("OutputImgs/" + str(target_temps[i])+"_"+str(target_forces[j]) + '_0.png', frame)
        for t in range(1, 60, 1):
            while time.time() - t0 < t:
                pass
            frame = camera.get_data(n)
            n += 1
            iio.imwrite("OutputImgs/" + str(target_temps[i]) + "_" + str(target_forces[j]) + "_" + str(t) + '.png', frame)

        # Log actual measured force and temperature
        f = open("log.txt", "a")
        f.write(str(actualtemp) + ", " + str(actualforce) + ", " + str(bedtemp) + "\n")
        f.close()

Ender.write(str.encode("M104 S0\r\n"))   # Cooldown
Ender.write(str.encode("M18\r\n"))  # Disable steppers
