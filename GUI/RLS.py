import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import os #only for development

clear = lambda: os.system('cls')
clear() #only for dev

class RLS:

    # RLS params
    N = 10           # filter lenght
    l = 0.99         # weight param

    S = np.zeros([N,N])     # amplifying matrix
    x = np.zeros(N)         # input
    w = np.zeros(N)

    def __init__(self, start_samples, N = 10, l = 0.99):
        self.N = N
        self.l = l
        self.S = np.eye(self.N) * 100
        self.w = np.zeros(N)
        self.x = start_samples

    def insert(self, new_sample):
        self.x = np.roll(self.x,1)
        self.x[0] = new_sample

    def update(self, e):
        psi = self.S @ self.x
        self.S = (self.S - (np.outer(psi, psi))/(self.l + np.inner(psi, self.x)))/self.l

        self.w += e * (self.S @ self.x)

    def estimate(self):
        return np.inner(self.x, self.w)