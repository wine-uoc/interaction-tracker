# Description of this project

The simple_central project implements a simple Bluetooth low energy central device with GATT client functionality.
The device implementing this project will act in the role of master, allowing it to connect to a peripheral device. The peripheral device
will send out the data it takes from the VL6180X sensor to the central device via BLE. Later, the central device will keep gathering the
received data from peripheral device continuously and it will send the data to a RPI via Serial through USB.


