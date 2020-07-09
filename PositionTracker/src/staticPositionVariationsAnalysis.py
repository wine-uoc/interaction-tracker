import psycopg2
import yaml
import numpy as np
import matplotlib.pyplot as plt

cur = None

with open('config.yml', 'r') as file:
    cfg = yaml.load(file)
    conn = psycopg2.connect(database=cfg['postgreSQL']['dbname'], user=cfg['postgreSQL']['user'],
                                 password=cfg['postgreSQL']['pass'], host=cfg['postgreSQL']['host'],
                                 port=cfg['postgreSQL']['port'])
    cur = conn.cursor()

devname1 = 'TARGETDEV-mom1qo'
devname2 = 'TARGETDEV-xelc2r'
anchor = '4278'

cur.execute("SELECT rssi FROM rssiphonedata WHERE srcdevice=%(devname)s AND dstdevice=%(anc_name)s",
            {'devname': devname1, 'anc_name': anchor})
d1_res = np.array(cur.fetchall()).squeeze().astype(np.int)
print(d1_res)

cur.execute("SELECT rssi FROM rssiphonedata WHERE srcdevice=%(devname)s AND dstdevice=%(anc_name)s",
            {'devname': devname2, 'anc_name': anchor})
d2_res = np.array(cur.fetchall()).squeeze().astype(np.int)
print(d2_res)

plt.title("RSSI media de los moviles a un anchor")
plt.boxplot(np.array([d1_res,d2_res]),showmeans=True, labels=[devname1, devname2])
plt.xlabel("Movil")
plt.ylabel("RSSI al anchor")
plt.show()