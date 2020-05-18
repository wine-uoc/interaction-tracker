import serial
import os

dirlist = list(filter(lambda x: (x[len(x) - 1] == '0') and ("Texas_Instruments" in x), os.listdir("/dev/serial/by-id")))
print(dirlist)
os.symlink("/dev/serial/by-id/"+dirlist[0], "serialPorts/sp1")
'''
ser = serial.Serial('/home/myserial2', 115200)
print(ser.name)
h = ser.readline()
print(h)
ser.close()
'''


