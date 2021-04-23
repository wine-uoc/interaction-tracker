import time

from scipy.stats import mode
import sys
from abc import ABC, abstractmethod

sys.path.insert(1, '../persistence_layer')
from src.Data_Processing.persistence_layer.accessDB import DB
import numpy as np
from scipy.optimize import fsolve, minimize
import yaml
from joblib import load

file = open('../config.yml', 'r')
cfg = yaml.load(file)

NUM_RESULTS_RSSI = int(cfg['pythonApp']['numResultsDBrssi'])
NUM_RESULTS_ACCEL = int(cfg['pythonApp']['numResultsDBaccel'])
NUM_RESULTS_ORIENT = int(cfg['pythonApp']['numResultsDBorient'])
NUM_ROWS_KEPT_DB = int(cfg['pythonApp']['lastMillisDBKept'])


class ModelController:


    def initialize(self, form_data):
        """
        Initialize all the DS used in this class: launchpads and devices lists
        """
        self.anchors = []
        self.cells = []
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
            self.anchors.append(a)

        anchor_names = [anc.getName() for anc in self.anchors]
        self.db_manager = DB(anchor_names)
        # retrieve Devices data from DB
        for devname in self.db_manager.getDevicesList():
            d = Device(devname)
            self.cells.append(d)

        self.modelML = SVR(self.anchors, self.db_manager.getSVRModelPath(), self.db_manager.getSVRScalerPath())

    def deleteDatabaseContent(self):
        self.db_manager.deleteDatabaseContent()
        return

    def computeDevicesPositions(self):
        # using the anchors position and the radius for each circle they describe,
        # we can compute the position of the device devname

        # first of all, cells positions must be computed using ONLY the 3 real anchors
        est_init_dev_pos = dict()  # est_init_dev_pos contains a dictionary whose keys are device names and values are 2-tuples (x,y)
        for cell in self.cells:
            rssi_list = self.getRSSIsFromAnchorsToCell(cell.getDevName())
            if len(rssi_list) > 0: # If there are RSSI measurements from cellname
                # Update the position
                pos = self.modelML.getPosition(rssi_list[0][0], rssi_list[0][1], rssi_list[0][2])
                cell.setPosition(pos)


    def getRSSIsFromAnchorsToCell(self, cellname):
        rssi_list = self.db_manager.getRSSIsFromAnchorsToCell(cellname, NUM_RESULTS_RSSI)
        return rssi_list

    def getDevice(self, devname):
        for dev in self.devices:
            if dev.getDevName() == devname:
                return dev
        return None

    def getDevicePosition(self, dev):
        return dev.getPosition()

    def getDevicesPositions(self):
        result = dict()

        for cell in self.cells:
            self.getDevicePosition(cell)
            result[cell.getDevName()] = dict()
            pos = cell.getPosition()
            result[cell.getDevName()]['X'] = pos[0]
            result[cell.getDevName()]['Y'] = pos[1]

        return result

    def getDevicesList(self):
        return [self.cells[i].devname for i in self.cells]

    def getAnchorsPositions(self, anchors, non_target_pos):
        result = dict()
        for anc in anchors:
            result[anc] = dict()
            if len(anc) != 8:  # Anchor is a cell
                result[anc]['X'] = non_target_pos[0]
                result[anc]['Y'] = non_target_pos[1]
            else:  # Anchor is a launchpad
                x, y = self.getLaunchpadPosition(anc)
                result[anc]['X'] = x
                result[anc]['Y'] = y

        return result

    # returns launchpads positions (dictionary of anchors with dictionary of positions for each one)

    def getLaunchpadPositions(self):
        result = dict()
        for anc in self.anchors:
            result[anc.getName()] = dict()
            result[anc.getName()]['X'] = anc.getX()
            result[anc.getName()]['Y'] = anc.getY()
        return result

    # returns a 2-tuple (X, Y) representing the position of anchor anchor_name
    def getLaunchpadPosition(self, anchor_name):
        for anc in self.anchors:
            if anc.getName() == anchor_name:
                return anc.getX(), anc.getY()

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




class MLmodels:

    def __init__(self, anchors, path_to_model, path_to_scaler):
        self.anchors = anchors
        self.model = load(path_to_model)
        self.scaler = load(path_to_scaler)

    def trilateration(self, d1, d2, d3):

        def euclideanDistance(x, y, loc_x, loc_y):
            return np.sqrt(pow(x - loc_x, 2) + pow(y - loc_y, 2))

        def mse(x, locations, distances):
            mse_val = 0.0
            for location, distance in zip(locations, distances):
                distance_calculated = euclideanDistance(x[0], x[1], location[0], location[1])
                mse_val += pow(distance_calculated - distance, 2.0)
            return mse_val / len(locations)

        locations = [(self.anchors[0].X, self.anchors[0].Y),
                     (self.anchors[1].X, self.anchors[1].Y),
                     (self.anchors[2].X, self.anchors[2].Y)]
        distances = [d1, d2, d3]
        init_guess = np.array([0, 0])
        res = minimize(mse, init_guess, args=(locations, distances), method='L-BFGS-B',
                       options={'ftol': 1e-5, 'maxiter': 1e9})
        return res['x'][0], res['x'][1]

class SVR(MLmodels):

    """
        This class allows to perform positioning using the distance method (NO fingerprinting method)
    """

    def getPosition(self, rssi1, rssi2, rssi3):
        rssi1_scaled = self.scaler.transform(np.array(rssi1).reshape(-1, 1))
        rssi2_scaled = self.scaler.transform(np.array(rssi2).reshape(-1, 1))
        rssi3_scaled = self.scaler.transform(np.array(rssi3).reshape(-1, 1))

        d1 = self.model.predict(rssi1_scaled)[0]
        d2 = self.model.predict(rssi2_scaled)[0]
        d3 = self.model.predict(rssi3_scaled)[0]

        return self.trilateration(d1, d2, d3)

class MLP(MLmodels):
    """
        This class allows to perform positioning using the distance method (NO fingerprinting method)
    """

    def getPosition(self, rssi1, rssi2, rssi3):
        rssi1_scaled = self.scaler.transform(np.array(rssi1).reshape(-1, 1))
        rssi2_scaled = self.scaler.transform(np.array(rssi2).reshape(-1, 1))
        rssi3_scaled = self.scaler.transform(np.array(rssi3).reshape(-1, 1))

        d1 = self.model.predict(rssi1_scaled)[0]
        d2 = self.model.predict(rssi2_scaled)[0]
        d3 = self.model.predict(rssi3_scaled)[0]

        return self.trilateration(d1, d2, d3)

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
        """
            Initializes a Device instance with its name and sets its position to (0, 0) by default
        """
        self.devname = devname
        self.x = 0
        self.y = 0

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
