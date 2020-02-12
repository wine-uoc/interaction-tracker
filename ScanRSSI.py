import serial
import json
import requests as req
import threading
import sched
import time
import re

import unicodedata, re

# or equivalently and much more efficiently
#control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape('\\x00-\\x1f\\x7f-\\x9f'))

def remove_control_chars(s):
    return control_char_re.sub('', s)

def sendToNodeRed():
    with open("data_example.json", "r") as file:
        dataJS = json.load(file)
        for obj in dataJS:
            t = req.post("http://localhost:1880/query", data=obj)

        threading.Timer(5.0, sendToNodeRed).start()


ser = serial.Serial('/dev/ttyACM1', 115200)  # open serial port


def cleanAddr(addr):
    addr = str(addr).rpartition('2K')[2]
    addr = addr[:len(addr) - 3]
    return addr


def cleanRssi(rssi):
    rssi = str(rssi).rpartition('2K')[2]
    rssi = rssi[:len(rssi) - 3]
    return rssi


# checks if addrRaw is already in dataJS.
def addrAlreadyAdded(addrRaw, dataJS):
    for i in dataJS:
        if i['Addr'] == addrRaw:
            return True
    return False


def updateRssi(addrRaw, rssiRaw, dataJS):
    for i in dataJS:
        if i["Addr"] == addrRaw:
            i["RSSI"] = rssiRaw


def addDataToJSON(addrRaw, rssiRaw):
    print(addrRaw)
    _addrRaw = remove_control_chars(addrRaw)

    with open("data_example.json", mode='r') as file:
        dataJS = json.load(file)

        # check if addr is already in dataJS. If not, add it
        if not addrAlreadyAdded(addrRaw, dataJS):
            frame = {
                "Addr": _addrRaw,
                "RSSI": rssiRaw
                # añadir aqui más parámetros (ToF, Microfono...)
            }

            dataJS.append(frame)

        # if yes, update associated rssi
        else:
            updateRssi(_addrRaw, rssiRaw, dataJS)

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
        addrRaw = ser.readline()
        rssiRaw = ser.readline()

        # Eliminamos los datos inútiles

        addrRaw = cleanAddr(addrRaw)
        rssiRaw = cleanRssi(rssiRaw)
        frame = {
            'Addr': addrRaw,
            'RSSI': rssiRaw
        }

        # Obtenemos el valor de la RSSI que hay en el Serial Port
        addDataToJSON(addrRaw, rssiRaw)

    ser.close()


main()
