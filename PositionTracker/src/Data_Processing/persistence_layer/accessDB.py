import psycopg2
import yaml
import time
import pandas as pd


class DB:

    def __init__(self, anchors_list):
        # setting the database parameters for accessing later.

        self.last_rssi_values = None
        with open('../config.yml', 'r') as file:
            self.cfg = yaml.load(file)
            self.conn = psycopg2.connect(database=self.cfg['postgreSQL']['dbname'], user=self.cfg['postgreSQL']['user'],
                                         password=self.cfg['postgreSQL']['pass'], host=self.cfg['postgreSQL']['host'],
                                         port=self.cfg['postgreSQL']['port'])

        self.cur = self.conn.cursor()

        self.anchor1_name = anchors_list[0]
        self.anchor2_name = anchors_list[1]
        self.anchor3_name = anchors_list[2]

        # get the devices names and store them in a list

        self.devnamesList = []
        self.cur.execute("SELECT DISTINCT advDevice FROM cc2640data")
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
            "SELECT advDeviceRSSI FROM cc2640data WHERE advDevice=%(advertiser)s AND scanDevice=%(scanner)s ORDER BY id DESC LIMIT %(num_res)s",{'advertiser':dev1, 'scanner':lp, 'num_res':str(num_results)} )

        aux = self.cur.fetchall()
        result[lp] = list(map(lambda x: int(x[0]), aux))

        return result[lp]

    def getRSSIsFromAnchorsToCell(self, cellname, num_results):
        """
            Gets the latest num_results RSSIs from all the anchors to the tag 'cellname'

            A list of 'num_results' 3-tuple is returned. A 3-tuple value is (RSSI1, RSSI2, RSSI3).
            It first performs an inner join on timestamp, meaning that all records that have matching values on timestamp are joined and selected.
        """

        # Run this query if you consider that a reading of a BLE packet is valid as long as the 3 anchors received it.
        self.cur.execute("""SELECT t1.advdevicerssi, t2.advdevicerssi, t3.advdevicerssi 
                            FROM cc2640data AS t1 
                            INNER JOIN (SELECT time, advdevicerssi 
                                        FROM cc2640data 
                                        WHERE scandevice = %(anchor2)s AND advdevice = %(advertiser)s ) AS t2
                            ON t1.time = t2.time
                            INNER JOIN (SELECT time, advdevicerssi
                                        FROM cc2640data
                                        WHERE scandevice = %(anchor3)s AND advdevice = %(advertiser)s ) AS t3
                            ON t1.time = t2.time AND t1.time = t3.time
                            WHERE t1.scandevice = %(anchor1)s and t1.advdevice = %(advertiser)s
                            ORDER BY t1.time DESC
                            LIMIT %(num_res)s""", {'advertiser': cellname, 'anchor1': self.anchor1_name, 'anchor2': self.anchor2_name, 'anchor3': self.anchor3_name, 'num_res': str(num_results)})

        # Run this query if you do not mind that the 3 anchors received the same BLE packet but they received BLE packets with very similar timestamps
        #TODO: Create this query


        results = self.cur.fetchall()

        return results

    def getDevicesList(self):
        return self.devnamesList

    def getAnchorNames(self):
        return [self.anchor1_name, self.anchor2_name, self.anchor3_name]

    # se encarga de eliminar los resultados de la BD mas antiguos que ya no son utiles. Tanto de la tabla data como de la tabla sensorData.
    def keepLastXResultsInDB(self, keepNRows):
        # Tabla rssidata

        self.cur.execute("SELECT MAX(time) FROM cc2640data")
        res = self.cur.fetchall()
        res = int(res[0][0]) - keepNRows
        self.cur.execute("DELETE FROM cc2640data WHERE time < %(res)s", {'res': str(res)})
        self.conn.commit()

    def deleteDatabaseContent(self):
        self.cur.execute("DELETE FROM cc2640data WHERE true")
        return

    def getSVRScalerPath(self):
        return self.cfg['pythonApp']['pathSVRscaler']

    def getSVRModelPath(self):
        return self.cfg['pythonApp']['pathSVRmodel']

