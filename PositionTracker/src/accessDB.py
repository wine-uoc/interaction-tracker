import psycopg2
import yaml


class DB:

    def __init__(self):
        # setting the database parameters for accessing later.

        with open('db.yml', 'r') as file:
            cfg = yaml.load(file)
            self.conn = psycopg2.connect(database=cfg['postgreSQL']['dbname'], user=cfg['postgreSQL']['user'],
                                         password=cfg['postgreSQL']['pass'], host=cfg['postgreSQL']['host'],
                                         port=cfg['postgreSQL']['port'])

        self.cur = self.conn.cursor()

        # get the 3 different launchpad identifiers in order to build the queries later
        self.cur.execute("SELECT DISTINCT launchpadId FROM data")
        anchor_list_names = self.cur.fetchall()
        self.anchor1_name = anchor_list_names[0][0]
        self.anchor2_name = anchor_list_names[1][0]
        self.anchor3_name = anchor_list_names[2][0]

        # get the devices names and store them in a list

        self.devicesList = []
        self.cur.execute("SELECT DISTINCT devname FROM data")

        for dev_tup in self.cur.fetchall():
            self.devicesList.append(dev_tup[0])

    def getRssiOfDeviceFromAnchor(self, devname, anchor_name, num_results=30):
        """
            gets a list of the last num_results RSSI measures of the device with devname
            from anchor anchor_name. By default, num_results is 30.
        """
        result = dict()
        self.cur.execute(
            "SELECT rssi FROM data WHERE devname='" + devname + "'AND launchpadId='" + anchor_name + "' ORDER BY id DESC LIMIT " + str(
                num_results))
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
            "SELECT rssi FROM data WHERE devname='" + devname + "'AND launchpadId='" + self.anchor1_name + "' ORDER BY id DESC LIMIT " + str(
                num_results))
        aux = self.cur.fetchall()
        result[self.anchor1_name] = list(map(lambda x: int(x[0]), aux))
        self.cur.execute(
            "SELECT rssi FROM data WHERE devname='" + devname + "'AND launchpadId='" + self.anchor2_name + "' ORDER BY id DESC LIMIT " + str(
                num_results))
        aux = self.cur.fetchall()
        result[self.anchor2_name] = list(map(lambda x: int(x[0]), aux))
        self.cur.execute(
            "SELECT rssi FROM data WHERE devname='" + devname + "'AND launchpadId='" + self.anchor3_name + "' ORDER BY id DESC LIMIT " + str(
                num_results))
        aux = self.cur.fetchall()
        result[self.anchor3_name] = list(map(lambda x: int(x[0]), aux))
        return result

    def getDevicesList(self):
        return self.devicesList

    def getAnchorNames(self):
        return [self.anchor1_name, self.anchor2_name, self.anchor3_name]

    # se encarga de eliminar los resultados de la BD mas antiguos que ya no son utiles. Tanto de la tabla data como de la tabla sensorData.
    def keepLastXResultsInDB(self, keepNRows):
        # Tabla data
        self.cur.execute("SELECT MAX(id) FROM data")
        res = self.cur.fetchall()
        res = res[0][0] - keepNRows
        self.cur.execute("DELETE FROM data WHERE id < %(res)s", {'res': str(res)})
        self.conn.commit()

        # Tabla sensorData
        self.cur.execute("SELECT MAX(id) FROM sensordata")
        res = self.cur.fetchall()
        res = res[0][0] - keepNRows
        self.cur.execute("DELETE FROM sensordata WHERE id < %(res)s", {'res': str(res)})
        self.conn.commit()

    def getAccelerationValues(self, devname, num_results):
        self.cur.execute(
            "SELECT x_acc, y_acc FROM sensordata WHERE devname='" + devname + "' ORDER BY id DESC LIMIT 1")
        data_raw = self.cur.fetchall()

        acc_x = list(map(lambda x: float(x[0]), data_raw))
        acc_y = list(map(lambda x: float(x[1]), data_raw))

        return acc_x[0], acc_y[0]
