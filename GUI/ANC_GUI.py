import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from LMSFilter import LMS
from RLS import RLS
from system import system
import numpy as np

from pygame import mixer
from tkinter import *
import tkinter.font as font
from tkinter import filedialog
import pygame
import os

import scipy as sp
from audio_converter import *

#DSP PROJECT -> SHOW PAGE
#CONST
clear = lambda: os.system('cls')
clear()
sampleRate = 44100

# Filters on 0 input + noise
print("Calculating with 0 on input")
t = np.linspace(0.01, 10, 10000)

zeros_desired = np.zeros(t.size)
test_noise = np.random.rand(np.size(zeros_desired))*2 - np.ones(np.size(zeros_desired))
zeros_noised = zeros_desired + test_noise
k = 6
start = test_noise[k:0:-1]

LMS_zeros = LMS(start, N=k, u=0.01)
RLS_zeros = RLS(start, N=k, l=0.999)

sys_lms = system(test_noise, zeros_noised, LMS_zeros)
sys_rls = system(test_noise, zeros_noised, RLS0=RLS_zeros)

e_lms, y_lms = sys_lms.calculate_LMS()
e_rls, y_rls = sys_rls.calculate_RLS()

audio_converter.data_to_wav("zeros.wav", sampleRate, zeros_desired, zeros_desired) # Desired
audio_converter.data_to_wav("zeros+noise.wav", sampleRate, zeros_noised, zeros_noised) # Desired + noise
audio_converter.data_to_wav("zeros_LMS.wav", sampleRate, e_lms, e_lms) # Filtered LMS
audio_converter.data_to_wav("zeros_RLS.wav", sampleRate, e_rls, e_rls) # Filtered RLS

#
#Filter on audio_sample.wav + noise input
#

print("Calculating with sound on input and noise")

sample_Rate, data_L, data_R = audio_converter.wav_to_data("audio_sample.wav")
test_noise_sample = (np.random.rand(np.size(data_L))-0.5)*np.amax(data_L)/4
sample_noised_L = data_L + test_noise_sample

start_sample = test_noise_sample[k:0:-1]
LMS_sample = LMS(start_sample, k, u=0.01)
RLS_sample = RLS(start_sample, k, l=0.999)

sys_lms_sample = system(test_noise_sample, sample_noised_L, LMS_sample)
sys_rls_sample = system(test_noise_sample, sample_noised_L, RLS0=RLS_sample)

e_lms_sample, y_lms_sample = sys_lms_sample.calculate_LMS()
e_rls_sample, y_rls_sample = sys_rls_sample.calculate_RLS()


audio_converter.data_to_wav("audio_sample+noise.wav", sampleRate, sample_noised_L, sample_noised_L) # Desired + noise
audio_converter.data_to_wav("audio_sample_LMS.wav", sampleRate, e_lms_sample, e_lms_sample) # Filtered LMS
audio_converter.data_to_wav("audio_sample_RLS.wav", sampleRate, e_rls_sample, e_rls_sample) # Filtered RLS

#
# Filter on audio_sample.wav + voice
#
sampleRate, voice_L, voice_R = audio_converter.wav_to_data("mowa.wav") # Filtered RLS

voice_L = 2.5 * voice_L[0:data_L.size]
voice_noised_L = data_L + voice_L
start_voice = voice_L[k:0:-1]
LMS_voice = LMS(start_voice, k, u=0.01)
RLS_voice = RLS(start_voice, k, l=0.999)

sys_lms_voice = system(voice_L, voice_noised_L, LMS_voice)
sys_rls_voice = system(voice_L, voice_noised_L, RLS0=RLS_voice)

e_lms_voice, y_lms_voice = sys_lms_voice.calculate_LMS()
e_rls_voice, y_rls_voice = sys_rls_voice.calculate_RLS()

audio_converter.data_to_wav("audio_sample+voice.wav", sampleRate, voice_noised_L, voice_noised_L) # Desired + voice
audio_converter.data_to_wav("audio_sample_voice_LMS.wav", sampleRate, e_lms_voice, e_lms_voice) # Filtered LMS
audio_converter.data_to_wav("audio_sample_voice_RLS.wav", sampleRate, e_rls_voice, e_rls_voice) # Filtered RLS




#
# GUI
#

class windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        print("Starting GUI...")

        mixer.init()
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("Design Lab Application")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.frames = {}
        for F in (MainPage, LMS_zero, RLS_zero, LMS_sound_noise, RLS_sound_noise, LMS_sound_sound, RLS_sound_sound):
            print("Loading window " + str(F)[16:-2] + "...")
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
    def plot(self, data, col_p, row_p, chart_label, valueP="linear"):
        figure = plt.Figure(figsize=(10, 2.5), dpi=100)
        figure.subplots_adjust(left=0.06, bottom=0.11, right=0.985, top=0.91, wspace=0, hspace=0) 
        #w, h space up -> dunno?
        #left up -> charts shrink with more white space to them
        #r up -> right borter shrinks
        # uu -> more space over chart + title apperas
        # bu -> more white space below chart

        ax = figure.add_subplot(111)

        chart = FigureCanvasTkAgg(figure, self)
        chart.get_tk_widget().grid(column = col_p, row = row_p, rowspan=2)
        
        ax.plot(data, label=chart_label )
        ax.plot(kind='bar', legend=True, ax=ax)
        ax.set_title(chart_label)
        ax.set_xlim(left=0-len(data)*0.01, right=len(data)*1.01)
        ax.set_yscale(value=valueP)
        #plot chart

        return chart
    
    def Play(path):
        mixer.music.load(path) #this path will be provided in function
        mixer.music.play()

    def Stop():
        mixer.music.stop()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        mixer.init()
        tk.Frame.__init__(self, parent)
        
        label = tk.Label(self, text="Main Page", font=40, padx=50)
        label.grid(row=1, column=1)
        
        switch_window_button_LMS_zero = tk.Button(self, text="Go to the LMS Page", command=lambda: controller.show_frame(LMS_zero), font=30)
        switch_window_button_LMS_zero.grid(row=1, column=2, pady=30, padx=20)
        
        switch_window_button_RLS_zero = tk.Button(self, text="Go to the RLS Page", command=lambda: controller.show_frame(RLS_zero), font=30)
        switch_window_button_RLS_zero.grid(row=1, column=3, pady=30, padx=20) 

        switch_window_button_LMS_sound_noise = tk.Button(self, text="Go to the LMS noise + audio", command=lambda: controller.show_frame(LMS_sound_noise), font=30)
        switch_window_button_LMS_sound_noise.grid(row=2, column=2, pady=30, padx=20)

        switch_window_button_RLS_sound_noise = tk.Button(self, text="Go to the RLS noise + audio", command=lambda: controller.show_frame(RLS_sound_noise), font=30)
        switch_window_button_RLS_sound_noise.grid(row=2, column=3, pady=30, padx=20)
        
        switch_window_button_LMS_sound_sound = tk.Button(self, text="Go to the LMS voice + audio", command=lambda: controller.show_frame(LMS_sound_sound), font=30)
        switch_window_button_LMS_sound_sound.grid(row=3, column=2, pady=30, padx=20)
        
        switch_window_button_RLS_sound_sound = tk.Button(self, text="Go to the RLS voice + audio", command=lambda: controller.show_frame(RLS_sound_sound), font=30)
        switch_window_button_RLS_sound_sound.grid(row=3, column=3, pady=30, padx=20)

class LMS_zero(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        mixer.init()
        label = tk.Label(self, text="This is the LMS input zero", font=20)
        label.grid(row=1, column=1)

        switch_window_button = tk.Button(
            self,
            text="Go to the Menu",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.grid(column=1, padx= 10, pady= 10)

        figure_data =  windows.plot(self, zeros_desired, 2, 1, "Desired")
  
        figure_error = windows.plot(self, zeros_noised, 2, 3, "Desired + Noise")

        figure_signal = windows.plot(self, e_lms, 2, 5, "Filtered", "log")

class RLS_zero(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        mixer.init()
        label = tk.Label(self, text="This is the RLS Page", font=20)
        label.grid(row=1, column=1)

        switch_window_button = tk.Button(
            self,
            text="Go to the Menu",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.grid(column=1, padx= 10, pady= 10)

        figure_data =  windows.plot(self, zeros_desired, 2, 1, "Desired") # porzadany-> wejsciowy -> przefiltrowany
  
        figure_error = windows.plot(self, zeros_noised, 2, 3, "Desired + Noise", "log")

        figure_signal = windows.plot(self, e_rls, 2, 5, "Filtered", "log")

class LMS_sound_noise(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        mixer.init()
        label = tk.Label(self, text="This is the LMS input sample.wav + noise", font=20)
        label.grid(row=1, column=1)

        switch_window_button = tk.Button(
            self,
            text="Go to the Menu",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.grid(column=1, padx= 10, pady= 10)

        figure_data =  windows.plot(self, data_L, 2, 1, "Desired")
        play_button=Button(self,text="Play",width =6,command= lambda: windows.Play("audio_sample.wav"), font='Belda')
        play_button.grid(row=1,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=1,column=4)
  
        figure_error = windows.plot(self, sample_noised_L, 2, 3, "Desired + Noise")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample+noise.wav"), font='Belda')
        play_button.grid(row=3,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=3,column=4)

        figure_signal = windows.plot(self, e_lms_sample, 2, 5, "Filtered")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample_LMS.wav"), font='Belda')
        play_button.grid(row=5,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=5,column=4)

class RLS_sound_noise(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        mixer.init()
        label = tk.Label(self, text="This is the RLS input sample.wav + noise", font=20)
        label.grid(row=1, column=1)

        switch_window_button = tk.Button(
            self,
            text="Go to the Menu",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.grid(column=1, padx= 10, pady= 10)

        figure_data =  windows.plot(self, data_L, 2, 1, "Desired")
        play_button=Button(self,text="Play",width =6,command= lambda: windows.Play("audio_sample.wav"), font='Belda')
        play_button.grid(row=1,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=1,column=4)
  
        figure_error = windows.plot(self, sample_noised_L, 2, 3, "Desired + Noise")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample+noise.wav"), font='Belda')
        play_button.grid(row=3,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=3,column=4)

        figure_signal = windows.plot(self, e_rls_sample, 2, 5, "Filtered")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample_RLS.wav"), font='Belda')
        play_button.grid(row=5,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=5,column=4)
        
class RLS_sound_sound(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        mixer.init()
        label = tk.Label(self, text="This is the RLS input sample.wav + voice", font=20)
        label.grid(row=1, column=1)

        switch_window_button = tk.Button(
            self,
            text="Go to the Menu",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.grid(column=1, padx= 10, pady= 10)

        figure_data =  windows.plot(self, data_L, 2, 1, "Desired")
        play_button=Button(self,text="Play",width =6,command= lambda: windows.Play("audio_sample.wav"), font='Belda')
        play_button.grid(row=1,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=1,column=4)
  
        figure_error = windows.plot(self, sample_noised_L, 2, 3, "Desired + Voice")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample+voice.wav"), font='Belda')
        play_button.grid(row=3,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=3,column=4)

        figure_signal = windows.plot(self, e_rls_voice, 2, 5, "Filtered")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample_voice_RLS.wav"), font='Belda')
        play_button.grid(row=5,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=5,column=4)
        
class LMS_sound_sound(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        mixer.init()
        label = tk.Label(self, text="This is the LMS input sample.wav + voice", font=20)
        label.grid(row=1, column=1)

        switch_window_button = tk.Button(
            self,
            text="Go to the Menu",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.grid(column=1, padx= 10, pady= 10)

        figure_data =  windows.plot(self, data_L, 2, 1, "Desired")
        play_button=Button(self,text="Play",width =6,command= lambda: windows.Play("audio_sample.wav"), font='Belda')
        play_button.grid(row=1,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=1,column=4)
  
        figure_error = windows.plot(self, sample_noised_L, 2, 3, "Desired + Voice")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample+voice.wav"), font='Belda')
        play_button.grid(row=3,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=3,column=4)

        figure_signal = windows.plot(self, e_lms_voice, 2, 5, "Filtered")
        play_button=Button(self,text="Play",width =6,command=lambda: windows.Play("audio_sample_voice_LMS.wav"), font='Belda')
        play_button.grid(row=5,column=3)
        pause_button=Button(self,text="Stop",width =6,command=windows.Stop, font='Belda')
        pause_button.grid(row=5,column=4)

#GUI START

testObj = windows()
testObj.mainloop()