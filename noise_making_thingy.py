#!/usr/bin/env python3

""" Python thingy, a bit like a synthesizer """

import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd
import time
import pickle
import os
import tkinter as tk
from tkinter import messagebox


def play(save=False):
    """Gets values and selections from gui then plays or saves"""
    play_button.config(text="Wait", state="disabled")    # disable play button
    play_button.update()

    def tremelo():                              # more of a tremelator!
        trem_adder = 1.0 - trem_amount_value
        return np.sin(x * trem_speed) * trem_amount_value + trem_adder

    def ramp_2_osc():
        return ramp_2 * np.sin(fm * x)

    def lfo_osc_wave(lfo_shape):
        return lfo_shape() * np.sin(fm * x)

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

    def lfo():
        return (np.sin(x * speed)) * lfo_amount

    def lfo_pluss():
        y = np.sin(x * speed) * 2 + 1
        yy = np.clip(y, 0.2, 1) * lfo_amount
        return yy

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

    total_samples = int(duration * sample_rate)
    x = np.linspace(0, duration * 2 * np.pi, total_samples)    # f(x)

    # get tk variables.
    choose = lfo_int.get()
    choose_trem = trem_bool.get()
    choose_fm2 = fm2_bool.get()
    choose_noise = noise_int.get()
    choose_wave = wave_bool.get()

    ramp_3 = np.ones(len(x))
    ramp_3_ramp = np.logspace(
        1, 0, int(duration * sample_rate // ramp3_divizor))

    ramp_0 = np.logspace(noise_shape, 1, total_samples, base=5)
    ramp_1 = np.logspace(1, noise_shape, total_samples, base=5)
    ramp_2 = np.logspace(0, 1, total_samples) * ramp_amount
    ramp_3[: len(ramp_3_ramp)] = ramp_3_ramp
    fade_ramp = np.linspace(1, 0, fade_size if fade_size < 120000 else 120000)

    # wave selector
    if choose_wave is True:
        if choose_fm2 is False:
            if choose is 0:
                waveform = triangle(ramp_2_osc())
            elif choose is 1:
                waveform = triangle(lfo_osc_wave(lfo))
            else:
                waveform = triangle(lfo_osc_wave(lfo_pluss))

        if choose_fm2 is True:
            if choose is 0:
                waveform = 2 / np.pi * np.arcsin(np.sin(x * freq + ramp_2 * 2 / np.pi * np.arcsin(
                    np.sin(x * fm + ramp_3_fm2()))))
            elif choose is 1:
                waveform = 2 / np.pi * np.arcsin(np.sin(x * freq + lfo() * 2 / np.pi * np.arcsin(
                    np.sin(x * fm + ramp_3_fm2()))))   # bollox
            else:
                waveform = 2 / np.pi * np.arcsin(np.sin(x * freq + lfo_pluss() * 2 / np.pi * np.arcsin(
                    np.sin(x * fm + ramp_3_fm2()))))   # bollox

    if choose_wave is False:
        if choose_fm2 is False:
            if choose is 0:
                waveform = sine_wave(ramp_2_osc())
            elif choose is 1:
                waveform = sine_wave(lfo_osc_wave(lfo))
            else:
                waveform = sine_wave(lfo_osc_wave(lfo_pluss))

        if choose_fm2 is True:
            if choose is 0:
                waveform = np.sin(x * freq + ramp_2 * np.sin(
                    fm * x + ramp_3_fm2()))
            elif choose is 1:
                waveform = np.sin(x * freq + lfo() * np.sin(
                    fm * x + ramp_3_fm2()))
            else:
                waveform = np.sin(x * freq + lfo_pluss() * np.sin(
                    fm * x + ramp_3_fm2()))

    if choose_noise is 1:
        waveform = waveform + noise(ramp_1)

    if choose_noise is 2:
        waveform = waveform + noise(ramp_0)

    if choose_trem is True:
        waveform = waveform * tremelo()

    waveform = waveform * attenuation * vol
    # Split into stereo by delaying right speaker by roller variable amount.
    waveform1 = np.roll(waveform, roller)
    waveform1[:roller] = 0
    waveform[- len(fade_ramp):] *= fade_ramp
    waveform1[- len(fade_ramp):] *= fade_ramp
    waveform_stereo = np.vstack((waveform, waveform1)).T

    if save is True:            # Flag from set_save_flag_func.
        stamp = file_name.get()
        if len(stamp) == 0:     # Then time stamp it!
            stamp = "NMT-{}.wav".format(str(time.ctime()
                                            [-16:].replace(" ", "-").replace(":", "-")))
        else:
            stamp = "{}.wav".format(stamp)

        write_waveform = np.int16(waveform_stereo * 32767)
        write(stamp, sample_rate, write_waveform)
        # print('writing {}'.format(stamp))

        file_name.set("")
        play_button.update()
        play_button.config(text="Play", state="normal")

        saver_window.destroy()
        if ms_win is not None:
            ms_win.destroy()
        message_win("File Saved", "File saved as {}".format(stamp))
    else:
        try:
            if device_arg < 0:
                sd.play(waveform_stereo, sample_rate)
            else:
                sd.play(waveform_stereo, sample_rate, device=device_arg)
        except sd.PortAudioError:
            if ms_win is not None:
                ms_win.destroy()
            device_l()
            message_win(
                "PortAudioError", """Driver not valid! Click on or select
                 device from the list. Or Click Reset to Default Driver""")

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

# Toggling wave selector boolian values and setting button colors


def toggle_wave():
    wave_bool.set(next(g_wave))
    if wave_bool.get() is True:
        wave_button.config(bg="#728C00", fg="white", text="Triangle")
    if wave_bool.get() is False:
        wave_button.config(bg="#000000", fg="white", text="Sine")


def toggle_lfo():
    lfo_int.set(next(g))
    if lfo_int.get() is 0:
        log_ramp_button.config(bg="#728C00", fg="white", text="FM1 Ramp")
    if lfo_int.get() is 1:
        log_ramp_button.config(bg="#000000", fg="white", text="Sin LFO")
    if lfo_int.get() is 2:
        log_ramp_button.config(bg="#000000", fg="white", text="LFO Clip")


def toggle_trem():
    trem_bool.set(next(g1))
    if trem_bool.get() is True:
        tremelo_button.config(bg="#728C00", fg="white", text="Trem On")
    if trem_bool.get() is False:
        tremelo_button.config(bg="#000000", fg="white", text="Trem Off")


def toggle_fm2():
    fm2_bool.set(next(g2))
    if fm2_bool.get() is True:
        fm2_button.config(bg="#728C00", fg="white", text="FM2 On")
    if fm2_bool.get() is False:
        fm2_button.config(bg="#000000", fg="white", text="FM2 Off")


def select_noise():             # Three way push button.
    noise_int.set(next(g3))
    if noise_int.get() is 1:
        noise_button.config(bg="#728C00", fg="white", text="Noise >")
    if noise_int.get() is 0:
        noise_button.config(bg="#000000", fg="white", text="Noise Off")
    if noise_int.get() is 2:
        noise_button.config(bg="#728C00", fg="white", text="Noise <")


def stop_it():    # stop button function.
    sd.stop()


def message_win_func(mtitle, blah):

    def closer():
        ms_win.destroy()

    global ms_win
    ms_win = tk.Toplevel(master)
    ms_win.title(mtitle)
    label = tk.Label(ms_win, text=blah, font='Times 20')
    button = tk.Button(ms_win, text='OK', width=6,
                       bg="#728C00", fg="white", command=closer)
    ms_win.bind('<Return>', lambda event=None: button.invoke())

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

    def close_devices():
        device_window.destroy()

    def reset_d():
        device_num.set(-1)
        if ms_win is not None:
            ms_win.destroy()
        message_win("Default Device", "Device set to default")

    def driver_setter():
        """ Sets output device arg for play func to get """
        if ms_win is not None:
            ms_win.destroy()
        num = list_bx.curselection()[0]
        num_name = sd.query_devices()[num].get('name')
        device_num.set(num)
        message_win(
            'Driver Set', 'Device number {} ({}) \n set as output device'.format(num, num_name))

    query = repr(sd.query_devices())    # list ov i/o devices
    query = query.split("\n")

    dframe = tk.Frame(device_window, relief=tk.RAISED, bd=2, bg='#afb4b5')
    label_0 = tk.Label(device_window, text='List of availible devices',
                       bg='#afb4b5', font='Times 20')
    scrollbar = tk.Scrollbar(device_window)
    label_2 = tk.Label(
        dframe, text='Select output device then set', bg='#afb4b5', font='Times 15')
    set_device_button = tk.Button(dframe, text='Set', height=3, width=6, activebackground='#99c728',
                                  bg="#728C00", fg="white", command=driver_setter)
    reset_button = tk.Button(
        device_window, text='Reset to Default Device', command=reset_d)

    close_devices_button = tk.Button(
        device_window, text='Close', command=close_devices)
    list_bx = tk.Listbox(
        device_window, yscrollcommand=scrollbar.set, width=60, height=25)
    for i in range(len(query)):
        list_bx.insert(tk.END, query[i])
    device_window.bind('<Return>', lambda event=None: driver_setter())

    label_0.grid(row=0, column=0, columnspan=2)
    list_bx.grid(row=1, column=0, columnspan=3)
    scrollbar.grid(row=1, column=3, sticky=tk.N + tk.S)
    label_2.grid(row=2, column=0, sticky='ne', pady=8, padx=5)
    dframe.grid(row=2, column=0, rowspan=2, columnspan=2,
                sticky='w', pady=5, padx=20)
    set_device_button.grid(row=3, column=1, pady=5, padx=5)

    reset_button.grid(row=4, column=1, sticky='w', pady=8)
    close_devices_button.grid(row=3, column=2, sticky='w')
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

    def set_save_flag_func():
        play(save=True)  # flagged to write wav file

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
    save_button = tk.Button(saver_window, bg="#728C00", fg="white",
                            text='Save', command=set_save_flag_func)
    cancel_button = tk.Button(saver_window, text='Cancel', command=on_cancel)
    save_entry = tk.Entry(saver_window, textvariable=file_name)
    save_entry.focus()
    dot_wav_label = tk.Label(saver_window, text='.wav',
                             bg='white', relief=tk.SUNKEN)
    saver_window.bind('<Return>', lambda event=None: save_button.invoke())

    instruct_label.grid(column=0, row=0, columnspan=2, padx=20, pady=10)
    save_entry.grid(column=0, row=1, sticky='e')
    dot_wav_label.grid(column=1, row=1, sticky='w', padx=2)
    save_button.grid(column=1, row=2, pady=20)
    cancel_button.grid(column=2, row=2, pady=20, padx=20)

    # saver_window.protocol("WM_DELETE_WINDOW", on_cancel)
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
        pickler_window.destroy()

    def save_stuff():
        """Puts settings values in a python list then pickles"""
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
        s14 = lfo_int.get()    # log ramp/lfo/lfo clip
        s15 = trem_bool.get()    # tremelo
        s16 = fm2_bool.get()    # fm2
        s17 = noise_int.get()  # noise
        s18 = wave_bool.get()    # wave shape

        settings_list = [s0, s1, s2, s3, s4, s5, s6, s7, s8,
                         s9, s10, s11, s12, s13, s14, s15, s16, s17, s18]
        stamp = pickle_file_name.get()
        if len(stamp) == 0:
            stamp = "NMT-{}.pickle".format(str(time.ctime()
                                               [-16:].replace(" ", "-").replace(":", "-")))
        else:
            stamp = "{}.pickle".format(stamp)
        with open(stamp, "wb+") as fp:
            pickle.dump(settings_list, fp)
        pickle_file_name.set("")
        pickler_window.destroy()
        if ms_win is not None:
            ms_win.destroy()
        message_win("Settings Saved", "File saved as {}".format(stamp))

    global pickler_window
    pickler_window = tk.Toplevel(master)
    pickler_window.geometry('500x200')
    pickler_window.title('Save Settings')

    instruct_label = tk.Label(
        pickler_window, text='Enter a file name then click save', font='Times 20')
    pickle_namer_entry = tk.Entry(
        pickler_window, textvariable=pickle_file_name)
    pickle_namer_entry.focus_set()
    dot_pickle_label = tk.Label(
        pickler_window, text='.pickle', bg='white', relief=tk.SUNKEN)
    pickle_save_button = tk.Button(pickler_window, text='Save',
                                   bg="#728C00", fg="white", command=save_stuff)
    cancel_button = tk.Button(
        pickler_window, text='Cancel', command=on_closing_pickler)
    pickler_window.bind(
        '<Return>', lambda event=None: pickle_save_button.invoke())

    instruct_label.grid(column=0, row=0, columnspan=3, padx=30, pady=10)
    pickle_namer_entry.grid(column=0, row=1, sticky='e', ipadx=20)
    dot_pickle_label.grid(column=1, row=1, sticky='w')
    pickle_save_button.grid(column=2, row=1, padx=10)
    cancel_button.grid(column=0, row=4, pady=10)

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


def set_stuff_func():

    def cancel_set_window():
        set_window.destroy()

    def apply_settings():
        """Get selected settings file, open and set variables from list"""
        if list_bx.curselection() is ():
            message_win("No File Selected",
                        "Click on a file to select then Apply")
        else:
            item = list_bx.get(list_bx.curselection())

            try:
                with open(item, "rb") as fp:
                    go = pickle.load(fp)
            except FileNotFoundError:
                message_win("FileNotFoundError", "{} not found or does not exist".format(
                            list_bx.curselection()))
            except pickle.UnpicklingError:
                message_win("UnpicklingError", "File corrupted or wrong")
            else:
                try:
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
                    while lfo_int.get() != go[14]:
                        toggle_lfo()                # Button clicking func.
                    if go[15] != trem_bool.get():
                        toggle_trem()
                    if go[16] != fm2_bool.get():
                        toggle_fm2()
                    while noise_int.get() != go[17]:
                        select_noise()
                    if go[18] != wave_bool.get():
                        toggle_wave()
                except IndexError:
                    message_win("IndexError", "File corrupted or wrong")
                except tk.TclError:
                    message_win("IndexError", "File corrupted or wrong")

    global set_window
    set_window = tk.Toplevel(master)
    set_window.title('Recall settings')
    scrollbar = tk.Scrollbar(set_window)
    list_bx = tk.Listbox(
        set_window, yscrollcommand=scrollbar.set, width=60, height=20)
    button_close = tk.Button(set_window, text='Close',
                             command=cancel_set_window)
    button_apply = tk.Button(set_window, text='Apply', bg="#728C00",
                             fg="white", command=apply_settings)

    list_bx.grid(column=0, row=0, columnspan=2)
    button_apply.grid(column=0, row=1, pady=10)
    button_close.grid(column=1, row=1, pady=10)
    scrollbar.grid(column=2, row=0, sticky=tk.N + tk.S)
    scrollbar.config(command=list_bx.yview)
    d = os.getcwd()
    for entry in os.scandir(d):
        if not entry.name.startswith('.') and entry.name.endswith('.pickle') and entry.is_file():
            list_bx.insert(tk.END, entry.name)
    set_window.bind('<Return>', lambda event=None: apply_settings())

    set_window.lift()


def set_stuff():
    if set_window is None:
        set_stuff_func()
        return
    try:
        set_window.lift()
    except tk.TclError:
        set_stuff_func()


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit? "):
        quit()


def quit():
    sd.stop()
    master.destroy()


try:
    sample_rate = 44100
    attenuation = 0.2
    device_window = None
    saver_window = None
    pickler_window = None
    set_window = None
    ms_win = None

    # assign generators.
    g = gen_3()     # lfo
    g1 = gen_1()    # trem
    g2 = gen_1()
    g3 = gen_3()
    g_wave = gen_1()

    master = tk.Tk()
    master.geometry("930x640")
    master.title('Noise Making Thingy')

    lfo_int = tk.IntVar()         # log/lfo
    lfo_int.set(0)
    trem_bool = tk.BooleanVar()   # trem
    trem_bool.set(False)
    fm2_bool = tk.BooleanVar()    # fm2
    fm2_bool.set(False)
    noise_int = tk.IntVar()       # noise
    noise_int.set(0)
    wave_bool = tk.BooleanVar()   # wave shape
    wave_bool.set(False)

    device_num = tk.IntVar()
    device_num.set(-1)
    file_name = tk.StringVar()
    pickle_file_name = tk.StringVar()

    menu_bar = tk.Menu(master)
    menu_bar.add_command(label='Save As .wav', command=saver)
    menu_bar.add_command(label='Save Settings', command=pickler)
    menu_bar.add_command(label='Recall Settings', command=set_stuff)
    menu_bar.add_command(label='Output Devices', command=device_l)
    master.config(menu=menu_bar)

    duration_labal = tk.Label(master, text='Duration')
    freq_labal = tk.Label(master, text='Frequency Hz')
    fm_labal = tk.Label(master, text='FM 1 Hz')
    fm2_labal = tk.Label(master, text='FM 2 Hz')
    speed_labal = tk.Label(master, text='Sin LFO Speed')
    lfo_amount_label = tk.Label(master, text='Sin LFO Amount')
    ramp_amount_label = tk.Label(master, text='FM1 Ramp Amount')
    ramp3_size_label = tk.Label(master, text='FM2 Ramp Time Ratio')
    wave_label = tk.Label(master, text='Wave Shape')
    fade_out_label = tk.Label(master, text='Fade Out')

    noise_shape_label = tk.Label(master, text='Noise Shape')
    trem_speed_label = tk.Label(master, text='Trem Speed')
    vol_label = tk.Label(master, text='Volume')
    trem_amount_label = tk.Label(master, text='Trem Amount')
    ring_label = tk.Label(master, text='Ring')
    roll_label = tk.Label(master, text='Delay')
    roll_units_label = tk.Label(master, text='1/44100')

    scale_freq = tk.Scale(master, from_=50, to=510,
                          resolution=5, orient=tk.HORIZONTAL, length=250)
    scale_fm = tk.Scale(master, from_=10, to=250,
                        resolution=5, orient=tk.HORIZONTAL, length=250)
    scale_fm2 = tk.Scale(master, from_=40, to=400,
                         resolution=5, orient=tk.HORIZONTAL, length=250)
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
                         orient=tk.HORIZONTAL, length=250, troughcolor='#575857')
    scale_noise_shape = tk.Scale(master, from_=-10.0, to=0.0, resolution=0.1,
                                 orient=tk.HORIZONTAL, length=200)
    scale_trem_speed = tk.Scale(master, from_=0.5, to=15, resolution=0.2,
                                orient=tk.HORIZONTAL, length=200)
    scale_trem_amount = tk.Scale(master, from_=0.0, to=1.0, resolution=0.01,
                                 orient=tk.HORIZONTAL, length=200)
    scale_roll = tk.Scale(master, from_=0, to=4410,
                          resolution=50, orient=tk.HORIZONTAL, length=200)
    scale_fade = tk.Scale(master, from_=0.0, to=0.5, resolution=0.01,
                          orient=tk.HORIZONTAL, length=200)
    scale_vol.set(0.7)
    scale_trem_speed.set(6.0)
    scale_trem_amount.set(0.5)
    scale_noise_shape.set(-2.0)
    scale_roll.set(250)

    play_button = tk.Button(master, text='Play', bg='#0ba4a4',
                            activebackground='#21e4e4', height=3, width=7, command=play)
    log_ramp_button = tk.Button(master, bg="#728C00", fg="white",
                                text="FM1 Ramp", width=7, command=toggle_lfo)
    tremelo_button = tk.Button(master, bg="#000000", fg="white",
                               text='Trem Off', width=7, command=toggle_trem)
    fm2_button = tk.Button(master, bg="#000000", fg="white",
                           text='FM2 Off', width=7, command=toggle_fm2)
    noise_button = tk.Button(master, bg="#000000", fg="white",
                             text='Noise', width=6, command=select_noise)
    wave_button = tk.Button(master, bg="#000000", fg="white",
                            text='Sine', width=10, command=toggle_wave)
    stop_button = tk.Button(master, bg="#728C00",
                            fg="white", text='Stop', width=7, command=stop_it)
    quit_button = tk.Button(master, text='Quit', width=7, command=quit)

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
    quit_button.grid(column=2, row=7)
    wave_button.grid(column=4, row=0)

    noise_shape_label.grid(column=3, row=4)
    scale_noise_shape.grid(column=4, row=4)
    trem_speed_label.grid(column=3, row=2)
    scale_trem_speed.grid(column=4, row=2)
    trem_amount_label.grid(column=3, row=3)
    scale_trem_amount.grid(column=4, row=3)
    ring_label.grid(column=5, row=3)
    roll_label.grid(column=3, row=9, pady=20, sticky='s')
    scale_roll.grid(column=4, row=9)
    roll_units_label.grid(column=5, row=9)
    fade_out_label.grid(column=3, row=10)
    scale_fade.grid(column=4, row=10)

    duration_labal.grid(column=0, row=11)

    # Its like a face.

    master.protocol("WM_DELETE_WINDOW", on_closing)
    master.mainloop()

except KeyboardInterrupt:
    print(' Come back soon')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
