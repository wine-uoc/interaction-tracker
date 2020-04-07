from accessDB import DB
import numpy as np
from scipy.optimize import fsolve
from sympy.solvers import solve
from sympy import Symbol
from sympy.solvers import linsolve
from sympy.geometry.ellipse import Circle
from sympy.geometry.polygon import Point, Triangle
from sympy.geometry.line import Segment2D

class ModelController:

    #initialize Anchor and Device classes
    def initialize(self, form_data):
        self.anchors = []
        self.devices = []
        self.db_manager = DB()
        self.model = RSSI_Distance_Model()
        self.plot_settings = PlotSettings(float(form_data['roomInfo']['X_min']),
                                          float(form_data['roomInfo']['X_max']),
                                          float(form_data['roomInfo']['Y_min']),
                                          float(form_data['roomInfo']['Y_max']))

        # set Anchor data from form_data
        for anc in form_data['anchorsInfo']:
            name = form_data['anchorsInfo'][anc]['name']
            X = float(form_data['anchorsInfo'][anc]['X'])
            Y = float(form_data['anchorsInfo'][anc]['Y'])
            a = Anchor(name,X,Y)
            self.anchors.append(a)

        #retrieve Devices data from DB
        for devname in self.db_manager.getDevicesList():
            d = Device(devname)
            self.devices.append(d)


    # returns anchors positions (dictionary of anchors with dictionary of positions for each one)
    def getAnchorsPositions(self):
        result = dict()
        for anc in self.anchors:
            result[anc.getName()] = dict()
            result[anc.getName()]['X'] = anc.getX()
            result[anc.getName()]['Y'] = anc.getY()
        return result

    #returns a 2-tuple (X, Y) representing the position of anchor anchor_name
    def getAnchorPosition(self, anchor_name):
        for anc in self.anchors:
            if anc.getName() == anchor_name:
                return anc.getX(), anc.getY()


    # returns the value of the distance from anchor anchor_name to device device_name
    def getDistanceFromAnchorToDevice(self, anchor_name, device_name):
        rssi_list = self.db_manager.getRssiOfDeviceFromAnchor(device_name, anchor_name, num_results=30)
        rssi_mean = np.mean(rssi_list)
        return self.model.calculateDistance(rssi_mean)

    # returns the value of the RSSI from anchor anchor_name to device device_name
    def getRssiFromAnchorOfDevice(self, anchor_name, device_name):
        rssi_list = self.db_manager.getRssiOfDeviceFromAnchor(device_name, anchor_name, num_results=30)
        rssi_mean = np.mean(rssi_list)
        return int(rssi_mean)

     #returns a dictionary with 3 keys. Keys are anchor names and values are the distances from this anchor to the device.
    def getDistancesToDevice(self, devname):
        result = dict()
        for anc in self.anchors:
            result[anc.getName()] = self.getDistanceFromAnchorToDevice(anc.getName(), devname)
        return result

    def getDevicePosition(self, devname):
        # using the anchors position and the radius for each circle they describe,
        # we can compute the position of the device devname

        radius_dict = self.getDistancesToDevice(devname)
        anchor_positions_dict = self.getAnchorsPositions()

        pos = self.model.calculatePosition(anchor_positions_dict, radius_dict)

        return pos

    def getDevicesPositions(self):
        result = dict()

        for dev in self.devices:
            x, y = self.getDevicePosition(dev.getDevName())
            result[dev.getDevName()] = dict()
            result[dev.getDevName()]['X'] = x
            result[dev.getDevName()]['Y'] = y

        return result

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
        self.db_manager.keepLastXResultsInDB(300)


class RSSI_Distance_Model:
    def __init__(self):
        self.A = -47.697
        self.n = 5#-0.827

    def get_A(self):
        return self.A

    def get_n(self):
        return self.n

    def set_A(self, a):
        self.A = a

    def set_n(self, n):
        self.n = n

    def calculateDistance(self, rssi_mean):
        return np.power(10,(rssi_mean - self.A)/(-10*self.n))




    #if position is computable, returns 2-tuple (X, Y) with the position
    #otherwise, returns ValueError
    def calculatePosition(self, anchors_positions, anchors_radius):

        anchor_names = list(anchors_positions.keys())
        anchors_positions.keys()
        x1 = anchors_positions[anchor_names[0]]['X']
        y1 = anchors_positions[anchor_names[0]]['Y']
        r1 = anchors_radius[anchor_names[0]]

        x2 = anchors_positions[anchor_names[1]]['X']
        y2 = anchors_positions[anchor_names[1]]['Y']
        r2 = anchors_radius[anchor_names[1]]

        x3 = anchors_positions[anchor_names[2]]['X']
        y3 = anchors_positions[anchor_names[2]]['Y']
        r3 = anchors_radius[anchor_names[2]]

        #define the circles with center anchor_position (xi, yi) and radius ri
        c1 = Circle(Point(x1, y1), r1)
        c2 = Circle(Point(x2, y2), r2)
        c3 = Circle(Point(x3, y3), r3)

        x = Symbol('x')
        y = Symbol('y')

        # compute the line equations
        f = solve(c1.equation(x, y) - c2.equation(x, y), [x, y], dict=True)
        g = solve(c1.equation(x, y) - c3.equation(x, y), [x, y], dict=True)
        h = solve(c2.equation(x, y) - c3.equation(x, y), [x, y], dict=True)

        #convert the line equations (y = a*x + b) or (x = a*y + b) to (a*y - b*x - c = 0)
        if y in f[0].keys():
            eq1 = -y + f[0][y].evalf(2)
        else:
            eq1 = -x + f[0][x].evalf(2)

        if y in g[0].keys():
            eq2 = -y + g[0][y].evalf(2)
        else:
            eq2 = -x + g[0][x].evalf(2)

        if y in h[0].keys():
            eq3 = -y + h[0][y].evalf(2)
        else:
            eq3 = -x + h[0][x].evalf(2)

        # get the points of intersection between the three lines
        point1 = Point(list(linsolve([eq1, eq2], (x, y)))[0])
        point2 = Point(list(linsolve([eq1, eq3], (x, y)))[0])
        point3 = Point(list(linsolve([eq2, eq3], (x, y)))[0])

        t = Triangle(point1, point2, point3)
        if isinstance(t, Triangle):
            return tuple(t.incenter.evalf(5))
        elif isinstance(t, Segment2D):
            return tuple(t.midpoint.evalf(5))
        else :
            return tuple(t.evalf(5))




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


class PlotSettings:

    def __init__(self, x_min=None, x_max = None, y_min=None, y_max=None, show_circles=False, show_RSSI=False):
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


