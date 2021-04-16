import psycopg2
import yaml
import time


class DB:

    def __init__(self):
        # setting the database parameters for accessing later.

        with open('../config.yml', 'r') as file:
            cfg = yaml.load(file)
            self.conn = psycopg2.connect(database=cfg['postgreSQL']['dbname'], user=cfg['postgreSQL']['user'],
                                         password=cfg['postgreSQL']['pass'], host=cfg['postgreSQL']['host'],
                                         port=cfg['postgreSQL']['port'])

        self.cur = self.conn.cursor()

        # get the 3 different launchpad identifiers in order to build the queries later
        self.cur.execute("SELECT DISTINCT launchpadid FROM scannersData")
        anchor_list_names = self.cur.fetchall()
        self.anchor1_name = anchor_list_names[0][0]
        self.anchor2_name = anchor_list_names[1][0]
        self.anchor3_name = anchor_list_names[2][0]

        # get the devices names and store them in a list

        self.devnamesList = []
        self.cur.execute("SELECT DISTINCT devname FROM scannersData")
        res = self.cur.fetchall()
        for dev_tup in res:
            self.devnamesList.append(dev_tup[0])

    def getRssiBetweenDevices(self, dev1, lp, num_results=30):
        """
            gets a list of the last num_results RSSI measures between dev1 and dev2.
            dev1 acts as advertiser whereas dev2 acts as scanner.
            By default, num_results is 30.
        """

        result = dict()
        self.cur.execute(
            "SELECT rssi FROM scannersdata WHERE devname=%(advertiser)s AND launchpadid=%(scanner)s ORDER BY id DESC LIMIT %(num_res)s",{'advertiser':dev1, 'scanner':lp, 'num_res':str(num_results)} )

        aux = self.cur.fetchall()
        result[lp] = list(map(lambda x: int(x[0]), aux))

        return result[lp]


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

        self.cur.execute("SELECT MAX(id) FROM scannersdata")
        res = self.cur.fetchall()
        res = int(res[0][0]) - keepNRows
        self.cur.execute("DELETE FROM scannersdata WHERE id < %(res)s", {'res': str(res)})
        self.conn.commit()

    def deleteDatabaseContent(self):
        self.cur.execute("DELETE FROM scannersdata WHERE true")
        return
