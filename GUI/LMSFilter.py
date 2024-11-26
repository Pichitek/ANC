import numpy as np
import scipy as sp
import matplotlib as plot
import os #only for development


clear = lambda: os.system('cls')
clear() #only for dev

class LMS:
    
    # LMS params
    N = 0          # filter length
    u = 0          # starting learing rate

    x = np.zeros([N])
    h = np.zeros([N])

    def __init__(self, start_samples, N = 10, u = 0.01):
        self.N = N
        self.u = u
        self.x = start_samples
        self.h = np.zeros(self.N) #starting FIR coefficient

    def update(self, e):
        gamma = 1 # used to avoid devision by 0
        mu = self.u/(gamma + np.dot(self.x, self.x))
        self.h += mu * e * self.x

    def estimate(self):
        return np.dot(self.x,self.h)

    def insert(self, new_sample):
        self.x = np.roll(self.x,1)
        self.x[0] = new_sample