import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from math import *


def decompose(func, n=50):
    A = list()
    B = list()
    for i in range(n):
        fc = lambda x: func(x) * cos(i * x)
        fs = lambda x: func(x) * sin(i * x)
        A.append(quad(fc, -np.pi, np.pi)[0] * (1.0 / np.pi))
        B.append(quad(fs, -np.pi, np.pi)[0] * (1.0 / np.pi))
    A[0] /= 2
    return A, B


def fourier(x, A, B):
    sum = 0
    for i in range(len(A)):
        sum += (A[i] * np.cos(i * x) + B[i] * np.sin(i * x))
    return sum


x = np.arange(-np.pi, np.pi, 0.001)
func = lambda x: (x - 0.5) ** 2
A, B = decompose(func)

plt.plot(x, fourier(x, A, B), 'g')
plt.plot(x, func(x), 'r--')
plt.title("fourier series for square wave")

plt.show()
