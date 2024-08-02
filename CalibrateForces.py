import time
import serial

centreposition = (116, 86, 10)
targetforce = 3  # Maximum force in N
retractheight = 15  # How far to lift up?
step = 0.01  # Distance to move between force measurements

Ender = serial.Serial("COM7", 250000)
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
    Ender.write(str.encode("M302 P1\r\n"))  # Allow extruder driver to run without temperature checks
    Ender.write(str.encode("G28\r\n"))

    Ender.write(str.encode("G1 Z"+str(centreposition[2]+retractheight)+" F400\r\n"))  # Go to starting Z position
    Ender.write(str.encode("G1 X "+str(centreposition[0])+" Y "+str(centreposition[1])+" F1000\r\n"))  # Go to starting X/Y position
    waitforposition()


def main():

    waitforposition()
    takereading(targetforce)  # Press to desired force

    Ender.write(str.encode("G1 Z" + str(centreposition[2] + retractheight) + " F4000\r\n"))  # Lift up
    Ender.write(str.encode("M18\r\n"))  # Disable steppers


setup()
main()
