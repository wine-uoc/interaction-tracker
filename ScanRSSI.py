import serial
import json
import requests as req
import threading
import sched
import time
import re

import unicodedata, re


def sendToNodeRed():
    with open("data_example.json", "r") as file:
        dataJS = json.load(file)
        for obj in dataJS:
            t = req.post("http://192.168.1.130:1880/query", data=obj)

        threading.Timer(5.0, sendToNodeRed).start()


ser = serial.Serial('/dev/ttyACM0', 115200)  # open serial port


def cleanAddr(addr):
    addr = str(addr).rpartition('2K')[2]
    addr = addr[:len(addr) - 3]
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


def addDataToJSON(devName, rssiRaw):

    with open("data_example.json", mode='r') as file:
        dataJS = json.load(file)

        # check if addr is already in dataJS. If not, add it
        if not addrAlreadyAdded(devName, dataJS):
            frame = {
                "devname": devName,
                "RSSI": rssiRaw
                # añadir aqui más parámetros (ToF, Microfono...)
            }

            dataJS.append(frame)

        # if yes, update associated rssi
        else:
            updateRssi(devName, rssiRaw, dataJS)

    with open("data_example.json", "w") as file:
        json.dump(dataJS, file, indent=4)

    print(dataJS)


def main():
    dataJS = list()
    threading.Timer(5.0, sendToNodeRed).start()
    with open("data_example.json", "w") as file:
        json.dump(dataJS, file, indent=4)
    while True:
        # Obtenemos el valor de la direccion y el rssi del Serial Port
        devName = ser.readline()
        rssiRaw = ser.readline()

        # Eliminamos los datos inútiles

        devName = cleanAddr(devName)
        rssiRaw = cleanRssi(rssiRaw)
        frame = {
            'devname': devName,
            'RSSI': rssiRaw
        }

        # Obtenemos el valor de la RSSI que hay en el Serial Port
        addDataToJSON(devName, rssiRaw)

    ser.close()


main()
