import time

from scipy.stats import mode
from accessDB import DB
import numpy as np
from scipy.optimize import fsolve, minimize
from itertools import combinations
from sympy.solvers import solve
from sympy import Symbol
from sympy.solvers import linsolve
from sympy.geometry.ellipse import Circle
from sympy.geometry.polygon import Point, Triangle
from sympy.geometry.line import Segment2D
from filterpy.kalman import KalmanFilter
import yaml

file = open('config.yml', 'r')
cfg = yaml.load(file)

NUM_RESULTS_RSSI = int(cfg['pythonApp']['numResultsDBrssi'])
NUM_RESULTS_ACCEL = int(cfg['pythonApp']['numResultsDBaccel'])
NUM_RESULTS_ORIENT = int(cfg['pythonApp']['numResultsDBorient'])
NUM_ROWS_KEPT_DB = int(cfg['pythonApp']['lastMillisDBKept'])
ACC_THRESHOLD = float(cfg['pythonApp']['accThreshold'])


class ModelController:

    # initialize Anchor and Device classes
    def __init__(self):
        self.db_manager = DB()

    def initialize(self, form_data):
        """
        Initialize all the DS used in this class: launchpads and devices lists
        """
        self.launchpads = []
        self.devices = []
        self.target_devices = []
        self.plot_settings = PlotSettings(float(form_data['roomInfo']['X_min']),
                                          float(form_data['roomInfo']['X_max']),
                                          float(form_data['roomInfo']['Y_min']),
                                          float(form_data['roomInfo']['Y_max']))

        # set Anchor data from form_data
        for anc in form_data['anchorsInfo']:
            name = form_data['anchorsInfo'][anc]['name']
            X = float(form_data['anchorsInfo'][anc]['X'])
            Y = float(form_data['anchorsInfo'][anc]['Y'])
            a = Anchor(name, X, Y)
            self.launchpads.append(a)

        # retrieve Devices data from DB
        for devname in self.db_manager.getDevicesList():
            d = Device(devname)
            self.devices.append(d)

        # Initializes PositioningComputations object. This will do all positions and distance computations.
        self.model = PositioningComputations([anc.getName() for anc in self.launchpads],
                                             [dev.getDevName() for dev in self.devices],
                                             form_data['roomInfo']['orientation'])
        # Get devices initial orientation.
        """
        devs_orientation = dict()
        for dev in self.devices:
            x_ori = self.db_manager.getOrientationValues(dev.getDevName(), NUM_RESULTS_ORIENT)
            devs_orientation[dev.getDevName()] = x_ori

        self.model.setDevicesInitialOrientation(devs_orientation)
        """

    # returns launchpads positions (dictionary of anchors with dictionary of positions for each one)
    def getLaunchpadPositions(self):
        result = dict()
        for anc in self.launchpads:
            result[anc.getName()] = dict()
            result[anc.getName()]['X'] = anc.getX()
            result[anc.getName()]['Y'] = anc.getY()
        return result

    def getAnchorsPositions(self, anchors, non_target_pos):
        result = dict()
        for anc in anchors:
            result[anc] = dict()
            if len(anc) != 4:  # Anchor is a cell
                result[anc]['X'] = non_target_pos[0]
                result[anc]['Y'] = non_target_pos[1]
            else:  # Anchor is a launchpad
                x, y = self.getLaunchpadPosition(anc)
                result[anc]['X'] = x
                result[anc]['Y'] = y

        return result

    # returns a 2-tuple (X, Y) representing the position of anchor anchor_name
    def getLaunchpadPosition(self, anchor_name):
        for anc in self.launchpads:
            if anc.getName() == anchor_name:
                return anc.getX(), anc.getY()

    # returns the value of the distance from anchor (launchpad or device) anchor_name to device device_name
    def getRadiusFromAnchorToDevice(self, anchor_name, device_name):

        if len(anchor_name) != 8:  # Anchor is a cell
            rssi_list = self.db_manager.getRssiOfDeviceFromDevice(device_name, anchor_name,
                                                                  num_results=NUM_RESULTS_RSSI)
        else:  # Anchor is a launchpad
            rssi_list = self.db_manager.getRssiOfDeviceFromLaunchpad(device_name, anchor_name,
                                                                     num_results=NUM_RESULTS_RSSI)
        rssi_list = [int(np.mean(rssi_list))]
        return self.model.calculateDistanceAnchorToDevice(rssi_list, device_name)

    # returns the value of the RSSI from anchor anchor_name of device device_name
    def getRssiFromLaunchpadOfDevice(self, anchor_name, device_name):
        rssi_list = self.db_manager.getRssiOfDeviceFromLaunchpad(device_name, anchor_name, num_results=NUM_RESULTS_RSSI)
        rssi_mean = np.mean(rssi_list)
        return int(rssi_mean)

    # returns a dictionary with 3 keys. Keys are anchor names and values are the distances from this anchor to the device.
    def getRadiiFromLaunchpadsToDevice(self, devname):
        result = dict()
        for anc in self.launchpads:
            result[anc.getName()] = self.getRadiusFromAnchorToDevice(anc.getName(), devname)
        return result

    def getRadiiToTargetDevice(self, target_devname, anchors_names):
        result = dict()
        for anc in anchors_names:
            result[anc] = self.getRadiusFromAnchorToDevice(anc, target_devname)
        return result

    def getDevicePosition(self, dev):
        return dev.getPosition()

    def getDevicesPositions(self):
        result = dict()

        for dev in self.devices:
            self.getDevicePosition(dev)
            result[dev.getDevName()] = dict()
            pos = dev.getPosition()
            result[dev.getDevName()]['X'] = pos[0]
            result[dev.getDevName()]['Y'] = pos[1]

        return result

    def getDevicesList(self):
        return [self.devices[i].devname for i in self.devices]

    def isTarget(self, devname):
        for d in self.devices:
            if d.getDevName() == devname:
                return d.isTarget()
        return False

    def computeDevicesPositions(self):
        # using the anchors position and the radius for each circle they describe,
        # we can compute the position of the device devname

        # weight for devices positions estimations (using only the 3 launchpads)
        W = 1.0

        # first of all, devices positions must be computed using ONLY the 3 real anchors
        est_init_dev_pos = dict()  #est_init_dev_pos contains a dictionary whose keys are device names and values are 2-tuples (x,y)
        for dev in self.devices:
            radii_to_dev = self.getRadiiFromLaunchpadsToDevice(dev.getDevName())
            launchpads_pos = self.getLaunchpadPositions()
            pos = self.model.calculatePosition(launchpads_pos, radii_to_dev)
            est_init_dev_pos[dev.getDevName()] = pos

        # create a set and fill it with the launchpads
        S = set([lp.getName() for lp in self.launchpads])

        # for each device to position (target)
        for dev in self.devices:

            # est_pos takes position estimations of "dev".
            est_pos = [0, 0]

            # then, for each non target device, a new position estimation will be computed for device "dev" using
            # these non target devices as an anchor, one at a time.

            #variable contador de numero de posiciones estimadas para cada "dev" (target)
            count = 0

            #for each device different from the target
            for non_target_devname in [d.getDevName() for d in self.devices if d.getDevName() != dev.getDevName()]:

                # add to S one of the non target devices,
                S.add(non_target_devname)
                # get the combination of anchor-anchor-non_target_dev
                comb = list(list(combinations(S, 3)))
                # calcularemos las posiciones estimadas para "dev". Una estimacion para cada terna de "comb"

                for c in comb:
                    if not all(map(lambda x: len(x) == 8,c)):
                        count += 1
                        radius_dict = self.getRadiiToTargetDevice(dev.getDevName(), c)
                        anchors_positions_dict = self.getAnchorsPositions(c, est_init_dev_pos[non_target_devname])
                        target_pos = self.model.calculatePosition(anchors_positions_dict, radius_dict)
                        est_pos[0] += target_pos[0]
                        est_pos[1] += target_pos[1]

                S.discard(non_target_devname)

                #dividiremos est_pos entre el numero de posiciones estimadas para sacar la posicion media.
            if count != 0:
                est_pos[0] /= count
                est_pos[1] /= count


            #final estimated position of device "dev"
            pos = []
            pos.append(W*est_init_dev_pos[dev.getDevName()][0] + (1-W)*est_pos[0])
            pos.append(W*est_init_dev_pos[dev.getDevName()][1] + (1-W)*est_pos[1])
            dev.setPosition(pos)


    def getDevice(self, devname):
        for dev in self.devices:
            if dev.getDevName() == devname:
                return dev
        return None

    def getRoomXMin(self):
        return self.plot_settings.getXMin()

    def getRoomXMax(self):
        return self.plot_settings.getXMax()

    def getRoomYMin(self):
        return self.plot_settings.getYMin()

    def getRoomYMax(self):
        return self.plot_settings.getYMax()

    def isShowCircles(self):
        return self.plot_settings.isShowCircles()

    def setShowCircles(self, show_circles):
        self.plot_settings.setShowCircles(show_circles)

    def triggerDeleteFromDBoldestData(self):
        self.db_manager.keepLastXResultsInDB(NUM_ROWS_KEPT_DB)


class PositioningComputations:

    # implements Kalman Filter
    def __init__(self, anchors, devices, room_ori):

        # log-distance path loss model parameters
        self.count = 0
        self.A = cfg['pythonApp']['A']
        self.n = cfg['pythonApp']['n']
        self.initial_devs_orientation = dict()
        # necessary information
        self.anchor_names = anchors
        self.device_names = devices
        self.kalman_enabled = False
        self.room_orientation = room_ori

        self.last_position_x = None
        self.last_position_y = None

        # data needed to filter small variations of RSSI when target is not moving.
        self.last_rssi_means = dict()
        self.last_rssi_std = dict()
        self.S = cfg['pythonApp'][
            'sensitivityToRSSIChanges']  # sensitivity to changes in RSSI. Lower values, more sensitivity

        # how much rssi receives the anchor (when scanning) from devices (when advertising) at 1 meter.
        self.rssi_to_dev_at_1m = {'TARGETDEV-g5mpwl': -50} #'TARGETDEV-mom1qo': -46

        for anc_name in self.anchor_names:
            self.last_rssi_means[anc_name] = dict()
            self.last_rssi_std[anc_name] = dict()
            for dev_name in self.device_names:
                self.last_rssi_means[anc_name][dev_name] = 0
                self.last_rssi_std[anc_name][dev_name] = 0

        # data needed to implement Kalman Filter
        self.delta_t = cfg['pythonApp']['delta_t']
        self.u_noise = cfg['pythonApp']['u_noise']  # (accelerometer error) std
        self.z_noise = cfg['pythonApp']['z_noise']  # (RSSI-Distance error) std

        self.state_var = np.array([[0.], [0.], [0.], [0.]])
        self.my_filter = KalmanFilter(dim_x=4, dim_z=2)

        self.my_filter.x = np.array([[0.],
                                     [0.],
                                     [0.],
                                     [0.]])

        self.my_filter.B = np.array([[(self.delta_t ** 2) / 2, 0],
                                     [0, (self.delta_t ** 2) / 2],
                                     [self.delta_t, 0],
                                     [0, self.delta_t]])

        self.my_filter.F = np.array([[1., 0., self.delta_t, 0.],
                                     [0., 1., 0., self.delta_t],
                                     [0., 0., 1., 0.],
                                     [0., 0., 0., 1.]])  # state transition matrix

        self.my_filter.H = np.array([[1., 0., 0., 0.],
                                     [0., 1., 0., 0.]])  # Measurement function

        self.my_filter.P = np.array([[100., 0., 0., 0.],
                                     [0., 100., 0., 0.],
                                     [0., 0., 100., 0.],
                                     [0., 0., 0., 100.],
                                     ])  # covariance matrix. The terms along the main diagonal of P are the variances associated with the corresponding terms
        # in the state vector. The off-diagonal terms of P provide the covariances between terms in the state vector. Depends on Q matrix as well.

        self.my_filter.Q = [[(self.u_noise ** 2) * ((self.delta_t ** 4) / 4.), 0., 0., 0.],
                            [0., (self.u_noise ** 2) * ((self.delta_t ** 4) / 4.), 0., 0.],
                            [0., 0., (self.u_noise ** 2) * (self.delta_t ** 2), 0.],
                            [0., 0., 0.,
                             (self.u_noise ** 2) * (self.delta_t ** 2)]]  # accelerometer error (process noise)

        self.my_filter.R = [[1. * (self.z_noise ** 2), 0.],
                            [0., 1. * (self.z_noise ** 2)]]  # RSSI-distance error (measurement noise)

    def get_A(self):
        return self.A

    def get_n(self):
        return self.n

    def set_A(self, a):
        self.A = a

    def set_n(self, n):
        self.n = n

    def euclideanDistance(self, x1, y1, x2, y2):
        return np.sqrt(pow(x1 - x2, 2.0) + pow(y1 - y2, 2.0))

    # calcula la nueva distancia de una anchor a un device si esta nueva distancia
    # es mayor que la anterior +- st.deviation. Si no, devuelve la distancia del estado anterior.
    def calculateDistance(self, rssi_list, anchor_name, device_name):

        # Si no se han inicializado aun las DS de ultima lectura, la inicializamos
        if self.last_rssi_means[anchor_name][device_name] == 0:
            rssi_mean = np.mean(rssi_list)
            rssi_std = np.std(rssi_list)
            self.last_rssi_means[anchor_name][device_name] = rssi_mean
            self.last_rssi_std[anchor_name][device_name] = rssi_std

        last_rssi_mean = self.last_rssi_means[anchor_name][device_name]
        last_rssi_std = self.last_rssi_std[anchor_name][device_name]
        current_rssi_mean = np.mean(rssi_list)
        current_rssi_std = self.S * np.std(rssi_list)

        # Si la nueva RSSI esta entre la anterior rssi + std y anterior rssi - std,
        # entendemos como que no se mueve el movil.
        if last_rssi_mean + last_rssi_std > current_rssi_mean > last_rssi_mean - last_rssi_std:
            return np.power(10, (last_rssi_mean - self.A) / (-10 * self.n))

        else:  # si no, el movil se ha movido y actualizamos la distancia anterior con la actual
            self.last_rssi_means[anchor_name][device_name] = current_rssi_mean
            self.last_rssi_std[anchor_name][device_name] = current_rssi_std
            return np.power(10, (current_rssi_mean - self.A) / (-10 * self.n))

    def calculateDistanceAnchorToDevice(self, rssi_list, device_name):
        A = self.rssi_to_dev_at_1m[device_name]
        return np.mean(list(map(lambda x: np.power(10, (x - A) / (-10 * self.n)), rssi_list)))

    # applies the Kalman Filter. position and acceleration are passed to function (z and u respectively).
    def estimatePosition(self, pos, acc_x, acc_y, curr_orientation, devname):

        # Computes the orientation of the device in order to
        # move it on the right direction.
        ori_x = self.initial_devs_orientation[devname]
        d_theta = ori_x - curr_orientation

        if d_theta > np.pi:
            d_theta = d_theta - 2 * np.pi
        elif d_theta < -np.pi:
            d_theta = d_theta + 2 * np.pi

        rotationMatrix = np.array([[np.cos(self.room_orientation), -np.sin(self.room_orientation)],
                                   [np.sin(self.room_orientation), np.cos(self.room_orientation)]])

        real_acc = np.matmul(rotationMatrix, np.array([[acc_x],
                                                       [acc_y]]))

        dev_stopped = False

        # Filter small acceleration when device is static
        if np.sqrt(real_acc[0][0] ** 2 + real_acc[1][0] ** 2) < ACC_THRESHOLD:
            real_acc[0][0] = real_acc[1][0] = 0
            dev_stopped = True

       # print(real_acc)
       # print()

        # Device is not moving
        if dev_stopped:
            if self.kalman_enabled:
                self.kalman_enabled = False
                self.last_position_x = None
                self.last_position_y = None
            print("Kalman disabled")

            if (self.last_position_x is None) and (self.last_position_y is None):
                self.last_position_x = list([pos[0]])
                self.last_position_y = list([pos[1]])
            else:
                self.last_position_x.append(pos[0])
                self.last_position_y.append(pos[1])

            return tuple((np.mean(self.last_position_x), np.mean(self.last_position_y)))

        # Device is moving
        else:
            if not self.kalman_enabled:
                self.kalman_enabled = True
                if (self.last_position_x is not None) and (self.last_position_y is not None):
                    self.my_filter.x = np.array([[np.mean(self.last_position_x)],
                                                 [np.mean(self.last_position_y)],
                                                 [0.],
                                                 [0.]])

            print("Kalman enabled")

            u = np.array([[real_acc[0][0]],
                          [real_acc[1][0]]
                          ])
            z = pos
            self.my_filter.predict(u)
            self.my_filter.update(z)
            self.count += 1
            print("Num: " + str(self.count))
            self.last_position_x = list([self.my_filter.x.item(0)])
            self.last_position_y = list([self.my_filter.x.item(1)])
            return self.last_position_x[0], self.last_position_y[0]  # returns position(X,Y)

    # SOLO TIENE EN CUENTA ACELERACION
    def estimatePositionUsingOnlyAcc(self, pos, acc_x, acc_y, curr_orientation, devname):

        # Computes the orientation of the device in order to
        # move it on the right direction.

        rotationMatrix = np.array([[np.cos(self.room_orientation), -np.sin(self.room_orientation)],
                                   [np.sin(self.room_orientation), np.cos(self.room_orientation)]])

        # rotationMatrix = np.array([[1, 0],
        #                            [0, 1]])

        real_acc = np.matmul(rotationMatrix, np.array([[acc_x],
                                                       [acc_y]]))

        # Filter small acceleration when device is static
        if np.sqrt(real_acc[0][0] ** 2 + real_acc[1][0] ** 2) < ACC_THRESHOLD:
            real_acc[0][0] = real_acc[1][0] = 0
            self.state_var[2] = 0.0
            self.state_var[3] = 0.0

        print(real_acc)
        print()

        # Device is moving

        print("Kalman enabled")

        self.state_var[0] += ((self.state_var[2] * self.delta_t) + ((real_acc[0][0] * (self.delta_t ** 2)) / 2))
        self.state_var[1] += ((self.state_var[3] * self.delta_t) + ((real_acc[1][0] * (self.delta_t ** 2)) / 2))
        self.state_var[2] += ((self.delta_t * real_acc[0][0]))
        self.state_var[3] += ((self.delta_t * real_acc[1][0]))

        self.last_position_x = list([self.state_var[0]])
        self.last_position_y = list([self.state_var[1]])
        return self.last_position_x[0], self.last_position_y[0]  # returns position(X,Y)

    # if position is computable, returns 2-tuple (X, Y) with the position
    # otherwise, returns ValueError
    def calculatePosition(self, anchors_positions, anchors_radius):

        anchor_names = list(anchors_positions.keys())

        x1 = anchors_positions[anchor_names[0]]['X']
        y1 = anchors_positions[anchor_names[0]]['Y']
        r1 = anchors_radius[anchor_names[0]]

        x2 = anchors_positions[anchor_names[1]]['X']
        y2 = anchors_positions[anchor_names[1]]['Y']
        r2 = anchors_radius[anchor_names[1]]

        x3 = anchors_positions[anchor_names[2]]['X']
        y3 = anchors_positions[anchor_names[2]]['Y']
        r3 = anchors_radius[anchor_names[2]]

        # Computing position using NumPy (doing the trilateration)

        def mse(x, locations, distances):
            mse = 0.0
            for location, distance in zip(locations, distances):
                distance_calculated = self.euclideanDistance(x[0], x[1], location[0], location[1])
                mse += pow(distance_calculated - distance, 2.0)
            return mse / len(locations)

        locations = [(x1, y1), (x2, y2), (x3, y3)]
        distances = [r1, r2, r3]
        init_guess = np.array([0, 0])
        res = minimize(mse, init_guess, args=(locations, distances), method='L-BFGS-B',
                       options={'ftol': 1e-5, 'maxiter': 1e9})

        return tuple((res.x[0], res.x[1]))

    def setDevicesInitialOrientation(self, devs_orientation):
        self.initial_devs_orientation.update(devs_orientation)


class Anchor:

    def __init__(self, name, X, Y):
        self.name = name
        self.X = X
        self.Y = Y

    def getName(self):
        return self.name

    def getX(self):
        return self.X

    def getY(self):
        return self.Y



class Device:

    def __init__(self, devname):
        self.devname = devname

    def getDevName(self):
        return self.devname

    def setPositionX(self, x):
        self.x = x

    def setPositionY(self, y):
        self.y = y

    def setPosition(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def getPosition(self):
        return self.x, self.y



class PlotSettings:

    def __init__(self, x_min=None, x_max=None, y_min=None, y_max=None, show_circles=False, show_RSSI=False):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.show_circles = show_circles
        self.show_RSSI = show_RSSI

    def getXMax(self):
        return self.x_max

    def getXMin(self):
        return self.x_min

    def getYMin(self):
        return self.y_min

    def getYMax(self):
        return self.y_max

    def isShowCircles(self):
        return self.show_circles

    def setShowCircles(self, show_circles):
        self.show_circles = show_circles
