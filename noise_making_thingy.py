
""" Python thingy, a bit like a synthesizer """

import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd
import time
import pickle
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


def play(save=False):
    """Gets values and selections from gui then plays or saves"""
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
        y = np.random.normal(0, 0.4, len(x))
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
    roller = int(scale_roll.get())
    fade_size = 5000 + int(duration * sample_rate * float(scale_fade.get()))
    noise_shape = float(scale_noise_shape.get())
    device_arg = device_num.get()

    x = np.linspace(0, duration * 2 * np.pi, duration * sample_rate)    # f(x)

    # get tk variables from lines 145 -> 150
    choose = bool_choice.get()
    choose_1 = bool_choice_1.get()
    choose_2 = bool_choice_2.get()
    choose_3 = int_choice_3.get()
    choose_wave = bool_choice_wave.get()

    ramp_3 = np.ones(len(x))
    ramp_3_ramp = np.logspace(1, 0, int(duration * sample_rate // ramp3_divizor))

    ramp_0 = np.logspace(noise_shape, 1, duration * sample_rate, base=5)
    ramp_1 = np.logspace(1, noise_shape, duration * sample_rate, base=5)
    ramp_2 = np.logspace(0, 1, duration * sample_rate) * ramp_amount
    ramp_3[: len(ramp_3_ramp)] = ramp_3_ramp
    fade_ramp = np.linspace(1, 0, fade_size if fade_size < 120000 else 120000)

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
                waveform = 2 / np.pi * np.arcsin(np.sin(x * freq + ramp_2 * 2 / np.pi * np.arcsin(
                                                 np.sin(x * fm + ramp_3_fm2()))))
            if choose is True:
                waveform = 2 / np.pi * np.arcsin(np.sin(x * freq + lfo * 2 / np.pi * np.arcsin(
                                                 np.sin(x * fm + ramp_3_fm2()))))  # bollox

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
    waveform1 = np.roll(waveform, roller)
    waveform1[:roller] = 0
    waveform[- len(fade_ramp):] *= fade_ramp
    waveform1[- len(fade_ramp):] *= fade_ramp
    waveform_stereo = np.vstack((waveform, waveform1)).T

    if save is True:
        stamp = file_name.get()
        if len(stamp) == 0:
            stamp = "{}.wav".format(str(time.time())[:10])
        else:
            stamp = "{}.wav".format(stamp)

        # write_waveform = np.int16(waveform_stereo * 32767)
        # write(stamp, sample_rate, write_waveform)
        print('writing {}'.format(stamp))

        file_name.set("")
        play_button.update()
        play_button.config(text="Play", state="normal")

        saver_window.destroy()
        if ms_win is not None:
            ms_win.destroy()
        message_win("File Saved", "File saved as {}".format(stamp))
    else:
        try:
            print(device_arg)
            if device_arg < 0:
                sd.play(waveform_stereo, sample_rate)
            else:
                sd.play(waveform_stereo, sample_rate, device=device_arg)
        except sd.PortAudioError:
            if ms_win is not None:
                ms_win.destroy()
            message_win(
                "PortAudioError", """Driver id not valid! Type id number from the list.
                 Or Click Reset to Default Driver""")
            device_l()

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


def choise_save():
    play(save=True)  # flagged to write wav file


def stop_it():
    sd.stop()


def message_win_func(mtitle, blah):

    def closer():
        ms_win.destroy()

    global ms_win
    ms_win = tk.Toplevel(master)
    ms_win.title(mtitle)
    label = tk.Label(ms_win, text=blah, font='Times 20')
    button = tk.Button(ms_win, text='OK', width=6, bg="#728C00", fg="white", command=closer)

    label.pack(padx=30, pady=10)
    button.pack(pady=20)
    ms_win.lift()


def message_win(mtitle, blah):
    if ms_win is None:
        message_win_func(mtitle, blah)
        return
    try:
        ms_win.lift()
    except tk.TclError:
        message_win_func(mtitle, blah)


def device_window_func():
    """Dialog for viewing and selecting output drivers"""
    global device_window
    device_window = tk.Toplevel(master)
    device_window.title('Device Selection')
    device_window.config(bg='#afb4b5')

    def reset_d():
        device_entry.delete(0, last='end')
        device_num.set(-1)

    def driver_setter():
        try:
            num = int(device_entry.get())
            device_num.set(num)
            print(device_num.get())
        except ValueError:
            device_num.set(-1)
            device_entry.delete(0, last="end")
            if ms_win is not None:
                ms_win.destroy()
            message_win(mtitle="ValueError",
                        blah="Must be integer number from list of available devices")

    a = repr(sd.query_devices())
    b = a.split("\n")

    dframe = tk.Frame(device_window, relief=tk.RAISED, bd=2, bg='#afb4b5')
    label_0 = tk.Label(device_window, text='List of availible devices',
                       bg='#afb4b5', font='Times 20')
    scrollbar = tk.Scrollbar(device_window)
    label_2 = tk.Label(dframe, text='Enter device number', bg='#afb4b5', font='Times 15')
    set_device_button = tk.Button(dframe, text='Select', height=3, command=driver_setter)
    reset_button = tk.Button(device_window, text='Reset to Default Driver', command=reset_d)
    device_entry = tk.Entry(dframe, width=10)
    device_entry.focus_set()
    list_bx = tk.Listbox(device_window, yscrollcommand=scrollbar.set, width=60, height=25)
    for i in range(len(b)):
        list_bx.insert(tk.END, b[i])

    label_0.grid(row=0, column=0, columnspan=2)
    list_bx.grid(row=1, column=0, columnspan=2)
    scrollbar.grid(row=1, column=2, sticky=tk.N+tk.S)
    label_2.grid(row=2, column=0, sticky='ne', pady=8, padx=5)
    dframe.grid(row=2, column=0, rowspan=2, columnspan=2, sticky='w', pady=5, padx=20)
    set_device_button.grid(row=3, column=1, sticky='w', pady=5, padx=5)
    device_entry.grid(row=2, column=1, sticky='w', pady=8, padx=5)
    reset_button.grid(row=4, column=1, sticky='w', pady=8)
    scrollbar.config(command=list_bx.yview)

    device_window.lift()


def device_l():
    if device_window is None:
        device_window_func()
        return
    try:
        device_window.lift()
    except tk.TclError:
        device_window_func()


def saver_window_func():
    """dialog box for saving as .wav"""

    def on_cancel():
        save_entry.delete(0, last='end')
        file_name.set("")
        saver_window.destroy()

    global saver_window
    saver_window = tk.Toplevel(master)
    saver_window.title('Save As .wav File')
    saver_window.geometry('500x200')

    instruct_label = tk.Label(
        saver_window, text="Enter a file name and click Save", font='Times 15')
    save_button = tk.Button(saver_window, bg="#000000", fg="white",
                            text='Save', command=choise_save)
    cancel_button = tk.Button(saver_window, text='Cancel', command=on_cancel)
    save_entry = tk.Entry(saver_window, textvariable=file_name)
    save_entry.focus()
    dot_wav_label = tk.Label(saver_window, text='.wav', bg='white', relief=tk.SUNKEN)

    instruct_label.grid(column=0, row=0, columnspan=2, padx=20, pady=10)
    save_entry.grid(column=0, row=1, sticky='e')
    dot_wav_label.grid(column=1, row=1, sticky='w', padx=2)
    save_button.grid(column=1, row=2, pady=20)
    cancel_button.grid(column=2, row=2, pady=20, padx=20)

    #saver_window.protocol("WM_DELETE_WINDOW", on_cancel)
    saver_window.lift()


def saver():
    if saver_window is None:   # don't forget to boolify it first!
        saver_window_func()
        return
    try:
        saver_window.lift()
    except tk.TclError:       # error on reopening closed window
        saver_window_func()


def pickler_window_func():
    """Dialog box for Save/Set Sliders"""
    def on_closing_pickler():
        pickle_namer_entry.delete(0, last='end')
        settings_apply_entry.delete(0, last='end')
        pickler_window.destroy()

    def look():
        pickler_window.withdraw()
        file_dialoge_item = filedialog.askopenfilename(
            initialdir="./", title="Select file", filetypes=(
                ("pickle files", "*.pickle"), ("all files", "*.*")))

        if len(file_dialoge_item) == 0:
            pickler_window.deiconify()
            print('if len(file_dialoge_item) == 0')
            return
        else:
            settings_apply_entry.delete(0, last='end')
            settings_apply_entry.insert(0, os.path.split(file_dialoge_item)[1])
            pickler_window.deiconify()

    def save_stuff():
        """Puts slider values in a python list then pickles"""
        s0 = scale_vol.get()
        s1 = scale_trem_speed.get()
        s2 = scale_trem_amount.get()
        s3 = scale_duration.get()
        s4 = scale_freq.get()
        s5 = scale_fm.get()
        s6 = scale_fm2.get()
        s7 = scale_speed.get()
        s8 = scale_lfo_amount.get()
        s9 = scale_ramp_amount.get()
        s10 = scale_ramp3_size.get()
        s11 = scale_noise_shape.get()
        s12 = scale_roll.get()
        s13 = scale_fade.get()

        settings_list = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]
        stamp = pickle_file_name.get()
        if len(stamp) == 0:
            stamp = "{}.pickle".format(str(time.time())[:10])
        else:
            stamp = "{}.pickle".format(stamp)
        with open(stamp, "wb+") as fp:
            pickle.dump(settings_list, fp)
        pickle_file_name.set("")
        pickler_window.destroy()
        if ms_win is not None:
            ms_win.destroy()
        message_win("Settings Saved", "File saved as {}".format(stamp))

    def set_stuff():
        """Unpickles list an reapplies to sliders"""
        try:
            with open(settings_apply_entry.get(), "rb") as fp:
                go = pickle.load(fp)

        except FileNotFoundError:
            # print('fuck')
            if len(settings_apply_entry.get()) == 0:
                if ms_win is not None:
                    ms_win.destroy()
                message_win("File Name Not Entered",
                            "Type [<file name>.pickle]       in the box.")
                settings_apply_entry.focus()
            else:
                if ms_win is not None:
                    ms_win.destroy()
                message_win(
                    "File Not Found", "{} not found or does not exist.".format(
                        settings_apply_entry.get()))
                settings_apply_entry.delete(0, last='end')
                settings_apply_entry.focus()
        else:
            scale_vol.set(go[0])
            scale_trem_speed.set(go[1])
            scale_trem_amount.set(go[2])
            scale_duration.set(go[3])
            scale_freq.set(go[4])
            scale_fm.set(go[5])
            scale_fm2.set(go[6])
            scale_speed.set(go[7])
            scale_lfo_amount.set(go[8])
            scale_ramp_amount.set(go[9])
            scale_ramp3_size.set(go[10])
            scale_noise_shape.set(go[11])
            scale_roll.set(go[12])
            scale_fade.set(go[13])

            pickler_window.destroy()

    global pickler_window
    pickler_window = tk.Toplevel(master)
    pickler_window.geometry('500x200')
    pickler_window.title('Save slider Settings')

    instruct_label = tk.Label(pickler_window, text='Enter a file name then click save')
    pickle_namer_entry = tk.Entry(pickler_window, textvariable=pickle_file_name)
    dot_pickle_label = tk.Label(pickler_window, text='.pickle', bg='white', relief=tk.SUNKEN)
    settings_apply_label = tk.Label(
        pickler_window, text='Enter Settings File.txt, then click Apply')
    settings_apply_entry = tk.Entry(pickler_window)
    pickle_save_button = tk.Button(pickler_window, text='Save', command=save_stuff)
    set_button = tk.Button(pickler_window, text='Apply', command=set_stuff)
    cancel_button = tk.Button(pickler_window, text='Cancel', command=on_closing_pickler)
    file_dialog_button = tk.Button(pickler_window, text='View Files', command=look)

    instruct_label.grid(column=0, row=0, columnspan=2)
    pickle_namer_entry.grid(column=0, row=1, sticky='e')
    dot_pickle_label.grid(column=1, row=1, sticky='w')
    pickle_save_button.grid(column=2, row=1)
    settings_apply_label.grid(column=0, row=2, columnspan=2)
    settings_apply_entry.grid(column=0, row=3, ipadx=26, columnspan=2)
    set_button.grid(column=2, row=3)
    cancel_button.grid(column=0, row=4, pady=10)
    file_dialog_button.grid(column=2, row=4, pady=10)

    pickler_window.protocol("WM_DELETE_WINDOW", on_closing_pickler)
    pickler_window.lift()


def pickler():
    if pickler_window is None:
        pickler_window_func()
        return
    try:
        pickler_window.lift()
    except tk.TclError:
        pickler_window_func()


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit? "):
        master.destroy()


sample_rate = 44100
attenuation = 0.2
device_window = None
saver_window = None
pickler_window = None
ms_win = None

g = gen_1()
g1 = gen_1()
g2 = gen_1()
g3 = gen_3()
g_wave = gen_1()

master = tk.Tk()
master.geometry("900x600")
master.title('Noise Making Thingy')

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

device_num = tk.IntVar()
device_num.set(-1)
file_name = tk.StringVar()
pickle_file_name = tk.StringVar()

menu_bar = tk.Menu(master)
menu_bar.add_command(label='Save As .wav', command=saver)
menu_bar.add_command(label='Save/Set Sliders', command=pickler)
menu_bar.add_command(label='Output Devices', command=device_l)
master.config(menu=menu_bar)

duration_labal = tk.Label(master, text='Duration')
freq_labal = tk.Label(master, text='Frequency Hz')
fm_labal = tk.Label(master, text='FM 1 Hz')
fm2_labal = tk.Label(master, text='FM 2 Hz')
speed_labal = tk.Label(master, text='Sin LFO Speed')
lfo_amount_label = tk.Label(master, text='Sin LFO Amount')
ramp_amount_label = tk.Label(master, text='FM 1 Ramp Amount')
ramp3_size_label = tk.Label(master, text='FM 2 Ramp Time Ratio')
wave_label = tk.Label(master, text='Wave Shape')
fade_out_label = tk.Label(master, text='Fade Out')

noise_shape_label = tk.Label(master, text='Noise Shape')
trem_speed_label = tk.Label(master, text='Trem Speed')
vol_label = tk.Label(master, text='Volume')
trem_amount_label = tk.Label(master, text='Amount Trem')
ring_label = tk.Label(master, text='Ring')
roll_label = tk.Label(master, text='Delay')

scale_freq = tk.Scale(master, from_=50, to=510, resolution=5, orient=tk.HORIZONTAL, length=250)
scale_fm = tk.Scale(master, from_=10, to=250, resolution=5, orient=tk.HORIZONTAL, length=250)
scale_fm2 = tk.Scale(master, from_=40, to=400, resolution=5, orient=tk.HORIZONTAL, length=250)
scale_speed = tk.Scale(master, from_=0.02, to=5, resolution=0.02,
                       orient=tk.HORIZONTAL, length=250)
scale_lfo_amount = tk.Scale(master, from_=1.0, to=5.0, resolution=0.1,
                            orient=tk.HORIZONTAL, length=250)
scale_ramp_amount = tk.Scale(master, from_=1.0, to=8, resolution=0.1,
                             orient=tk.HORIZONTAL, length=250)
scale_ramp3_size = tk.Scale(master, from_=1.3, to=10, resolution=0.1,
                            orient=tk.HORIZONTAL, length=250)
scale_duration = tk.Scale(master, from_=0.5, to=160, resolution=0.5,
                          orient=tk.HORIZONTAL, length=700, width=30, troughcolor='#848884')

scale_duration.set(4.0)
scale_freq.set(360)
scale_fm.set(60)
scale_fm2.set(300)
scale_speed.set(1.0)
scale_ramp3_size.set(2)

scale_vol = tk.Scale(master, from_=0.0, to=1.0, resolution=0.01,
                     orient=tk.HORIZONTAL, length=250, troughcolor='#848884')
scale_noise_shape = tk.Scale(master, from_=-10.0, to=0.0, resolution=0.1,
                             orient=tk.HORIZONTAL, length=200)
scale_trem_speed = tk.Scale(master, from_=0.5, to=15, resolution=0.2,
                            orient=tk.HORIZONTAL, length=200)
scale_trem_amount = tk.Scale(master, from_=0.0, to=1.0, resolution=0.01,
                             orient=tk.HORIZONTAL, length=200)
scale_roll = tk.Scale(master, from_=0, to=4410, resolution=50, orient=tk.HORIZONTAL, length=200)
scale_fade = tk.Scale(master, from_=0.0, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, length=200)
scale_vol.set(0.7)
scale_trem_speed.set(6.0)
scale_trem_amount.set(0.5)
scale_noise_shape.set(-2.0)
scale_roll.set(250)

play_button = tk.Button(master, text='Play', bg='#0ba4a4', height=3, width=7, command=play)
log_ramp_button = tk.Button(master, bg="#728C00", fg="white",
                            text="FM 1 Ramp", width=7, command=choise)
tremelo_button = tk.Button(master, bg="#000000", fg="white",
                           text='Trem Off', width=7, command=choise_1)
fm2_button = tk.Button(master, bg="#000000", fg="white", text='FM2 Off', width=7, command=choise_2)
noise_button = tk.Button(master, bg="#000000", fg="white", text='Noise', width=6, command=choise_3)
wave_button = tk.Button(master, bg="#000000", fg="white",
                        text='Sine', width=10, command=choise_wave)
stop_button = tk.Button(master, bg="#728C00", fg="white", text='Stop', width=7, command=stop_it)

freq_labal.grid(column=0, row=1)
fm_labal.grid(column=0, row=2)
fm2_labal.grid(column=0, row=3)
speed_labal.grid(column=0, row=4)
lfo_amount_label.grid(column=0, row=5)
ramp_amount_label.grid(column=0, row=6)
ramp3_size_label.grid(column=0, row=7)
wave_label.grid(column=3, row=0)

vol_label.grid(column=0, row=0)

scale_freq.grid(column=1, row=1)
scale_fm.grid(column=1, row=2)
scale_fm2.grid(column=1, row=3)
scale_speed.grid(column=1, row=4)
scale_lfo_amount.grid(column=1, row=5)
scale_ramp_amount.grid(column=1, row=6)
scale_ramp3_size.grid(column=1, row=7)
scale_duration.grid(column=1, row=11, columnspan=4)

scale_vol.grid(column=1, row=0)

play_button.grid(column=2, row=0, padx=20)
stop_button.grid(column=2, row=1)
log_ramp_button.grid(column=2, row=6)
tremelo_button.grid(column=2, row=2)
fm2_button.grid(column=2, row=3)
noise_button.grid(column=2, row=4)
wave_button.grid(column=4, row=0)

noise_shape_label.grid(column=3, row=4)
scale_noise_shape.grid(column=4, row=4)
trem_speed_label.grid(column=3, row=2)
scale_trem_speed.grid(column=4, row=2)
trem_amount_label.grid(column=3, row=3)
scale_trem_amount.grid(column=4, row=3)
ring_label.grid(column=5, row=3)
roll_label.grid(column=3, row=9)
scale_roll.grid(column=4, row=9)
fade_out_label.grid(column=3, row=10)
scale_fade.grid(column=4, row=10)

duration_labal.grid(column=0, row=11)

# Its like a face.

master.protocol("WM_DELETE_WINDOW", on_closing)
master.mainloop()
