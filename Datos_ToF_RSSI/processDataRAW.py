##
#
# Author: Carolina Cabrera
#

import json as js
import numpy as np
from matplotlib import pyplot


###################################################################################################################
#### IMPORTANTE: modificar estas variables de acuerdo a los datos que se tengan. Es lo único que hay que modificar.
#paths de archivos de datos
paths = ['dataOutMaster0MetrosRAW.json','dataOutMaster1MetrosRAW.json','dataOutMaster2MetrosRAW.json','dataOutMaster4MetrosRAW.json','dataOutMaster6MetrosRAW.json','dataOutMaster7MetrosRAW.json']#,'master3m.txt'] #,
# Distancias a las que se tomaron datos (en el mismo orden que se leen los archivos)
metros = [0,1,2,4,6,7]
# Frecuencias utilizadas
freq = [2422, 2424, 2448, 2450, 2472, 2470]
###################################################################################################################

### Defino Constantes
TICKS_TO_METER = 18.75
NOT_VALID = 0xFFFFFFFF

###################################################################################################################
### LECTURA DE DATOS

# Lectura de archivos
data = list() #lista para leer datos de los archivos
for filename in paths:
	with open(filename,'r') as file:
		data.append(js.load(file))
times = [n['elapsedTime'] for n in data]
data = [n['dataArray'] for n in data]

#Creo estructura para guardar datos
ticksPerFreq = list()
ticksMixFreq = list()
rssiPerFreq = list()
rssiMixFreq = list()
for i in range(len(paths)):
	ticksPerFreq.append([])
	ticksMixFreq.append([])
	rssiPerFreq.append([])
	rssiMixFreq.append([])
	for j in range(len(freq)):
		ticksPerFreq[i].append([])
		rssiPerFreq[i].append([])

#Organizo informacion de ticks y rssi en las estructuras creadas
for d in data: #Cada elemento de data son los resultados para una distancia (0,1,2,4, o 7 metros)
	dIdx = data.index(d)
	for b in d: #Cada elemento de d son los datos de cada burst
		for s in b['payload']['samples']: #Recorro samples
			freqIdx = s['freqIdx']
			tick = s['tick']
			rssi = s['rssi']
			if tick != NOT_VALID:
				(ticksPerFreq[dIdx][freqIdx]).append(tick/256)   #Divido por 256 porque los datos en modo RAW vienen multiplicados por este valor
				ticksMixFreq[dIdx].append(tick/256)
				(rssiPerFreq[dIdx][freqIdx]).append(rssi)
				rssiMixFreq[dIdx].append(rssi)

#Imprimo Cantidad de muestras válidas
print('Muestras validas 0m')
print(len(ticksMixFreq[0]))
print('Muestras validas 1m')
print(len(ticksMixFreq[1]))
print('Muestras validas 2m')
print(len(ticksMixFreq[2]))
print('Muestras validas 4m')
print(len(ticksMixFreq[3]))
print('Muestras validas 6m')
print(len(ticksMixFreq[4]))
print('Muestras validas 7m')
print(len(ticksMixFreq[5]))


###################################################################################################################
### CALCULO DE MEDIA Y DESVIACION

# Creo estructuras para guardar media por canal y media mezclando canales.
meanPerFreq = list()
stdPerFreq = list()
meanMixFreq = list()
stdMixFreq = list()
for i in range(len(paths)):
	meanPerFreq.append([])
	stdPerFreq.append([])
	meanMixFreq.append([])
	stdMixFreq.append([])
	for j in range(len(freq)):
		meanPerFreq[i].append([])
		stdPerFreq[i].append([])

#Calculo media por frecs
for td in ticksPerFreq:
	itd = ticksPerFreq.index(td)
	for tf in td:
		itf = td.index(tf)
		meanPerFreq[itd][itf] = np.mean(tf)
		stdPerFreq[itd][itf] = np.std(tf)

#Calculo media mezclando frecs y seleccionando primeras 7400 muestras 
for td in ticksMixFreq:
	itd = ticksMixFreq.index(td)
	meanMixFreq[itd] = np.mean(td[0:7400])
	stdMixFreq[itd] = np.std(td[0:7400])

#Imprimo resultados mezclando frecuencias
print("\nMedia mezclando frecs")
print(meanMixFreq)
print("Desviación mezclando frecs")
print(stdMixFreq)

###################################################################################################################
### CALCULO DE DISTANCIAS

# Creo vector de distancias (el largo es uno menos q las medidas realizadas pues se toma como referencia los resultados a 0 metros)
distancias = list(range(len(paths)-1))
for i in range(len(distancias)):
	distancias[i] = (meanMixFreq[i+1] - meanMixFreq[0])*TICKS_TO_METER
print('Distancias calculadas')
print(distancias)

###################################################################################################################
### GRAFICAS
#Histogramas

pyplot.figure('Histogramas')
subplot = 321
for ticks in ticksMixFreq:
	pyplot.subplot(subplot)
	pyplot.hist(ticks)
	title = 'Results for ' + str(metros[ticksMixFreq.index(ticks)]) + ' meters'
	xlabel = 'Meters'
	ylabel = 'Num. of samples'
	pyplot.title(title)
	pyplot.xlabel(xlabel)
	pyplot.ylabel(ylabel)
	subplot += 1

#Boxplots
#Para los resultados mezclando frecuencias
pyplot.figure('Boxplot Mix Freq')
pyplot.boxplot(ticksMixFreq[0:7400], positions = metros, showmeans = True, meanline = True)
pyplot.title('Mixing frequencies')
pyplot.xlabel('Meters')
pyplot.ylabel('Ticks')
# pyplot.plot(list(range(1,1+len(meanMixFreq))), meanMixFreq,'rs')

#Para cada frecuencia
pyplot.figure('Boxplots')
subplot = 231
for i in range(len(freq)):

	pyplot.subplot(subplot)
	pyplot.boxplot(ticksPerFreq[:][i], positions = metros, showmeans = True, meanline = True)
	pyplot.title(str(freq[i]) + ' kHz')
	pyplot.xlabel('Meters')
	pyplot.ylabel('Ticks')
	subplot += 1
pyplot.show()
