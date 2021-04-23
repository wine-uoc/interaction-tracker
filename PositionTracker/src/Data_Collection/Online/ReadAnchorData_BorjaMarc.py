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

SP_NAMES = []
IP_ADDR = get_ip_address('wlo1')
launchpadsInfo = []
SEND_TO_NODERED_INTERVAL = 1
SERIAL_PORTS_DIR = '../serialPorts'

# Indicates the (x,y,z) positions of each anchor LAUNCH1, LAUNCH2 and LAUNCH3.
ANCHORS_POSITIONS = {
    "LAUNCH1": (1.25, 2.5, 0.5),
    "LAUNCH2": (2.0, 1.5, 0.5),
    "LAUNCH3": (3.25, 3.5, 0.5)
}

#Indicates the RSSI threshold from which greater values means <= 1m distance and lesser values means >1m distance.
THRESHOLD_RSSI = -100

def set_SerialPorts_ids():
    global SP_NAMES
    if len(os.listdir(SERIAL_PORTS_DIR)) == 0: # serial ports symlinks no han sido creados aun.
        dirlist = sorted(list(filter(lambda x: (x[len(x) - 1] == '0') and ("Texas_Instruments" in x), os.listdir("/dev/serial/by-id"))))
        print(dirlist)

        for i, port in enumerate(dirlist):
            custom_port_id = port[-12:-5]
            print(custom_port_id)
            os.symlink("/dev/serial/by-id/" + port, SERIAL_PORTS_DIR+'/'+custom_port_id)
            SP_NAMES.append(custom_port_id)

    else: 
        for sp in sorted(os.listdir(SERIAL_PORTS_DIR)):
            SP_NAMES.append(sp)




def initialize_DS():
    i = 0
    while i < len(SP_NAMES):
        lp_info = dict()
        lp_info['sp_name'] = SP_NAMES[i]
        lp_info['json_filename'] = 'output.json'#'detectedDevs_' + SP_NAMES[i] + '.json'
        lp_info['anchor_position'] = (ANCHORS_POSITIONS[SP_NAMES[i]][0], ANCHORS_POSITIONS[SP_NAMES[i]][1], ANCHORS_POSITIONS[SP_NAMES[i]][2])

        with open(lp_info['json_filename'], "w") as file:
            pass

        launchpadsInfo.append(lp_info)
        i += 1


def deleteContent(fName):
    with open(fName, "w"):
        pass


def sendToNodeRed(lp_idx):
    '''
    with open(launchpadsInfo[lp_idx]['json_filename'], "r") as file:
        try:
            dataJS = json.load(file)
        except json.decoder.JSONDecodeError:
            pass

        try:
            for obj in dataJS:
                t = req.post("http://"+IP_ADDR+":1880/posts", data=obj)
        except UnboundLocalError:
            pass

    with open(launchpadsInfo[lp_idx]['json_filename'], "w") as file:
       # deleteContent(launchpadsInfo[i]['json_filename'])
        json.dump([], file, indent=4)

    '''
    pass

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


def addPacketToJSON(packet):#, lp_idx):

    with open('output.json', 'a') as file:
        file.write(json.dumps(packet))
        file.write('\n')

    '''
    with open(launchpadsInfo[lp_idx]['json_filename'], "a") as file:
        file.write(json.dumps(packet))
        file.write('\n')
    '''

def validData(anchorMAC, beaconId, beaconMAC, RSSI):
    if re.fullmatch("[a-f0-9]{12}", anchorMAC) is None:
        return False
    if re.fullmatch("(\-)[0-9]{2}", RSSI) is None:
        return False
    if re.fullmatch("TARGETDEV(\-)[a-z0-9]{6}", beaconId) is None:
        return False
    if re.fullmatch("[a-f0-9]{12}", beaconMAC) is None:
        return False
    return True

def addColonsToMAC (mac_addr):
    return f"{mac_addr[0:2]}:{mac_addr[2:4]}:{mac_addr[4:6]}:{mac_addr[6:8]}:{mac_addr[8:10]}:{mac_addr[10:12]}"

def buildPacket(anchorMAC, beaconId, beaconMAC, RSSI, lp_idx):
    '''
    FORMATO DEL PAQUETE

    {
      "timestamp": 1618331867243,
      "beaconId": "TARGETDEV-z67b89",
      "beaconMAC": "34:F0:23:54:2A:7E",
      "anchorMAC": "A2:45:FE:13:4A:1B",
      "RSSI": -75
      "x": 1.25,
      "y": 2.50,
      "z": 2.0,
      "dx": 1.0,
      "dy": 1.0,
      "dz": 1.0
    }
    '''

    packet = dict()

    pos = launchpadsInfo[lp_idx]['anchor_position']
    timestamp = round(time.time_ns() / 1000000000, 6)
    distance = (1.0, 1.0, 1.0)

    packet['timestamp'] = timestamp
    packet['beaconId'] = beaconId
    packet['beaconMAC'] = addColonsToMAC(beaconMAC.upper())
    packet['anchorMAC'] = addColonsToMAC(anchorMAC.upper())
    packet['RSSI'] = RSSI
    packet['x'] = pos[0]
    packet['y'] = pos[1]
    packet['z'] = pos[2]
    packet['dx'] = distance[0]
    packet['dy'] = distance[1]
    packet['dz'] = distance[2]

    return packet


def readingLaunchpadData(port, baud, lp_idx):

    # LOOP READING RSSI OF LAUNCHPADS' DETECTED DEVICES AND PREPARING TO SEND THEM TO NODERED

    while True:
        # open serial port

        ser = serial.Serial(SERIAL_PORTS_DIR+ '/' + port, baud)
        # get launchpadId, devName and RSSI from serial port

        try:
            #All the data are only in 1 line
            serialData = ser.readline().decode()

            #split the data into 4 parts (anchorMAC, beaconId, beaconMAC, RSSI)
            splittedData = serialData.split()
            if len(splittedData) == 4:

                # clean data from serial port
                anchorMAC = splittedData[0].partition('2K')[2]
                beaconId = splittedData[1][0:16]
                beaconMAC = splittedData[2]
                RSSI = splittedData[3]

                #check if each element fits the formatting and naming rules (using regex)
                if validData(anchorMAC, beaconId, beaconMAC, RSSI):
                    RSSI = int(RSSI)
                    #check if RSSI is greater or equal than the threshold
                    if RSSI >= THRESHOLD_RSSI:
                        # add read data to JSON
                        packet = buildPacket(anchorMAC, beaconId, beaconMAC, RSSI, lp_idx)
                        print(packet)
                        addPacketToJSON(packet)#, lp_idx)
                        sendToNodeRed(lp_idx)

        except SerialException:
            print("SERIAL EXCEPTION!")


        # close serial port
        #ser.close()
        #time.sleep(SEND_TO_NODERED_INTERVAL)

def removeOldFiles():
    try:
        os.remove(SERIAL_PORTS_DIR+"/LAUNCH1")
    except FileNotFoundError:
        pass
    try:
        os.remove(SERIAL_PORTS_DIR+"/LAUNCH2")
    except FileNotFoundError:
        pass
    try:
        os.remove(SERIAL_PORTS_DIR+"/LAUNCH3")
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
    #threading.Timer(SEND_TO_NODERED_INTERVAL, sendToNodeRed).start()

    while True:
        pass



if __name__ == '__main__':
    main()
