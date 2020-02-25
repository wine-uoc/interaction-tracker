import serial
import json
import requests as req
import threading
import sched
import time
import re
import sys
import glob
import serial

# Specify which serial ports are used by the launchpads
SP_NAMES = ['ttyACM0', 'ttyACM2', 'ttyACM4']
launchpadsInfo = []
""" Lists serial port names

    :raises EnvironmentError:
      On unsupported or unknown platforms
    :returns:
      A list of the serial ports available on the system
"""


def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# initialize data structures to store data related to each launchpad
def initialize_DS():
    i = 0
    while i < len(SP_NAMES):
        lp_info = dict()
        lp_info['sp_name'] = SP_NAMES[i]
        lp_info['json_filename'] = 'detectedDevs_' + SP_NAMES[i] + '.json'
        # lp_info['json_data'] = [] creo que no es necesaria

        with open(lp_info['json_filename'], "w") as file:
            json.dump([], file, indent=4)

        launchpadsInfo.append(lp_info)
        i += 1


def sendToNodeRed():
    i = 0
    while i < len(SP_NAMES):
        with open(launchpadsInfo[i]['json_filename'], "r") as file:
            dataJS = json.load(file)
            for obj in dataJS:
                t = req.post("http://192.168.0.120:1880/query", data=obj)
        i += 1
    threading.Timer(5.0, sendToNodeRed).start()


def cleanAddr(addr):
    addr = str(addr).rpartition('TARGETDEV-')[1]+str(addr).rpartition('TARGETDEV-')[2]
    addr = addr[:len(addr) - 3]
    print(addr)
    return addr


def cleanRssi(rssi):
    rssi = str(rssi).rpartition('2K')[2]
    rssi = rssi[:len(rssi) - 3]
    return rssi


# checks if addrRaw is already in dataJS.
def addrAlreadyAdded(devName, dataJS):
    for i in dataJS:
        if i['devname'] == devName:
            return True
    return False


def updateRssi(devName, rssiRaw, dataJS):
    for i in dataJS:
        if i["devname"] == devName:
            i["RSSI"] = rssiRaw


def addDataToJSON(devName, rssiRaw, lp_idx):
    with open(launchpadsInfo[lp_idx]['json_filename'], mode='r') as file:
        dataJS = json.load(file)

        # check if addr is already in dataJS. If not, add it
        if not addrAlreadyAdded(devName, dataJS):
            frame = {
                "launchpadId": launchpadsInfo[lp_idx]['sp_name'],
                "devname": devName,
                "RSSI": rssiRaw
                # añadir aqui más parámetros (ToF, Microfono...)
            }
            dataJS.append(frame)

        # if yes, update associated rssi
        else:
            updateRssi(devName, rssiRaw, dataJS)

    with open(launchpadsInfo[lp_idx]['json_filename'], "w") as file:
        json.dump(dataJS, file, indent=4)

    print(dataJS)


def main():
    # initialize DS's

    initialize_DS()

    # set a timer for sending data to NodeRED periodically
    threading.Timer(5.0, sendToNodeRed).start()

    while True:
        i = 0
        while i < len(SP_NAMES):
            # open serial port
            ser = serial.Serial('/dev/' + launchpadsInfo[i]['sp_name'], 115200)

            # get devName and rssi from serial port
            devName = ser.readline()
            rssiRaw = ser.readline()

            if (len(devName) > 11): #lectura valida

                # clean data from serial port
                devName = cleanAddr(devName)
                rssiRaw = cleanRssi(rssiRaw)

                if "TARGETDEV-" in devName: #if devName is clean and it's logical
                    # add read data to JSON
                    addDataToJSON(devName, rssiRaw, i)

            # close serial port
            ser.close()
            i += 1


if __name__ == '__main__':
    main()
