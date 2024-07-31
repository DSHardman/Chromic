import numpy as np
import random
import time
import serial
import imageio as iio

# NOTE THAT THE Y AXIS DOES NOT HOME AUTOMATICALLY (SINCE IT'S PLUGGED INTO THE EXTRUDER DRIVER)
# POSITION THE Y AXIS AT ITS ENDSTOP BEFORE RUNNING THIS PROGRAM

centreposition = (114, 90, 7.5)
targetforce = 3  # Maximum force in N
retractheight = 15  # How far to lift up?
step = 0.01  # Distance to move between force measurements

Ender = serial.Serial("COM4", 250000)
Forces = serial.Serial("COM17", 115200)
time.sleep(2)


def waitforposition():
    Ender.flush()
    Ender.write(str.encode("M114 R\r\n"))
    while True:
        line = Ender.readline()
        if line.find(b'Count') != -1:
            break
    return


def takereading(targetforce):
    Ender.write(str.encode("G1 Z" + str(centreposition[2]) + " F400\r\n"))
    waitforposition()
    Forces.flushInput()
    while 1:
        try:
            force = float(Forces.readline())
            break
        except ValueError:
            print("No force, trying again")
    f = open("ForceCalibration.csv", "w")
    f.write("0, "+str(force)+"\n")
    f.close()
    n = 1
    while (force < targetforce):
        Ender.write(str.encode("G1 Z" + str(centreposition[2] - n*step) + " F400\r\n"))
        waitforposition()
        Forces.flushInput()

        while 1:
            try:
                force = float(Forces.readline())
                break
            except ValueError:
                print("No force, trying again")

        f = open("ForceCalibration.csv", "a")
        f.write(str(n*step)+", " + str(force) + "\n")
        f.close()

        n += 1
        if n*step > 5:  # Do not descend further than 5 mm
            break
    # time.sleep(waittime)
    # Ender.write(str.encode("G1 Z" + str(centreposition[2] + retractheight) + " F400\r\n"))
    # waitforposition()


def setup():
    Ender.write(str.encode("M92 E80\r\n"))  # Calibrate steps for Y axis
    Ender.write(str.encode("M302 P1\r\n"))  # Allow extruder driver to run without temperature checks
    Ender.write(str.encode("G92 E0\r\n"))  # Run relative to this Y position
    Ender.write(str.encode("G28 X Y\r\n"))  # Home X
    Ender.write(str.encode("G0 E130\r\n"))  # Go to Y position for homing
    Ender.write(str.encode("G28 X Z\r\n"))  # Home Z

    Ender.write(str.encode("G1 Z"+str(centreposition[2]+retractheight)+" F400\r\n"))  # Go to starting Z position
    Ender.write(str.encode("G1 X "+str(centreposition[0])+" E "+str(centreposition[1])+" F1000\r\n"))  # Go to starting X/Y position
    waitforposition()


def main():

    waitforposition()
    takereading(targetforce)  # Press to desired force

    Ender.write(str.encode("G1 Z" + str(centreposition[2] + retractheight) + " F4000\r\n"))  # Lift up
    Ender.write(str.encode("M18\r\n"))  # Disable steppers


setup()
main()
