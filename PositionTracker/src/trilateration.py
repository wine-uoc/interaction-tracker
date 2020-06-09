import numpy as np
from scipy.optimize import fsolve, minimize
from scipy.linalg import null_space
import time


def myFunc(xy, x1, y1, r1, x2, y2, r2, x3, y3, r3):
    x = xy[0]
    y = xy[1]

    f0 = (x - x1) ** 2 + (y - y1) ** 2 - r1 ** 2 - ((x - x2) ** 2 + (y - y2) ** 2 - r2 ** 2)
    f1 = (x - x2) ** 2 + (y - y2) ** 2 - r2 ** 2 - ((x - x3) ** 2 + (y - y3) ** 2 - r3 ** 2)
    #f2 = (x - x3) ** 2 + (y - y3) ** 2 - r3 ** 2 - ((x - x1) ** 2 + (y - y1) ** 2 - r1 ** 2)

    return np.array([f0, f1])

#Euclidean distance between 2 points.
def great_circle_distance(x1, y1, x2, y2):
    return np.sqrt(pow(x1-x2,2.0)+pow(y1-y2,2.0))


def mse(x, locations, distances):
     mse = 0.0
     for location, distance in zip(locations, distances):
         distance_calculated = great_circle_distance(x[0], x[1], location[0], location[1])
         mse += pow(distance_calculated - distance, 2.0)
     return mse / len(locations)



x1 = 0
y1 = 0
r1 = 0.5

x2 = 1
y2 = 1
r2 = 1

x3 = 1
y3 = 0
r3 = 2

locations = [(x1,y1),(x2,y2),(x3,y3)]
distances = [r1,r2,r3]
'''
A = np.array([[1, -2*x1, -2*y1],
              [1, -2*x2, -2*y2],
              [1, -2*x3, -2*y3]])

b = np.array([[r1**2 - x1**2 - y1**2],
              [r2**2 - x2**2 - y1**2],
              [r3**2 - x3**2 - y1**2]])

'''

init_guess = np.array([0, 0])
t_ini = time.time()*1000
res = minimize(mse, init_guess, args=(locations,distances),method='L-BFGS-B',options={'maxiter':1e+100})
t_fin = time.time()*1000
print("time elapsed: "+str(t_fin-t_ini))
print(res)


'''
p = A*np.linalg.inv(np.transpose(A)*A)*b
x = np.linalg.lstsq(A,b,rcond=None)
print(x)
print(p)
'''
