import serial
import json
import time
import os

# CONSTANTES
NUM_SAMPLES = 20 # numero de muestras
DIST_INI = 1 # en metros
DIST_FIN = 10 # en metros


ser = serial.Serial('/dev/ttyACM0', 115200)  # open serial port

def cleanAddr(devName):
    devName = str(devName).rpartition('TARGETDEV-')[1]+str(devName).rpartition('TARGETDEV-')[2]
    devName = devName[:len(devName) - 3]
    return devName


def cleanRssi(rssi):
    rssi = str(rssi).rpartition('2K')[2]
    rssi = rssi[:len(rssi) - 3]
    return rssi

def main():
    duration = 0.15  # seconds
    freq_ini = 750  # Hz
    freq_fin = 440

    j = DIST_INI
    while (j <= DIST_FIN):
        dataJS = []
        try:
            with open("calibrationFiles/calib_"+str(j)+"_.json", "r") as file:
                dataJS = json.load(file)
        except FileNotFoundError:
            with open("calibrationFiles/calib_"+str(j)+"_.json", "w") as file:
                json.dump(dataJS, file, indent=4)

        i = 0
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq_ini))
        while i < NUM_SAMPLES:
            # Obtenemos el valor de la direccion y el rssi del Serial Port
            ak = ser.readline()
            devName = ser.readline()
            rssiRaw = ser.readline()

            # Eliminamos los datos inútiles
            if (len(devName) > 11):  # lectura valida

                # clean data from serial port
                devName = cleanAddr(devName)
                rssiRaw = cleanRssi(rssiRaw)

                if "TARGETDEV-" in devName:  # if devName is clean and it's logical
                    # add read data to JSON
                    frame = {
                        "devName": devName,
                        "RSSI": rssiRaw
                    }
                    dataJS.append(frame)
            time.sleep(0.5)
            print('sample no. '+str(i))
            i+=1

        with open("calibrationFiles/calib_"+str(j)+"_.json", "w") as file:
            json.dump(dataJS, file, indent=4)

        j+=1
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq_fin))
        time.sleep(5)


main()




