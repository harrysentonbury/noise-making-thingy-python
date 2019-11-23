
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
        return ramp_2 * np.sin(fm * x)

    def lfo_osc_wave():
        return lfo * np.sin(fm * x)

    def ramp_3_fm2():
        return ramp_3 * np.sin(fm2 * x)

    def sine_wave(mod):
        y = np.sin(x * freq + mod)
        return y

    def triangle(mod):
        y = 2 / np.pi * np.arcsin(np.sin(freq * x + mod))
        return y

    def noise(ramp):
        y = np.random.normal(0, 0.4, array_size,)
        y = np.clip(y, a_min=-1.0, a_max=1.0) * (ramp * 0.1)
        return y

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
    ramp3_divizor = float(scale_ramp3_size.get())

    x = np.linspace(0, duration * 2 * np.pi, duration * sample_rate)    # f(x)
    array_size = int(duration * sample_rate)
    # get tk variables from lines 145 -> 150
    choose = bool_choice.get()
    choose_1 = bool_choice_1.get()
    choose_2 = bool_choice_2.get()
    choose_3 = int_choice_3.get()
    choose_wave = bool_choice_wave.get()

    ramp3_size = int(sample_rate // ramp3_divizor)
    ones3_size = sample_rate - ramp3_size

    ramp_0 = np.logspace(0, 1, duration * sample_rate, base=5)
    ramp_1 = np.logspace(1, 0, duration * sample_rate, base=5)
    ramp_2 = np.logspace(0, 1, duration * sample_rate) * ramp_amount
    ramp_3 = np.concatenate((np.logspace(1, 0, duration * ramp3_size),
                             np.ones(int(duration * ones3_size))))
    lfo = np.sin(x * speed) * lfo_amount

    # wave selector
    if choose_wave is True:
        if choose_2 is False:
            if choose is True:
                waveform = triangle(lfo_osc_wave())
            if choose is False:
                waveform = triangle(ramp_2_osc())
        if choose_2 is True:
            if choose is False:
                waveform = 2 / np.pi * np.arcsin(np.sin(x * freq + ramp_2 * np.sin(
                    fm * x + ramp_3_fm2())))
            if choose is True:
                waveform = 2 / np.pi * np.arcsin(np.sin(x * freq + lfo * np.sin(
                    fm * x + ramp_3_fm2())))

    if choose_wave is False:
        if choose_2 is False:
            if choose is True:
                waveform = sine_wave(lfo_osc_wave())
            if choose is False:
                waveform = sine_wave(ramp_2_osc())

        if choose_2 is True:
            if choose is False:
                waveform = np.sin(x * freq + ramp_2 * np.sin(
                    fm * x + ramp_3_fm2()))
            if choose is True:
                waveform = np.sin(x * freq + lfo * np.sin(
                    fm * x + ramp_3_fm2()))

    if choose_3 is 1:
        waveform = waveform + noise(ramp_1)

    if choose_3 is 2:
        waveform = waveform + noise(ramp_0)

    if choose_1 is True:
        waveform = waveform * tremelo()

    waveform = waveform * attenuation * vol

    # print(max(waveform))
    # print(min(waveform))

    sd.play(waveform, sample_rate)
    time.sleep(duration)
    sd.stop()
    play_button.update()                    # Enable play again.
    play_button.config(text="Play", state="normal")

# generators for buttons.


def gen_1():
    n = True
    while True:
        yield n
        n = not n


def gen_3():
    first_val = 0
    n = 1
    while True:
        yield n
        n += 1
        if n == 3:
            n = first_val

# Toggling wave selector bool and setting button colors


def choise_wave():
    bool_choice_wave.set(next(g_wave))
    if bool_choice_wave.get() is True:
        wave_button.config(bg="#728C00", fg="white", text="Triangle")
    if bool_choice_wave.get() is False:
        wave_button.config(bg="#000000", fg="white", text="Sine")


def choise():
    bool_choice.set(next(g))
    if bool_choice.get() is False:
        log_ramp_button.config(bg="#728C00", fg="white", text="Log Ramp")
    if bool_choice.get() is True:
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


def choise_3():
    int_choice_3.set(next(g3))
    if int_choice_3.get() is 1:
        noise_button.config(bg="#728C00", fg="white", text="Noise >")
    if int_choice_3.get() is 0:
        noise_button.config(bg="#000000", fg="white", text="Noise Off")
    if int_choice_3.get() is 2:
        noise_button.config(bg="#728C00", fg="white", text="Noise <")


sample_rate = 44100
attenuation = 0.3

g = gen_1()
g1 = gen_1()
g2 = gen_1()
g3 = gen_3()
g_wave = gen_1()

master = tk.Tk()
master.geometry("800x500")

bool_choice = tk.BooleanVar()
bool_choice.set(False)
bool_choice_1 = tk.BooleanVar()
bool_choice_1.set(False)
bool_choice_2 = tk.BooleanVar()
bool_choice_2.set(False)
int_choice_3 = tk.IntVar()
int_choice_3.set(0)
bool_choice_wave = tk.BooleanVar()
bool_choice_wave.set(False)


duration_labal = tk.Label(master, text='Duration')
freq_labal = tk.Label(master, text='Frequency')
fm_labal = tk.Label(master, text='Fm1')
fm2_labal = tk.Label(master, text='Fm2')
speed_labal = tk.Label(master, text='LFO Speed')
lfo_amount_label = tk.Label(master, text='LFO Amount')
ramp_amount_label = tk.Label(master, text='Ramp Amount')
ramp3_size_label = tk.Label(master, text='Ramp3 Time Ratio')
wave_label = tk.Label(master, text='Wave Shape')

trem_speed_label = tk.Label(master, text='Trem Speed')
vol_label = tk.Label(master, text='Volume')
trem_amount_label = tk.Label(master, text='Trem Amount')

scale_duration = tk.Scale(master, from_=0.5, to=20, resolution=0.25,
                          orient=tk.HORIZONTAL, length=200)
scale_freq = tk.Scale(master, from_=50, to=510, resolution=10, orient=tk.HORIZONTAL, length=200)
scale_fm = tk.Scale(master, from_=10, to=250, resolution=5, orient=tk.HORIZONTAL, length=200)
scale_fm2 = tk.Scale(master, from_=40, to=400, resolution=5, orient=tk.HORIZONTAL, length=200)
scale_speed = tk.Scale(master, from_=0.05, to=5, resolution=0.05, orient=tk.HORIZONTAL, length=200)
scale_lfo_amount = tk.Scale(master, from_=1.0, to=5.0, resolution=0.2,
                            orient=tk.HORIZONTAL, length=200)
scale_ramp_amount = tk.Scale(master, from_=1.0, to=8, resolution=0.2,
                             orient=tk.HORIZONTAL, length=200)
scale_ramp3_size = tk.Scale(master, from_=1.5, to=10, resolution=0.5,
                            orient=tk.HORIZONTAL, length=200)
scale_duration.set(4.0)
scale_freq.set(440)
scale_fm.set(60)
scale_fm2.set(300)
scale_speed.set(1.0)
scale_ramp3_size.set(2)


scale_vol = tk.Scale(master, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
scale_trem_speed = tk.Scale(master, from_=0.5, to=15, resolution=0.2,
                            orient=tk.HORIZONTAL, length=150)
scale_trem_amount = tk.Scale(master, from_=0.0, to=1.0, resolution=0.1,
                             orient=tk.HORIZONTAL, length=150)
scale_vol.set(0.7)
scale_trem_speed.set(6.0)
scale_trem_amount.set(0.5)

play_button = tk.Button(master, text='Play', bg='#0ba4a4', height=3, width=7, command=play)
log_ramp_button = tk.Button(master, bg="#728C00", fg="white",
                            text="Log Ramp", width=7, command=choise)
tremelo_button = tk.Button(master, bg="#000000", fg="white",
                           text='Trem Off', width=7, command=choise_1)
fm2_button = tk.Button(master, bg="#000000", fg="white", text='FM2 Off', width=7, command=choise_2)
noise_button = tk.Button(master, bg="#000000", fg="white", text='Noise', width=6, command=choise_3)
wave_button = tk.Button(master, bg="#000000", fg="white",
                        text='Sine', width=10, command=choise_wave)

duration_labal.grid(column=0, row=0)
freq_labal.grid(column=0, row=1)
fm_labal.grid(column=0, row=2)
fm2_labal.grid(column=0, row=3)
speed_labal.grid(column=0, row=4)
lfo_amount_label.grid(column=0, row=5)
ramp_amount_label.grid(column=0, row=6)
ramp3_size_label.grid(column=0, row=7)
wave_label.grid(column=3, row=0)

vol_label.grid(column=0, row=9)

scale_duration.grid(column=1, row=0)
scale_freq.grid(column=1, row=1)
scale_fm.grid(column=1, row=2)
scale_fm2.grid(column=1, row=3)
scale_speed.grid(column=1, row=4)
scale_lfo_amount.grid(column=1, row=5)
scale_ramp_amount.grid(column=1, row=6)
scale_ramp3_size.grid(column=1, row=7)

scale_vol.grid(column=1, row=9)

play_button.grid(column=2, row=0)
log_ramp_button.grid(column=2, row=1)
tremelo_button.grid(column=2, row=2)
fm2_button.grid(column=2, row=3)
noise_button.grid(column=2, row=4)
wave_button.grid(column=4, row=0)

trem_speed_label.grid(column=3, row=7)
scale_trem_speed.grid(column=4, row=7)
trem_amount_label.grid(column=3, row=8)
scale_trem_amount.grid(column=4, row=8)

master.mainloop()
