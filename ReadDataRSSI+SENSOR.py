import serial
import json

numSamples = 50


dataJS = list()
#Distancia maxima empírica VL6180X: 585 mm -> approx. 60 cm

ser = serial.Serial('COM11', 115200)  # open serial port
print(ser.name)         # check which port was really used
i = 0
while i < numSamples:
    # Obtenemos el valor de la distancia que hay en el Serial Port
    distRaw = ser.readline().hex()
    size = len(distRaw)
    dist = [chr(int(str(distRaw[i]+ distRaw[j]), 16)) for i,j in zip(range(38,size-2, 2), range(39, size-2, 2))]
    dist = "".join(dist)

    #Obtenemos el valor de la RSSI que hay en el Serial Port

    RSSIRaw = ser.readline().hex()
    size = len(RSSIRaw)
    RSSI = [chr(int(str(RSSIRaw[i] + RSSIRaw[j]), 16)) for i, j in zip(range(38, size - 2, 2), range(39, size - 2, 2))]
    RSSI = "".join(RSSI)

    frame = {
        "distance" : dist,
        "RSSI" : RSSI
        # añadir aqui más parámetros (ToF, Microfono...)
    }
    dataJS.append(frame)
    i += 1

ser.close()

with open("data_example.json", "w") as file:
    json.dump(dataJS, file, indent=4)

