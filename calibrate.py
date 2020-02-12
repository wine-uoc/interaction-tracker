import serial
import json

# CONSTANTES
TARGET_ADDR = '0x5C45F7F6E79C' #DIRECCION DEL DISPOSITIVO QUE QUEREMOS CALIBRAR
NUM_SAMPLES = 50 # numero de muestras
DIST = 4 # en metros

ser = serial.Serial('COM11', 115200)  # open serial port

def cleanAddr (addr) :
    addr = str(addr).rpartition('2K')[2]
    addr = addr[:len(addr) - 3]
    return addr

def cleanRssi (rssi) :
    rssi = str(rssi).rpartition('2K')[2]
    rssi = rssi[:len(rssi) - 3]
    return rssi


def main():
    dataJS = []

    try:

        with open("calib_data_"+str(DIST)+".json", "r") as file:
            dataJS = json.load(file)

    except FileNotFoundError:

        with open("calib_data_"+str(DIST)+".json", "w") as file:
            json.dump(dataJS, file, indent=4)

    i = 0

    while i < NUM_SAMPLES:
        # Obtenemos el valor de la direccion y el rssi del Serial Port
        addrRaw = ser.readline()
        rssiRaw = ser.readline()

        # Eliminamos los datos inútiles

        addrRaw = cleanAddr(addrRaw)
        rssiRaw = cleanRssi(rssiRaw)

        # Guardamos el valor de la RSSI  a la distancia escogida del dispositivo adecuado
        if addrRaw == TARGET_ADDR:
            frame = {
                "RSSI": rssiRaw,
                "dist": DIST
            }
            dataJS.append(frame)
            i += 1
            print(i)

    with open("calib_data_"+str(DIST)+".json", "w") as file:
        json.dump(dataJS, file, indent=4)
    ser.close()

main()




