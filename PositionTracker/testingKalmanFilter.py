import numpy as np
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
import matplotlib.gridspec as gridspec

# print(gs)

delta_t = 0.1
time = 50 # seconds
max_time = int(time / delta_t)

# vector de instantes de tiempo
TIME = [i for i in range(1, max_time + 1, 1)]

# variables
#ax = ay = 0.2  # valor de aceleracion en x e y
ax = (np.random.normal(0, 5, max_time))
ay = (np.random.normal(0, 5, max_time))

u_noise = 0.018  # (accelerometer error) std
z_noise = 0.48940446  # (RSSI-Distance error) std

# MODELO IDEAL M.U.A.

x = []  # pos x
y = []  # pos y
vx = []  # vel x
vy = []  # vel y

# valores para estado inicial (t=0)
x.append(0)
y.append(0)
vx.append(0)
vy.append(0)

# generamos la trayectoria ideal usando el modelo de un M.U.A.
for t in TIME:
    x.append(x[t - 1] + (vx[t - 1] * delta_t) + ((ax[t-1] * (delta_t ** 2)) / 2))
    y.append(y[t - 1] + (vy[t - 1] * delta_t) + ((ay[t-1] * (delta_t ** 2)) / 2))
    vx.append(vx[t - 1] + (delta_t * ax[t-1]))
    vy.append(vy[t - 1] + (delta_t * ay[t-1]))

# IMPLEMENTAMOS EL KALMAN FILTER

x_est = []  # pos x
y_est = []  # pos y
vx_est = []  # vel x
vy_est = []  # vel y

x_est.append(0)
y_est.append(0)
vx_est.append(0)
vy_est.append(0)

my_filter = KalmanFilter(dim_x=4, dim_z=2)

my_filter.x = np.array([[0.],
                        [0.],
                        [0.],
                        [0.]])

my_filter.B = np.array([[(delta_t ** 2) / 2, 0],
                        [0, (delta_t ** 2) / 2],
                        [delta_t, 0],
                        [0, delta_t]])

my_filter.F = np.array([[1., 0., delta_t, 0.],
                        [0., 1., 0., delta_t],
                        [0., 0., 1., 0.],
                        [0., 0., 0., 1.]])  # state transition matrix

my_filter.H = np.array([[1., 0., 0., 0.],
                        [0., 1., 0., 0.]])  # Measurement function

my_filter.P = np.array([[100., 0., 0., 0.],
                        [0., 100., 0., 0.],
                        [0., 0., 100., 0.],
                        [0., 0., 0., 100.],
                        ])  # covariance matrix. The terms along the main diagonal of P are the variances associated with the corresponding terms
# in the state vector. The off-diagonal terms of P provide the covariances between terms in the state vector. Depends on Q matrix as well.


my_filter.Q = [[(u_noise ** 2) * ((delta_t ** 4) / 4.), 0., 0., 0.],
               [0., (u_noise ** 2) * ((delta_t ** 4) / 4.), 0., 0.],
               [0., 0., (u_noise ** 2) * (delta_t ** 2), 0.],
               [0., 0., 0., (u_noise ** 2) * (delta_t ** 2)]]  # accelerometer error (process noise)

my_filter.R = [[1. * (z_noise ** 2), 0.],
               [0., 1. * (z_noise ** 2)]]  # RSSI-distance error (measurement noise)

# Añadimos ruido a las medidas obtenidas del modelo ideal (x,y,vx,vy)

noise = np.random.multivariate_normal([0, 0, 0, 0], my_filter.Q, max_time)
noise_acc = np.random.multivariate_normal([0, 0], np.array([[u_noise ** 2, 0],
                                                              [0, u_noise ** 2]]), max_time)
noise_mea = np.random.multivariate_normal([0, 0], my_filter.R, max_time)

x_dirt_pred = []
y_dirt_pred = []
vx_dirt_pred = []
vy_dirt_pred = []
accx_dirt_pred = []
accy_dirt_pred = []

x_dirt_mea = []
y_dirt_mea = []

error_P_prior = dict()
error_P_prior['x'] = []
error_P_prior['y'] = []

error_P_post = dict()
error_P_post['x'] = []
error_P_post['y'] = []

for n in enumerate(noise):
    x_dirt_pred.append(x[n[0]] + n[1][0])
    y_dirt_pred.append(y[n[0]] + n[1][1])
    vx_dirt_pred.append(vx[n[0]] + n[1][2])
    vy_dirt_pred.append(vy[n[0]] + n[1][3])

for n in enumerate(noise_acc):
    accx_dirt_pred.append(ax[n[0]]+n[1][0])
    accy_dirt_pred.append(ay[n[0]]+n[1][1])

for n in enumerate(noise_mea):
    x_dirt_mea.append(x[n[0]] + n[1][0])
    y_dirt_mea.append(y[n[0]] + n[1][1])

for t in TIME:
    my_filter.predict(np.array([[accx_dirt_pred[t-1]],
                                [accy_dirt_pred[t-1]]]))  # utilizamos la media de las medidas de la aceleracion
    my_filter.update(np.array([[x_dirt_mea[t-1]],
                               [y_dirt_mea[t-1]]]))

    error_P_prior['x'].append(np.sqrt(my_filter.P_prior.item(0,0)))
    error_P_prior['y'].append(np.sqrt(my_filter.P_prior.item(1,1)))
    error_P_post['x'].append(np.sqrt(my_filter.P_post.item(0, 0)))
    error_P_post['y'].append(np.sqrt(my_filter.P_post.item(1, 1)))

    x_est.append(my_filter.x.item(0))
    y_est.append(my_filter.x.item(1))
    vx_est.append(my_filter.x.item(2))
    vy_est.append(my_filter.x.item(3))
# print("x: " + str(x[t]) + " x_est: " + str(x_est[t]))


fig = plt.figure(tight_layout=True)
gs = gridspec.GridSpec(2, 2)

# plots del movimiento en X respecto el tiempo

ax = fig.add_subplot(gs[0, 0])
ax.plot(TIME, x[1:], 'r-', label='x modelo ideal')
ax.plot(TIME, x_dirt_pred, 'g-', label='x modelo + ruido acelerometro')
ax.plot(TIME, x_dirt_mea, 'm-', label='x modelo + ruido RSSI-Distance')
ax.plot(TIME, x_est[1:], 'b-', label='x estimacion Kalman')
ax.set_xlabel('Time (sec*10)')
ax.set_ylabel('X position')
ax.grid()
ax.legend()

ax = fig.add_subplot(gs[0, 1])
ax.plot(TIME, y[1:], 'r-', label='y modelo ideal')
ax.plot(TIME, y_dirt_pred, 'g-', label='y modelo + ruido acelerometro')
ax.plot(TIME, y_dirt_mea, 'm-', label='y modelo + ruido RSSI-Distance')
ax.plot(TIME, y_est[1:], 'b-', label='y estimacion Kalman')
ax.set_xlabel('Time (sec*10)')
ax.set_ylabel('Y position')
ax.grid()
ax.legend()

# plots de la trayectoria

ax = fig.add_subplot(gs[1, :])
ax.plot(x, y, c='r', label='modelo ideal')
ax.plot(x_dirt_pred, y_dirt_pred, c='g', label='modelo + ruido acelerometro')
ax.plot(x_dirt_mea, y_dirt_mea, c='m', label='modelo + ruido RSSI-Distance')
ax.plot(x_est, y_est, c='b', label='estimacion Kalman')
ax.set_xlabel('X position')
ax.set_ylabel('Y position')
ax.grid()
ax.legend()

plt.show()

#plots de la matriz P

plt.title("Error covariance matrix P")
plt.subplot(1,2,1)
plt.plot(TIME, error_P_prior['x'], label="X std P_prior")
plt.plot(TIME, error_P_post['x'], label="X std P_post")
plt.legend()
plt.xlabel("Time (sec*10)")
plt.ylabel("Standard deviation")

plt.subplot(1,2,2)
plt.plot(TIME, error_P_prior['y'], label="Y std P_prior")
plt.plot(TIME, error_P_post['y'], label="Y std P_post")
plt.legend()
plt.xlabel("Time (sec*10)")
plt.ylabel("Standard deviation")
plt.show()
