from accessDB import DB
import numpy as np
import yaml
from scipy.optimize import fsolve
from sympy.solvers import solve
from sympy import Symbol
from sympy.solvers import linsolve
import math


class ProcessData:

    def __init__(self):
        # hardcodeamos los parametros de la formula RSSI-distance
        self.A = -47.697
        self.n = -0.827
        self.db_manager = DB()
        self.launchpadIds = self.db_manager.getAnchorNames()
        self.devicesList = self.db_manager.getDevicesList()


        # self.result es un diccionario cuyos elementos seran los nombres de los móviles. Cada elemento de ese diccionario es a la vez
        # otro diccionario de 3 elementos, cuyas KEYs seran los nombres de los id's de launchpad y sus VALUEs seran arrays
        # de N valores de RSSI.

        self.result = dict()
        for dev in self.devicesList:
            self.result[dev] = self.db_manager.getRssiOfDevice(dev)

        # este diccionario almacenara, por cada id de launchpad, otro diccionario con la coord X y la coord Y.
        self.anchorPositions = dict()

        # Leemos el fichero yaml que contiene las posicones que introdujo el usuario en el formulario de la web

        with open("position.yml", 'r') as posfile:
            data_pos = yaml.load(posfile)
            for anchor_data in data_pos["anchorsInfo"]:
                x = float(data_pos["anchorsInfo"][anchor_data]['X'])
                y = float(data_pos["anchorsInfo"][anchor_data]['Y'])
                self.anchorPositions[data_pos["anchorsInfo"][anchor_data]["name"]] = {'X': x, 'Y': y}

    def getAnchorPositions(self):
        pass


    def estimatePosition(self):


        # obtenemos las capturas de RSSI de los 3 launchpads para cada movil detectado
        res = dict()
        for rssi_dev in self.result.keys():
            l1_data = list(map(lambda x: int(x[0]), self.result[rssi_dev][self.launchpadIds[0]]))  # x[0] porque x es una tupla
            l2_data = list(map(lambda x: int(x[0]), self.result[rssi_dev][self.launchpadIds[1]]))  # x[0] porque x es una tupla
            l3_data = list(map(lambda x: int(x[0]), self.result[rssi_dev][self.launchpadIds[2]]))  # x[0] porque x es una tupla

            # calculamos la media de la RSSI capturada para cada launchpad

            rssi_l1 = np.mean(l1_data)
            rssi_l2 = np.mean(l2_data)
            rssi_l3 = np.mean(l3_data)

            # aplicamos la formula RSSI-distance

            dist = lambda x: np.power(10, (x - self.A) / (-10 * self.n))

            r1 = dist(rssi_l1)
            r2 = dist(rssi_l2)
            r3 = dist(rssi_l3)

            #usamos dichas distancias como los radios en las ecuaciones del circulo de los respectivos anchors para encontrar la posicion del movil.
            x1 = self.anchorPositions[self.launchpadIds[0]]['X']
            y1 = self.anchorPositions[self.launchpadIds[0]]['Y']

            x2 = self.anchorPositions[self.launchpadIds[1]]['X']
            y2 = self.anchorPositions[self.launchpadIds[1]]['Y']

            x3 = self.anchorPositions[self.launchpadIds[2]]['X']
            y3 = self.anchorPositions[self.launchpadIds[2]]['Y']

            x = Symbol('x')
            y = Symbol('y')
            f = solve((x - x1) ** 2 + (y - y1) ** 2 - (r1 ** 2) - ((x - x2) ** 2 + (y - y2) ** 2 - (r2 ** 2)),[x,y],dict=True)
            g = solve((x - x1) ** 2 + (y - y1) ** 2 - (r1 ** 2) - ((x - x3) ** 2 + (y - y3) ** 2 - (r3 ** 2)),[x,y],dict=True)
            h = solve((x - x2) ** 2 + (y - y2) ** 2 - (r2 ** 2) - ((x - x3) ** 2 + (y - y3) ** 2 - (r3 ** 2)),[x,y],dict=True)

            #extraer las ecuaciones de las rectas y calcular el punto.

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


            #print(linsolve([eq1, eq2], (y, x)))
            #print(linsolve([eq1, eq3], (y, x)))
            #print(linsolve([eq2, eq3], (y, x)))

            coord_dev_i = dict()

            coords = list(linsolve([eq1, eq2, eq3], (y, x)))
            if len(coords) > 0:
                coord_dev_i['x'] = str(coords[0][1])
                coord_dev_i['y'] = str(coords[0][0])

            res[rssi_dev] = coord_dev_i

        return res

    def getLaunchpadIds(self):
        return self.launchpadIds

    def getDevicesList(self):
        return self.devicesList
