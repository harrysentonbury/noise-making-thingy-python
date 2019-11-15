

import numpy as np
import sounddevice as sd
import time
import tkinter as tk


def play():
    play_button.config(text="Wait", state="disabled")    # disable play button
    play_button.update()

    def tremelo():                              # more of a tremelator!
        trem_adder = 1.0 - trem_amount_value
        return np.sin(x * trem_speed) * trem_amount_value + trem_adder

    def ramp_2_osc():
        return np.sin(x * freq + ramp_2 * np.sin(fm * x))

    def lfo_osc_wave():
        return np.sin(x * freq + lfo * np.sin(fm * x))

    def ramp_2_fm2():
        return ramp_2 * np.sin(fm2 * x)

    freq = float(scale_freq.get())
    fm = float(scale_fm.get())
    fm2 = float(scale_fm2.get())
    speed = float(scale_speed.get())
    duration = float(scale_duration.get())
    lfo_amount = float(scale_lfo_amount.get())
    ramp_amount = float(scale_ramp_amount.get())
    trem_speed = float(scale_trem_speed.get())
    vol = float(scale_vol.get())
    trem_amount_value = float(scale_trem_amount.get())

    x = np.linspace(0, duration * 2 * np.pi, duration * sample_rate)    # f(x)
    # get tk variables from lines 145 -> 150
    choose = bool_choice.get()
    choose_1 = bool_choice_1.get()
    choose_2 = bool_choice_2.get()

    ramp_2 = np.logspace(0, 1, duration * sample_rate) * ramp_amount
    lfo = np.sin(x * speed) * lfo_amount

    # wave selector
    if choose is False and choose_2 is False:
        waveform = lfo_osc_wave()
    if choose is True and choose_2 is False:
        waveform = ramp_2_osc()

    if choose is True and choose_2 is True:
        waveform = np.sin(x * freq + ramp_2 * np.sin(
                          fm * x) + ramp_2_fm2())
    if choose is False and choose_2 is True:
        waveform = np.sin(x * freq + lfo * np.sin(
                          fm * x) + ramp_2_fm2())

    if choose_1 is True:
        waveform = waveform * tremelo()

    waveform = waveform * attenuation * vol

    # print(max(waveform))
    # print(min(waveform))

    sd.play(waveform, sample_rate)
    time.sleep(duration)
    sd.stop()
    play_button.update()
    play_button.config(text="Play", state="normal")

# toggle generators for buttons.


def gen():
    n = False
    while True:
        yield n
        n = not n


def gen_1():
    n = True
    while True:
        yield n
        n = not n


def gen_2():
    n = True
    while True:
        yield n
        n = not n

# Toggling wave selector bool and setting button colors


def choise():
    bool_choice.set(next(g))
    if bool_choice.get() is True:
        log_ramp_button.config(bg="#728C00", fg="white", text="Log Ramp")
    if bool_choice.get() is False:
        log_ramp_button.config(bg="#000000", fg="white", text="Sin LFO")


def choise_1():
    bool_choice_1.set(next(g1))
    if bool_choice_1.get() is True:
        tremelo_button.config(bg="#728C00", fg="white", text="Trem On")
    if bool_choice_1.get() is False:
        tremelo_button.config(bg="#000000", fg="white", text="Trem Off")


def choise_2():
    bool_choice_2.set(next(g2))
    if bool_choice_2.get() is True:
        fm2_button.config(bg="#728C00", fg="white", text="FM2 On")
    if bool_choice_2.get() is False:
        fm2_button.config(bg="#000000", fg="white", text="FM2 Off")


sample_rate = 44100
attenuation = 0.3

g = gen()
g1 = gen_1()
g2 = gen_2()

master = tk.Tk()
master.geometry("750x500")
bool_choice = tk.BooleanVar()
bool_choice.set(True)
bool_choice_1 = tk.BooleanVar()
bool_choice_1.set(False)
bool_choice_2 = tk.BooleanVar()
bool_choice_2.set(False)


duration_labal = tk.Label(master, text='Duration')
freq_labal = tk.Label(master, text='Frequency')
fm_labal = tk.Label(master, text='Fm1')
fm2_labal = tk.Label(master, text='Fm2')
speed_labal = tk.Label(master, text='LFO Speed')
lfo_amount_label = tk.Label(master, text='LFO Amount')
ramp_amount_label = tk.Label(master, text='Ramp Amount')

trem_speed_label = tk.Label(master, text='Trem Speed')
vol_label = tk.Label(master, text='Volume')
trem_amount_label = tk.Label(master, text='Trem Amount')

scale_duration = tk.Scale(master, from_=0.5, to=20, resolution=0.25, orient=tk.HORIZONTAL)
scale_freq = tk.Scale(master, from_=50, to=510, resolution=10, orient=tk.HORIZONTAL)
scale_fm = tk.Scale(master, from_=10, to=250, resolution=5, orient=tk.HORIZONTAL)
scale_fm2 = tk.Scale(master, from_=40, to=400, resolution=5, orient=tk.HORIZONTAL)
scale_speed = tk.Scale(master, from_=0.05, to=5, resolution=0.05, orient=tk.HORIZONTAL)
scale_lfo_amount = tk.Scale(master, from_=1.0, to=10, resolution=0.2, orient=tk.HORIZONTAL)
scale_ramp_amount = tk.Scale(master, from_=1.0, to=8, resolution=0.2, orient=tk.HORIZONTAL)

scale_vol = tk.Scale(master, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL)
scale_trem_speed = tk.Scale(master, from_=0.5, to=15, resolution=0.2, orient=tk.HORIZONTAL)
scale_trem_amount = tk.Scale(master, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL)

play_button = tk.Button(master, text='Play', command=play)
log_ramp_button = tk.Button(master, bg="#728C00", fg="white", text="Log Ramp", command=choise)
tremelo_button = tk.Button(master, bg="#000000", fg="white", text='Trem Off', command=choise_1)
fm2_button = tk.Button(master, bg="#000000", fg="white", text='FM2 Off', command=choise_2)

duration_labal.grid(column=0, row=0)
freq_labal.grid(column=0, row=1)
fm_labal.grid(column=0, row=2)
fm2_labal.grid(column=0, row=3)
speed_labal.grid(column=0, row=4)
lfo_amount_label.grid(column=0, row=5)
ramp_amount_label.grid(column=0, row=6)

vol_label.grid(column=0, row=8)

scale_duration.grid(column=1, row=0)
scale_freq.grid(column=1, row=1)
scale_fm.grid(column=1, row=2)
scale_fm2.grid(column=1, row=3)
scale_speed.grid(column=1, row=4)
scale_lfo_amount.grid(column=1, row=5)
scale_ramp_amount.grid(column=1, row=6)

scale_vol.grid(column=1, row=8)

play_button.grid(column=2, row=0)
log_ramp_button.grid(column=2, row=1)
tremelo_button.grid(column=2, row=2)
fm2_button.grid(column=2, row=3)

trem_speed_label.grid(column=3, row=6)
scale_trem_speed.grid(column=4, row=6)
trem_amount_label.grid(column=3, row=7)
scale_trem_amount.grid(column=4, row=7)

master.mainloop()
