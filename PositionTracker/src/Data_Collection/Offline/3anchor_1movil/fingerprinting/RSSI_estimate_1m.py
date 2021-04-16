'''
Lee los datos de RSSI a 1m del movil a cada launchpad (/3LP_1M/1m_LAUNCHX)
Saca la media y la stdev
'''

import numpy as np
import matplotlib.pyplot as plt
import json
import scipy.stats as stats
import pandas as pd
import statsmodels.api as sm

rssi_data = [] #datos de RSSI de cada launchpad al movil. Luego se usaran estos datos para la estadistica

'''
Guardamos la RSSI de cada muestra obtenida a través del LAUNCH1
'''
with open('1m_LAUNCH1.json', 'r') as file:
    python_obj = json.load(file)
    rssi_data += [int(sample['RSSI']) for sample in python_obj]

'''
Guardamos la RSSI de cada muestra obtenida a través del LAUNCH2
'''
with open('1m_LAUNCH2.json', 'r') as file:
    python_obj = json.load(file)
    rssi_data += [int(sample['RSSI']) for sample in python_obj]

'''
Guardamos la RSSI de cada muestra obtenida a través del LAUNCH3
'''
with open('1m_LAUNCH3.json', 'r') as file:
    python_obj = json.load(file)
    rssi_data += [int(sample['RSSI']) for sample in python_obj]

'''
hacemos estadisticas con los datos almacenados en rssi_data
'''

print(f'mean: {np.mean(rssi_data)}')
print(f'std dev: {np.std(rssi_data)}')
print(f'num samples: {len(rssi_data)}')

'''
comprobar si sigue una distribucion normal
'''

print(f'intervalo confianza 95%: {stats.norm.interval(0.95, loc=np.mean(rssi_data), scale=stats.sem(rssi_data))}')

stats.probplot(rssi_data, dist="norm", plot=plt)
plt.show()
