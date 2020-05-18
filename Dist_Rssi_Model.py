import matplotlib.pyplot as pyp
import numpy as np
import scipy as sp
import json
from os import listdir
from os.path import isfile, join
from scipy.optimize import curve_fit
import numpy as np

DATA = list() #list of lists
CURR_ARR_MEAN = None
CURR_ARR_STD = None

def filterFunc(val):
    return (val > CURR_ARR_MEAN - CURR_ARR_STD and val < CURR_ARR_MEAN + CURR_ARR_STD)

'''
def generateDataRandom(): # SE HA DE ELIMINAR CUANDO TOME LOS DATOS REALES
    var = -56
    for _ in range(0,40):
        arr = np.random.randint(-120, var, size=40)
        DATA.append(arr)
        var -= np.random.randint(0,4)
'''

def func_model(x, A, n):
    # MODEL FORMULA
    # RSSI = −10·n·log(d) + A

    # A : average measured RSSI at 1 meter. --> -58.95 dBm

    return -10 * n * np.log10(x) + A

def loadData():

    fileslist = [f for f in listdir('./calibrationFiles/') if isfile(join('./calibrationFiles/', f))]
    fileslist.sort()
    file_10 = fileslist.pop(0)
    fileslist.append(file_10)
    print(fileslist)
    for file in fileslist:
        with open('calibrationFiles/'+file,"r") as fl:
            js_data = json.load(fl) # pair <devName, RSSI> array for this distance
            row_data = [] # array of RSSI measurements
            for obj in js_data:
                row_data.append(int(obj["RSSI"]))
            row_data.sort()
            DATA.append(row_data)

    print(np.mean(DATA[1]))

def testNormData():
    SIGMA = []
    for i in range(0,10,1):
        SIGMA.append(np.std(DATA[i]))
    pyp.hist(SIGMA)
    pyp.show()
    '''
    for i in range(0,10,1):
        pyp.hist(sorted(DATA[i]))
        pyp.show()
    '''

def dataFiltering():
    # filtramos los datos
    i = 0
    for arr in DATA:
        global CURR_ARR_MEAN
        global CURR_ARR_STD
        CURR_ARR_MEAN = np.mean(arr)
        CURR_ARR_STD = np.std(arr)
        DATA[i] = list(filter(filterFunc, arr))
        i = i + 1


def curveFitting():

    #establecemos el eje X : las distancias en metros a las que tomamos datos.
    xdata = np.linspace(1, 10, num=10)  # 1 to 10 meters spaced 1 meter

    # hacemos la media de las rssi obtenidas a cada distancia

    ydata = [np.mean(arr) for arr in DATA]
    sigma = [np.std(arr) for arr in DATA]
    print(ydata)
    print(sigma)
    # Preparamos los parámetros para crear la función que se
    # adecuará al modelo teórico rssi-distancia
    A = ydata[0]
    n = 4
    y = func_model(xdata, A, n)

    pyp.plot(xdata, y, 'g-', label='ideal: A - 10*n*log(x)')
    # HACEMOS PLOT DE NUESTROS DATOS (DATOS EXPERIMENTALES)
    pyp.plot(xdata, ydata, 'b-', label='data obtained')

    #obtenemos los valores de los parámetros de la funcion óptimos
    #asi como la covariancia de los datos.
    popt, pcov = curve_fit(func_model, xdata, ydata, sigma=sigma, absolute_sigma=True, bounds=([-100,0],[0,10]))

    #obtiene desviacion tipica
    print(popt)
    print(pcov)
    print(np.sqrt(np.diag(pcov)))

    pyp.plot(xdata, func_model(xdata, *popt), 'r-', label='fit: %5.3f - 10*%5.3f*log(x)' % tuple(popt))

    pyp.xlabel('x')
    pyp.ylabel('y')
    pyp.legend()
    pyp.show()


def main():
    loadData()
    testNormData()
  #  dataFiltering()

    curveFitting()


if __name__ == '__main__':
    main()