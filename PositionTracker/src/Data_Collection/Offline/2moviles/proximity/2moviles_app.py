import numpy as np
import matplotlib.pyplot as plt
import json
import scipy.stats as stats
import pandas as pd
# import statsmodels.api as sm
import os
from joblib import load
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.utils import resample
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
import psycopg2
from psycopg2.extras import RealDictCursor
import yaml
import time
import json

'''
CONECTAR CON LA BD
'''
file = open('/home/aaron/Trabajo/interaction-tracker-updated/PositionTracker/src/Data_Processing/config.yml', 'r')
cfg = yaml.load(file)
conn = psycopg2.connect(database=cfg['postgreSQL']['dbname'], user=cfg['postgreSQL']['user'],
                             password=cfg['postgreSQL']['pass'], host=cfg['postgreSQL']['host'],
                             port=cfg['postgreSQL']['port'])

cur = conn.cursor(cursor_factory=RealDictCursor)

'''
IMPORTAR MODELO DE FICHERO
'''
NB_model = load('NB_model.joblib')

'''
ALGORITMO
'''
MOVILES = ['TARGETDEV-z9412b', 'TARGETDEV-r7v5wv'] #tendrá los nombres de los 2 móviles

while True:
    cur.execute("SELECT * FROM phonesdata WHERE scanDevice=%(scanDevice)s ORDER BY time DESC LIMIT %(num_samples)s", {'scanDevice':MOVILES[0], 'num_samples':1})
    rssi_mov0 = cur.fetchone()

    cur.execute("SELECT * FROM phonesdata WHERE scanDevice=%(scanDevice)s ORDER BY time DESC LIMIT %(num_samples)s", {'scanDevice':MOVILES[1], 'num_samples':1})
    rssi_mov1 = cur.fetchone()

    print(NB_model.predict(np.array(int(rssi_mov0['advdevicerssi'])).reshape(-1, 1)))

    time.sleep(0.2)

