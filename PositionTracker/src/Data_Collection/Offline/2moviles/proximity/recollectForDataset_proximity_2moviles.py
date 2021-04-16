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
PREPARAR ESTRUCTURAS DE DATOS
'''
MOVILES = ['TARGETDEV-z9412b', 'TARGETDEV-r7v5wv'] #tendrá los nombres de los 2 móviles
NUM_SAMPLES = 50    # numero de muestras por cada movil y posicion (x,y)
DIST = 300          # en centimetros

'''
CREAR FICHEROS
'''
filename_mov_1 = 'detectedDevs_' + MOVILES[0] + '_' + str(DIST) + '_cm' + '_.json'
filename_mov_2 = 'detectedDevs_' + MOVILES[1] + '_' + str(DIST) + '_cm' + '_.json'

'''
ALGORITMO
'''
#Eliminar contenido BD
cur.execute("DELETE FROM phonesdata WHERE true")
conn.commit()

#Inicializar num_collected_samples a 0 para cada movil
num_collected_samples = dict()
num_collected_samples[MOVILES[0]] = 0
num_collected_samples[MOVILES[1]] = 0

#Mientras no se hayan recolectado la cantidad de samples deseados
while (num_collected_samples[MOVILES[0]] < NUM_SAMPLES or num_collected_samples[MOVILES[1]] < NUM_SAMPLES):

    #Mirar cuántos samples se han recolectado por cada móvil
    cur.execute("SELECT COUNT(*) FROM phonesdata WHERE scanDevice=%(scanDevice)s",{'scanDevice':MOVILES[0]})
    num_collected_samples[MOVILES[0]] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM phonesdata WHERE scanDevice=%(scanDevice)s",{'scanDevice':MOVILES[1]})
    num_collected_samples[MOVILES[1]] = cur.fetchone()['count']

print('END!')

cur.execute("SELECT * FROM phonesdata WHERE scanDevice=%(scanDevice)s ORDER BY time DESC LIMIT %(num_samples)s", {'scanDevice':MOVILES[0], 'num_samples':NUM_SAMPLES})
raw_data_mov0 = cur.fetchall()

cur.execute("SELECT * FROM phonesdata WHERE scanDevice=%(scanDevice)s ORDER BY time DESC LIMIT %(num_samples)s", {'scanDevice':MOVILES[1], 'num_samples':NUM_SAMPLES})
raw_data_mov1 = cur.fetchall()

'''
GUARDAR LOS DATOS EN FICHEROS
'''
f1 = open(filename_mov_1, 'a')
json.dump(raw_data_mov0, f1, indent=2)

f2 = open(filename_mov_2, 'a')
json.dump(raw_data_mov1, f2, indent=2)

