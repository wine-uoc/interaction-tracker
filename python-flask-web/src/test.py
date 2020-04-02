from sympy.geometry.ellipse import Circle
from sympy.geometry.polygon import Point, Polygon, Triangle
import numpy as np
from scipy.optimize import fsolve
from sympy.solvers import solve
from sympy import Symbol
from sympy.solvers import linsolve
from sympy.geometry import Line
from sympy import Eq

c1 = Circle(Point(0, 0), 0.08462309706809855)
c2 = Circle(Point(1, 0), 0.5516666664845306)
c3 = Circle(Point(0, 1), 0.5778696787291522)

x = Symbol('x')
y = Symbol('y')
f = solve(c1.equation(x, y) - c2.equation(x, y), [x, y], dict=True)
print(f[0][x].evalf(5))

#l = Line(Eq(y - 0.15, 0))
#print(l.equation())
# o = c2.intersection(c3)
# print(o.)
# print(inters)

a = tuple(Point(0.14, 0.15).evalf(4))
print(a)
p1, p2, p3 = Point(0.35, 0.335), Point(0.35, 0.34), Point(0.355, 0.34)
t = Triangle(p1, p2, p3)
# print(t.incenter.evalf(5))
