from accessDB import DB
import numpy as np
import yaml

class ProcessData:

    def __init__(self):
        #hardcodeamos los parametros de la formula RSSI-distance
        self.A = -47.697
        self.n = -0.827
        self.db_manager = DB()
        self.launchpadIds = self.db_manager.getLaunchpadIds()
        self.devicesList = self.db_manager.getDevicesList()
#        self.form_data = form_data
        self.raw_result = self.db_manager.getDataOfDevice(self.devicesList[0])

    def get_raw_result(self):
        return self.raw_result

    def estimate_position(self):

        #obtenemos las capturas de RSSI de los 3 launchpads

        l1_data = list(map(lambda x: int(x[0]), self.raw_result[self.launchpadIds[0]])) # x[0] porque x es una tupla
        l2_data = list(map(lambda x: int(x[0]), self.raw_result[self.launchpadIds[1]])) # x[0] porque x es una tupla
        l3_data = list(map(lambda x: int(x[0]), self.raw_result[self.launchpadIds[2]])) # x[0] porque x es una tupla

        # calculamos la media de la RSSI capturada para cada launchpad

        rssi_l1 = np.mean(l1_data)
        rssi_l2 = np.mean(l2_data)
        rssi_l3 = np.mean(l3_data)

        #aplicamos la formula RSSI-distance

        dist = lambda x : np.power(10, (x-self.A)/(-10*self.n))

        dists_dict = dict()
        dists_dict[self.launchpadIds[0]] = dist(rssi_l1)
        dists_dict[self.launchpadIds[1]] = dist(rssi_l2)
        dists_dict[self.launchpadIds[2]] = dist(rssi_l3)

        return dists_dict

    def getLaunchpadIds(self):
        return self.launchpadIds