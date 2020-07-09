import psycopg2
import yaml
import time


class DB:

    def __init__(self):
        # setting the database parameters for accessing later.

        with open('config.yml', 'r') as file:
            cfg = yaml.load(file)
            self.conn = psycopg2.connect(database=cfg['postgreSQL']['dbname'], user=cfg['postgreSQL']['user'],
                                         password=cfg['postgreSQL']['pass'], host=cfg['postgreSQL']['host'],
                                         port=cfg['postgreSQL']['port'])

        self.cur = self.conn.cursor()

        # get the 3 different launchpad identifiers in order to build the queries later
        self.cur.execute("SELECT DISTINCT dstdevice FROM rssiphonedata WHERE length(dstdevice) = 4")
        anchor_list_names = self.cur.fetchall()
        self.anchor1_name = anchor_list_names[0][0]
        self.anchor2_name = anchor_list_names[1][0]
        self.anchor3_name = anchor_list_names[2][0]

        # get the devices names and store them in a list

        self.devnamesList = []
        self.cur.execute("SELECT DISTINCT srcdevice FROM rssiphonedata")
        res = self.cur.fetchall()
        for dev_tup in res:
            self.devnamesList.append(dev_tup[0])

    def getRssiOfDeviceFromDevice(self, devname, anchor_name, num_results=30):
        """
            gets a list of the last num_results RSSI measures of the device with devname
            from device anchor_name acting as anchor. By default, num_results is 30.
        """

        result = dict()

        self.cur.execute(
            "SELECT rssi FROM rssiphonedata WHERE srcdevice=%(devname)s AND dstdevice=%(anc_name)s ORDER BY id DESC LIMIT %(num_res)s",
            {'devname': devname, 'anc_name': anchor_name, 'num_res': str(num_results)})
        aux1 = self.cur.fetchall()

        self.cur.execute(
            "SELECT rssi FROM rssiphonedata WHERE srcdevice=%(anc_name)s AND dstdevice=%(devname)s ORDER BY id DESC LIMIT %(num_res)s",
            {'devname': devname, 'anc_name': anchor_name, 'num_res': str(num_results)})
        aux2 = self.cur.fetchall()

        res_list = list(map(lambda x: int(x[0]), aux1)) + list(map(lambda x: int(x[0]), aux2))
        result[anchor_name] = res_list

        return result[anchor_name]

    def getRssiOfDeviceFromLaunchpad(self, devname, anchor_name, num_results=30):
        """
            gets a list of the last num_results RSSI measures of the device with devname
            from anchor anchor_name. By default, num_results is 30.
        """

        result = dict()
        self.cur.execute(
            "SELECT rssi FROM rssiphonedata WHERE srcdevice=%(devname)s AND dstdevice=%(anc_name)s ORDER BY id DESC LIMIT %(num_res)s",{'devname':devname, 'anc_name':anchor_name, 'num_res':str(num_results)} )

        aux = self.cur.fetchall()
        result[anchor_name] = list(map(lambda x: int(x[0]), aux))

        return result[anchor_name]




    def getRssiOfDevice(self, devname, num_results=30):
        """
            gets a list of the last num_results RSSI measures of the device with devname
            from all anchors. By default, num_results is 30.

            returns a dictionary with 3 elements, one for each anchor, and every element has a list
            of the last num_results RSSI values for the device devname.
        """

        result = dict()
        self.cur.execute(
            "SELECT rssi FROM rssiphonedata WHERE srcdevice='" + devname + "'AND dstdevice='" + self.anchor1_name + "' ORDER BY id DESC LIMIT " + str(
                num_results))
        aux = self.cur.fetchall()
        result[self.anchor1_name] = list(map(lambda x: int(x[0]), aux))
        self.cur.execute(
            "SELECT rssi FROM rssiphonedata WHERE srcdevice='" + devname + "'AND dstdevice='" + self.anchor2_name + "' ORDER BY id DESC LIMIT " + str(
                num_results))
        aux = self.cur.fetchall()
        result[self.anchor2_name] = list(map(lambda x: int(x[0]), aux))
        self.cur.execute(
            "SELECT rssi FROM rssiphonedata WHERE srcdevice='" + devname + "'AND dstdevice='" + self.anchor3_name + "' ORDER BY id DESC LIMIT " + str(
                num_results))
        aux = self.cur.fetchall()
        result[self.anchor3_name] = list(map(lambda x: int(x[0]), aux))

        return result

    def getDevicesList(self):
        return self.devnamesList

    def getAnchorNames(self):
        return [self.anchor1_name, self.anchor2_name, self.anchor3_name]

    # se encarga de eliminar los resultados de la BD mas antiguos que ya no son utiles. Tanto de la tabla data como de la tabla sensorData.
    def keepLastXResultsInDB(self, keepNRows):
        # Tabla rssidata

        self.cur.execute("SELECT MAX(id) FROM rssiphonedata")
        res = self.cur.fetchall()
        res = int(res[0][0]) - keepNRows
        self.cur.execute("DELETE FROM rssiphonedata WHERE id < %(res)s", {'res': str(res)})
        self.conn.commit()

        # Tabla accelData
        '''
        self.cur.execute("SELECT MAX(id) FROM acceldata")
        res = self.cur.fetchall()
        res = int(res[0][0]) - keepNRows
        self.cur.execute("DELETE FROM acceldata WHERE id < %(res)s", {'res': str(res)})
        self.conn.commit()

        # Tabla orientationData
        self.cur.execute("SELECT MAX(id) FROM orientationdata")
        res = self.cur.fetchall()
        res = int(res[0][0]) - keepNRows
        self.cur.execute("DELETE FROM orientationdata WHERE id < %(res)s", {'res': str(res)})
        self.conn.commit()
        '''

    def getAccelerationValues(self, devname, num_results):
        self.cur.execute(
            "SELECT x_acc, y_acc FROM acceldata WHERE devname=%(devname)s ORDER BY id DESC LIMIT %(num_results)s",{'devname':devname, 'num_results':num_results})
        data_raw = self.cur.fetchone()

        acc_x = float(data_raw[0])#list(map(lambda x: float(x[0]), data_raw))
        acc_y = float(data_raw[1])#list(map(lambda x: float(x[1]), data_raw))
        return acc_x, acc_y

    def getOrientationValues(self, devname, num_results):

        self.cur.execute(
            "SELECT x_ori FROM orientationdata WHERE devname=%(devname)s ORDER BY id DESC LIMIT %(num_results)s",{'devname':devname, 'num_results':num_results})
        data_raw = self.cur.fetchone()

        #De momento solo nos interesa la orientacion en x (cuantos grados nos hemos desviado del vector que apunta hacia el norte magnetico)
        ori_x = float(data_raw[0])#list(map(lambda x: float(x[0]), data_raw))
        return ori_x

