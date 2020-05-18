import numpy as np
from filterpy.kalman import KalmanFilter
import matplotlib.pyplot as plt
from filterpy.common import Q_discrete_white_noise
import psycopg2
import yaml

conn = psycopg2.connect(database="track", user="postgres",
                                         password="postgres", host="172.17.0.3",
                                         port="5432")
cur = conn.cursor()


dt = 1
u_noise = 0.010081 #standard deviation

my_filter = KalmanFilter(dim_x=4, dim_z=2)

my_filter.x = np.array([[0.], [0.], [0.], [0.]])
my_filter.B = np.array([[(dt ** 2) / 2], [(dt ** 2) / 2], [dt], [dt]])
my_filter.F = np.array([[1., 0., dt, 0.],
                        [0., 1., 0., dt],
                        [0., 0., 1., 0.],
                        [0., 0., 0., 1.]])  # state transition matrix

my_filter.H = np.array([[1., 0., 0., 0.],
                        [0., 1., 0., 0.]])  # Measurement function

my_filter.P = np.array([[3., 0., 0., 0.],
                        [0., 3., 0., 0.],
                        [0., 0., 3., 0.],
                        [0., 0., 0., 3.]])  # covariance matrix. The terms along the main diagonal of P are the variances associated with the corresponding terms
                                                                 # in the state vector. The off-diagonal terms of P provide the covariances between terms in the state vector

my_filter.R = [[1.*(3.**2), 0.],
               [0., 1.*(3.**2)]]  # RSSI-distance error (measurement noise)

my_filter.Q = [[(u_noise**2)*((dt**4)/4.), 0., 0., 0.],
               [0. ,(u_noise**2)*((dt**4)/4.), 0., 0.],
               [0. , 0., (u_noise**2)*(dt**2), 0.],
               [0. ,0., 0., (u_noise**2)*(dt**2)]]   # accelerometer error (process noise)


def get_some_measurement():
    return np.array([[5], [10]])


def do_something_amazing(x):
    print(x)
    print()


for i in range(0, 5, 1):
    #cur.execute("SELECT x_acc FROM sensordata WHERE devname='TARGETDEV-2vyc1v' ORDER BY id DESC LIMIT 900")
    #acc = list(map(lambda x: float(x[0]), cur.fetchall()))
    my_filter.predict(u=np.array([[float(0.3)]]))
    my_filter.update(get_some_measurement())

    # do something with the output
    x = my_filter.x

    do_something_amazing(x)

cur.execute("SELECT x_acc, y_acc FROM sensordata WHERE devname='TARGETDEV-2vyc1v' ORDER BY id DESC LIMIT 300")
data_raw = cur.fetchall()
acc_x = list(map(lambda x: float(x[0]), data_raw))
acc_y = list(map(lambda x: float(x[1]), data_raw))


plt.hist(acc_y)
plt.xlabel("X acceleration value")
plt.ylabel("Number of occurrences")

print("std: "+str(np.std(acc_y)))
plt.show()