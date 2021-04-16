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
file = open('../../../../Data_Processing/config.yml','r')
cfg = yaml.load(file)
SP_NAMES = []
IP_ADDR = get_ip_address('wlo1')
launchpadsInfo = []
SEND_TO_NODERED_INTERVAL = float(cfg['anchorsToNodeRED']['sending_period'])

# CONSTANTES
NUM_SAMPLES = 50    # numero de muestras por cada locator y posicion (x,y)
COORD_X = 4        # PUERTA - VENTANA
COORD_Y = 5      # PUERTA - ARMARIO

# PARAMS AVISO SONORO
duration = 0.15  # seconds
freq_LAUNCH1 = 540  # Hz
freq_LAUNCH2 = 640  # Hz
freq_LAUNCH3 = 740  # Hz


def set_SerialPorts_ids():
    global SP_NAMES
    if len(os.listdir('../../../serialPorts')) == 0: # serial ports symlinks no han sido creados aun.
        dirlist = sorted(list(filter(lambda x: (x[len(x) - 1] == '0') and ("Texas_Instruments" in x), os.listdir("/dev/serial/by-id"))))
        print(dirlist)

        for i, port in enumerate(dirlist):
            custom_port_id = port[-12:-5]
            print(custom_port_id)
            os.symlink("/dev/serial/by-id/" + port, "../../../serialPorts/"+custom_port_id)
            SP_NAMES.append(custom_port_id)

    for sp in sorted(os.listdir('../../../serialPorts')):
        SP_NAMES.append(sp)




def initialize_DS():
    i = 0
    while i < len(SP_NAMES):
        lp_info = dict()
        lp_info['sp_name'] = SP_NAMES[i]
        lp_info['json_filename'] = 'detectedDevs_' + SP_NAMES[i] + '_x_'+str(COORD_X)+'_y_'+str(COORD_Y)+'_.json'

        if not os.path.exists(lp_info['json_filename']):
            with open(lp_info['json_filename'], "w") as file:
                json.dump([], file, indent=4)

        launchpadsInfo.append(lp_info)
        i += 1


def deleteContent(fName):
    with open(fName, "w"):
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


def addDataToJSON(launchpadId, devName, timestamp, rssiRaw, lp_idx):

    frame = {
        "timestamp": timestamp,
        "launchpadId": launchpadId,
        "devname": devName,
        "RSSI": rssiRaw
        # añadir aqui más parámetros (ToF, Microfono...)
    }
    with open(launchpadsInfo[lp_idx]['json_filename'], "r+") as file:
        data = json.load(file)
        data.append(frame)
        file.seek(0)
        json.dump(data, file, indent=4)

    # print(dataJS)

def validData(launchpadId, devName, rssiRaw):
    if re.fullmatch("ANC(\-)[a-z0-9]{4}", launchpadId) is None:
        return False
    elif re.fullmatch("(\-)[0-9]{2}", rssiRaw) is None:
        return False
    elif (re.fullmatch("TARGETDEV(\-)[a-z0-9]{6}", devName) is None) and (re.fullmatch("ANC(\-)[a-zA-Z0-9]{4}", devName) is None):
        return False
    else:
        return True


def readingLaunchpadData(port, baud, lp_idx):

    # LOOP READING RSSI OF LAUNCHPADS' DETECTED DEVICES AND SAVE THEM INTO A JSON
    while True:
        # open serial port

        ser = serial.Serial('../../../serialPorts/' + port, baud)
        # get launchpadId, devName and RSSI from serial port

        sample_idx = 0
        while (sample_idx <= NUM_SAMPLES):
            try:
                #All the data are only in 1 line
                serialData = ser.readline().decode()

                #split the data into 3 parts (launchpadId, devname, rssi)
                splittedData = serialData.split()
                if len(splittedData) == 4:

                    # clean data from serial port
                    launchpadId = splittedData[0].partition('2K')[2]
                    devName = splittedData[1][0:16]
                    timestamp = int(splittedData[2], 16)
                    rssiRaw = splittedData[3]

                    #check if each element fits the formatting and naming rules (using regex)
                    if validData(launchpadId, devName, rssiRaw):
                        # add read data to JSON
                        addDataToJSON(launchpadId, devName, timestamp, rssiRaw, lp_idx)
                        # sendToNodeRed(lp_idx)
                        sample_idx += 1
            except SerialException:
                print("SERIAL EXCEPTION!")
            time.sleep(0.10)
            

        # avisar que ha acabado el launchpad lp_idx
        if lp_idx == 0:
            print("End LAUNCH1!")
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq_LAUNCH1))
        elif lp_idx == 1:
            print("End LAUNCH2!")
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq_LAUNCH2))
        else:
            print("End LAUNCH3!")
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq_LAUNCH3))

        sys.exit()

def removeOldFiles():
    try:
        os.remove("../../../serialPorts/LAUNCH1")
    except FileNotFoundError:
        pass
    try:
        os.remove("../../../serialPorts/LAUNCH2")
    except FileNotFoundError:
        pass
    try:
        os.remove("../../../serialPorts/LAUNCH3")
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
        t1.daemon = False  # thread dies when main thread (only non-daemon thread) exits.
        t1.start()

        t2 = threading.Thread(target=readingLaunchpadData, args=(SP_NAMES[1],115200,1))
        t2.daemon = False  # thread dies when main thread (only non-daemon thread) exits.
        t2.start()

        t3 = threading.Thread(target=readingLaunchpadData, args=(SP_NAMES[2],115200,2))
        t3.daemon = False  # thread dies when main thread (only non-daemon thread) exits.
        t3.start()

    except:
        print("Error: unable to start thread")

    # set a timer for sending data to NodeRED periodically
    #threading.Timer(SEND_TO_NODERED_INTERVAL, sendToNodeRed).start()

    while True:
        pass



if __name__ == '__main__':
    main()
