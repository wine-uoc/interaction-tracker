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
        ids_list = self.cur.fetchall()
        self.lId_1 = ids_list[0][0]
        self.lId_2 = ids_list[1][0]
        self.lId_3 = ids_list[2][0]

        # get the devices names and store them in a list

        self.devicesList = []
        self.cur.execute("SELECT DISTINCT devname FROM data")

        for dev_tup in self.cur.fetchall():
            self.devicesList.append(dev_tup[0])

    """
        Get the last 30 RSSI measurements for each different launchpad
        
        :return Dictionary of three keys, one for each launchpad. Values for each key are lists with the respective query result  
    """

    def getDataOfDevice(self, devname):
        self.result = dict()

        self.cur.execute(
            "SELECT rssi FROM data WHERE devname='" + devname + "'AND launchpadId='" + self.lId_1 + "' ORDER BY id DESC LIMIT 30")
        self.result[self.lId_1] = self.cur.fetchall()
        self.cur.execute(
            "SELECT rssi FROM data WHERE devname='" + devname + "'AND launchpadId='" + self.lId_2 + "' ORDER BY id DESC LIMIT 30")
        self.result[self.lId_2] = self.cur.fetchall()
        self.cur.execute(
            "SELECT rssi FROM data WHERE devname='" + devname + "'AND launchpadId='" + self.lId_3 + "' ORDER BY id DESC LIMIT 30")
        self.result[self.lId_3] = self.cur.fetchall()
        return self.result

    def getDevicesList(self):
        return self.devicesList


    def getLaunchpadIds(self):
        return [self.lId_1, self.lId_2, self.lId_3]
