import numpy as np
import random
import time
import serial

## NOTE THAT THE Y AXIS DOES NOT HOME AUTOMATICALLY (SINCE IT'S PLUGGED INTO THE EXTRUDER DRIVER)
## POSITION THE Y AXIS AT ITS ENDSTOP BEFORE RUNNING THIS PROGRAM
## Script currently assumes that temperature is set manually

centreposition = (43.6, 19.6, 12)
targetforce = 0.3  # In N
waittime = 5  # How long to hold in position?

retractheight = 15  # How far to lift up?
step = 0.05  # Distance to move between force measurements

Ender = serial.Serial("COM10", 115200)
Forces = serial.Serial("COM9", 115200)
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
    n = 1
    while (force < targetforce):
        Ender.write(str.encode("G1 Z" + str(Cornerposition[2] - n*step) + " F400\r\n"))
        waitforposition()
        Forces.flushInput()

        while 1:
            try:
                force = float(Forces.readline())
                break
            except ValueError:
                print("No force, trying again")
        n += 1
        if n*step > 5:  # Do not descend further than 5 mm
            break
    time.sleep(waittime)
    Ender.write(str.encode("G1 Z" + str(Cornerposition[2] + retractheight) + " F400\r\n"))
    waitforposition()

def setup():
    Ender.write(str.encode("M92 E80\r\n"))  # Calibrate steps for Y axis
    Ender.write(str.encode("M302 P1\r\n"))  # Allow extruder driver to run without temperature checks
    Ender.write(str.encode("G92 E0\r\n")) # Run relative to this Y position
    Ender.write(str.encode("G0 E30\r\n"))  # Go to Y position for homing
    Ender.write(str.encode("G28 X Z\r\n"))  # Home X & Z axes

    Ender.write(str.encode("G1 Z"+str(centreposition[2]+retractheight)+" F400\r\n"))  # Go to starting Z position
    Ender.write(str.encode("G1 X "+str(centreposition[0])+" E "+str(centreposition[1])+" F1000\r\n"))  # Go to starting X/Y position
    waitforposition()

def main():

    x = 0  # Desired offsets from centre
    y = 0
    Ender.write(str.encode("G1 X "+str(centreposition[0]+x)+" E "+str(centreposition[1]+y)+" F800\r\n"))
    waitforposition()
    takereading(targetforce)  # Press to desired force
    time.sleep(waittime)  # Wait for desired time
    Ender.write(str.encode("G1 Z" + str(centreposition[2] + retractheight) + " F400\r\n"))  # Lift up

setup()
main()