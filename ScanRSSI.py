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
import socket
import socket
import fcntl
import struct


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15],'utf-8'))
    )[20:24])


# Specify which serial ports are used by the launchpads
SP_NAMES = ['ttyACM0', 'ttyACM1', 'ttyACM4']
IP_ADDR = get_ip_address('wlo1')
launchpadsInfo = []
TIMER = 2.0


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
                t = req.post("http://"+IP_ADDR+":1880/query", data=obj)
        i += 1
    threading.Timer(TIMER, sendToNodeRed).start()


def cleanAddr(addr):
    addr = str(addr).rpartition('TARGETDEV-')[1]+str(addr).rpartition('TARGETDEV-')[2]
    addr = addr[:len(addr) - 3]
    return addr


def cleanRssi(rssi):
    rssi = str(rssi).rpartition('2K')[2]
    rssi = rssi[:len(rssi) - 3]
    return rssi

def cleanLaunchpadId(lp_id):
    lp_id = str(lp_id).rpartition('2K')[2]
    lp_id = lp_id[:len(lp_id) - 3]
    return lp_id


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


def addDataToJSON(launchpadId, devName, rssiRaw, lp_idx):
    with open(launchpadsInfo[lp_idx]['json_filename'], mode='r') as file:
        dataJS = json.load(file)

        # check if addr is already in dataJS. If not, add it
        if not addrAlreadyAdded(devName, dataJS):
            frame = {
                "launchpadId": launchpadId,
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

def readingLaunchpadData():

    # LOOP READING RSSI OF LAUNCHPADS' DETECTED DEVICES AND PREPARING TO SEND THEM TO NODERED
    i = 0
    while i < len(SP_NAMES):
        # open serial port
        ser = serial.Serial('/dev/' + launchpadsInfo[i]['sp_name'], 115200)

        # get launchpadId, devName and RSSI from serial port
        launchpadId = ser.readline()
        devName = ser.readline()
        rssiRaw = ser.readline()

        if (len(devName) > 11):  # lectura valida

            # clean data from serial port
            launchpadId = cleanLaunchpadId(launchpadId)
            devName = cleanAddr(devName)
            rssiRaw = cleanRssi(rssiRaw)

            if "TARGETDEV-" in devName:  # if devName is clean and it's logical
                # add read data to JSON

                addDataToJSON(launchpadId, devName, rssiRaw, i)

        # close serial port
        ser.close()
        i += 1

def main():
    # initialize DS's

    initialize_DS()

    # set a timer for sending data to NodeRED periodically
    threading.Timer(TIMER, sendToNodeRed).start()

    while True:
        # every TIMER secs, read data from Launchpads is sent to NodeRED
        readingLaunchpadData()
        time.sleep(0.5)





if __name__ == '__main__':
    main()
