#!/usr/bin/python3

import serial, os
from serial.serialutil import SerialException
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
import fcntl
import struct
import platform
import signal
import yaml

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15],'utf-8'))
    )[20:24])

# Specify which serial ports are used by the launchpads
file = open('config.yml','r')
cfg = yaml.load(file)
SP_NAMES = []
IP_ADDR = get_ip_address('wlo1')
launchpadsInfo = []
SEND_TO_NODERED_INTERVAL = float(cfg['anchorsToNodeRED']['sending_period'])

def set_SerialPorts_ids():
    global SP_NAMES
    if len(os.listdir('serialPorts')) == 0: # custom serial ports no han sido creados aun.
        dirlist = sorted(list(filter(lambda x: (x[len(x) - 1] == '0') and ("Texas_Instruments" in x), os.listdir("/dev/serial/by-id"))))
        print(dirlist)

        for i, port in enumerate(dirlist):
            os.symlink("/dev/serial/by-id/" + port, "serialPorts/sp"+str(i))
            SP_NAMES.append("sp"+str(i))

    for sp in sorted(os.listdir('serialPorts')):
        SP_NAMES.append(sp)




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
            try:
                dataJS = json.load(file)
            except json.decoder.JSONDecodeError:
                pass

            try:
                for obj in dataJS:
                    t = req.post("http://"+IP_ADDR+":1880/query", data=obj)
            except UnboundLocalError:
                pass
        i += 1
    threading.Timer(SEND_TO_NODERED_INTERVAL, sendToNodeRed).start()


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

def readingLaunchpadData(port, baud, lp_idx):

    # LOOP READING RSSI OF LAUNCHPADS' DETECTED DEVICES AND PREPARING TO SEND THEM TO NODERED

    while True:
        # open serial port

        ser = serial.Serial('serialPorts/' + port, baud)
        devName = None
        # get launchpadId, devName and RSSI from serial port
        try:
            launchpadId = ser.readline()
        except SerialException:
            pass
        try:
            devName = ser.readline()
        except SerialException:
            pass
        try:
            rssiRaw = ser.readline()
        except SerialException:
            pass


        if (devName is not None and len(devName) > 11):  # lectura valida


            # clean data from serial port
            launchpadId = cleanLaunchpadId(launchpadId)
            devName = cleanAddr(devName)
            rssiRaw = cleanRssi(rssiRaw)


            if "TARGETDEV-" in devName:  # if devName is clean and it's logical
                # add read data to JSON
                addDataToJSON(launchpadId, devName, rssiRaw, lp_idx)

        # close serial port
        #ser.close()
        time.sleep(SEND_TO_NODERED_INTERVAL)

def removeOldFiles():
    try:
        os.remove("serialPorts/sp0")
    except FileNotFoundError:
        pass
    try:
        os.remove("serialPorts/sp1")
    except FileNotFoundError:
        pass
    try:
        os.remove("serialPorts/sp2")
    except FileNotFoundError:
        pass



def main():
    # initialize DS's
    removeOldFiles()
    set_SerialPorts_ids()
    initialize_DS()
    print(SP_NAMES)

    # Create three threads as follows

    try:
        t1 = threading.Thread(target=readingLaunchpadData, args=(SP_NAMES[0],115200,0))
        t1.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t1.start()

        t2 = threading.Thread(target=readingLaunchpadData, args=(SP_NAMES[1],115200,1))
        t2.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t2.start()

        t3 = threading.Thread(target=readingLaunchpadData, args=(SP_NAMES[2],115200,2))
        t3.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t3.start()

    except:
        print("Error: unable to start thread")

    # set a timer for sending data to NodeRED periodically
    threading.Timer(SEND_TO_NODERED_INTERVAL, sendToNodeRed).start()

    while True:
        pass



if __name__ == '__main__':
    main()
