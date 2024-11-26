import numpy as np
import matplotlib.pyplot as plot
import pylab as pl
from LMSFilter import LMS
from RLS import RLS

class system:

    y = np.empty([])
    e = np.empty([])

    x = np.empty([])
    d = np.empty([])

    RLS1 = RLS([])
    LMS1 = LMS([])

    s = 0
    k_r = 0
    k_l = 0

    def __init__(self, x, d, LMS0=LMS([]), RLS0=RLS([])):

        self.RLS1 = RLS0
        self.LMS1 = LMS0
        self.x = x
        self.d = d
        
        self.s = np.size(self.x)

        self.y = np.zeros(self.s)
        self.e = np.zeros(self.s)

        self.k_l = self.LMS1.N
        self.k_r = self.RLS1.N

    def calculate_RLS(self):
        for n in range(self.RLS1.N, self.s):
            self.RLS1.insert(self.x[n])
            self.y[n-self.k_r] = self.RLS1.estimate()
            self.e[n-self.k_r] = self.d[n] - self.y[n-self.k_r]
            self.RLS1.update(self.e[n-self.k_r])
        return self.e, self.y

    def calculate_LMS(self):
        for n in range(self.LMS1.N, self.s):
            self.LMS1.insert(self.x[n])
            self.y[n-self.k_l] = self.LMS1.estimate()
            self.e[n-self.k_l] = self.d[n] - self.y[n-self.k_l]
            self.LMS1.update(self.e[n-self.k_l])
        return self.e, self.y

    def plot(self, d, e, y):
        fig, ax = plot.subplots( nrows=3 )
        fig.set_size_inches( 24, 16 )
        fig.suptitle( "Result of adaptive filtering", fontsize=12 )
        ax[0].plot( d, label="desired signal")
        ax[0].legend()

        ax[1].plot( e, label="filtered signal" )
        ax[1].plot( self.d, label="raw signal", alpha = 0.5 )
        ax[1].legend()

        ax[2].plot(y, label = "anti-sound")
        ax[2].legend()
        pl.show()