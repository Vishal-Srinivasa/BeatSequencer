from tkinter import *
from tkinter import messagebox
from pydub import AudioSegment
from pydub.playback import play
import time
import mysql.connector
import demjson
from threading import Thread


def tempo():
    global t_value
    t_value = int(tempo_value.get())


def mix(checklist):
    global drum_order
    flag = 0
    for i in range(10):
        if checklist[i].get() == 1:
            flag += 1
            if flag == 1:
                mixed = AudioSegment.from_wav('drums_audio_samples\\' + drum_order[i] + '.wav')
            else:
                mixed = mixed.overlay(AudioSegment.from_wav('drums_audio_samples\\' + drum_order[i] + '.wav'))
    if flag == 0:
        mixed = AudioSegment.silent(duration=125)
    return mixed


def export_mix(checklist):
    global drum_order
    flag = 0
    for i in range(10):
        if checklist[i] == 1:
            flag += 1
            if flag == 1:
                mixed = AudioSegment.from_wav('drums_audio_samples\\' + drum_order[i] + '.wav')
            else:
                mixed = mixed.overlay(AudioSegment.from_wav('drums_audio_samples\\' + drum_order[i] + '.wav'))
    if flag == 0:
        mixed = False
    return mixed


def playing():
    try:
        global t_value, checkcount, stop
        stop = False
        play_b.config(image = play_2)
        pause_b.config(image = pause_1)
        start_time = time.time()
        while True:
            delta_time = 60 / (t_value * 4)
            for i in range(16):
                mixed = mix(checkcount[i])
                start_time = time.time()
                play(mixed)
                try:
                    time.sleep(delta_time - (time.time() - start_time) - 0.125)
                except:
                    pass
            if stop:
                break

    except:
        messagebox.showerror('Invalid Tempo', 'Enter an integer value between 10 to 240')


stop = False


def pause():
    global stop
    stop = True
    play_b.config(image = play_1)
    pause_b.config(image = pause_2)


def save():
    try:
        global checkcount
        checkcount_value = {}
        for i in range(16):
            checkcount_value[i] = []
            for j in range(10):
                checkcount_value[i].append(checkcount[i][j].get())
        mycursor.execute(
            "insert into beat_sequencer values ( '{}' , '{}' )".format(s_name.get(), str(checkcount_value)))
        mydb.commit()
        messagebox.showinfo('Saved', 'Current pattern is saved')
        s_name.delete(0, len(s_name.get()))
    except:
        if s_name.get() == '':
            messagebox.showerror('No Name', 'Enter the name of the the pattern to be saved')
        else:
            messagebox.showerror('Name already exists', 'Enter another name')
    loadlist()


def load():
    try:
        global checkcount, strvar
        mycursor.execute("select checklist from beat_sequencer where name = '{}'  ".format(strvar.get()[2:-3]))
        for i in mycursor:
            checkcount_value = demjson.decode(i[0])
        for i in range(16):
            for j in range(10):
                checkcount[i][j].set(checkcount_value[i][j])
    except:
        messagebox.showerror('File name  not selected', 'Select the file name to be loaded')


def loadlist():
    loadlist = []
    mycursor.execute('select name from beat_sequencer')
    for i in mycursor:
        loadlist.append(i)
    global strvar
    strvar = StringVar()
    try:
        l_name = OptionMenu(root, strvar, *loadlist)
        l_name.place(x=120, y=600, width=100, height=35)
        l_name.config(bg = 'grey45')
    except:
        pass


def export():
    bar_list()
    response = messagebox.askyesno('Export', 'Do you want to Export')
    if response == 1:
        try:
            global t_value
            delta_time = 60000 / (t_value * 4)
            proceed = True
        except:
            messagebox.showerror('Invalid Tempo', 'Enter an integer value between 10 to 240')
            proceed = False
        if proceed:
            final_audio = AudioSegment.silent(duration=1)
            global checkcount_dict, dvar_dict
            for i in checkcount_dict:
                fin_audio = AudioSegment.silent(duration=1)
                count = checkcount_dict[i]
                for j in range(16):
                    mixed = export_mix(count[j])
                    if mixed:
                        fin_audio += mixed + AudioSegment.silent(duration=delta_time)
                    else:
                        fin_audio += AudioSegment.silent(duration=delta_time)
                fin_audio *= int(dvar_dict[i])
                final_audio += fin_audio
            final_audio.export('Exported\\' + e_name.get() + '.wav', format="wav")
            e_name.delete(0, len(e_name.get()))


def alive():
    global play_button
    if not play_button.is_alive():
        play_button = Thread(target=playing)
        play_button.start()


def clear():
    response = messagebox.askyesno('Clear', 'Do you want to Clear')
    if response == 1:
        global checkcount
        for i in range(16):
            for j in range(10):
                checkcount[i][j].set(0)


def delete():
    try:
        mycursor.execute("delete from beat_sequencer where name = '{}'  ".format(strvar.get()[2:-3]))
        loadlist()
    except:
        messagebox.showerror('File name  not selected', 'Select the file name to be loaded')


def add():
    global checkcount_dict, bar_number
    new_checkcount = {}
    for i in range(16):
        new_checkcount[i] = []
        for j in range(10):
            new_checkcount[i].append(0)
    checkcount_dict[bar_number + 1] = new_checkcount
    dvar_dict[bar_number + 1] = 1
    bar_number += 1
    Open()


def remove():
    global checkcount_dict, bar_number, dvar_dict
    if bar_number > 1:
        del checkcount_dict[bar_number]
        del dvar_dict[bar_number]
        bar_number -= 1
        Open()


def bar_list():
    global checkcount, checkcount_dict, dvar_dict, prev_bar, string_var, dvar
    try:
        try:
            for i in range(16):
                for j in range(10):
                    checkcount_dict[prev_bar][i][j] = checkcount[i][j].get()
            dvar_dict[prev_bar] = dvar.get()
        except:
            pass
        prev_bar = int(string_var.get())
        for i in range(16):
            for j in range(10):
                checkcount[i][j].set(checkcount_dict[prev_bar][i][j])
        dvar.set(dvar_dict[prev_bar])
    except:
        messagebox.showerror('Bar number not selected', 'Select the bar number to be loaded')


def Open():
    global string_var, checkcount_dict
    string_var = StringVar()
    bar = OptionMenu(root, string_var, *list(checkcount_dict.keys()))
    bar.place(x=370, y=600, width=100, height=35)
    bar.config(bg = 'grey45')


root = Tk()
root.title("Beat Sequencer")
root.geometry("750x655+0+0")
root.iconbitmap('icons\\drums.ico')
root.configure(background = 'grey21')
root.resizable(False, False)

tempo_value = Spinbox(root, font=10, from_=10, to=240, command=lambda: Thread(target=tempo).start(), bg = 'grey45', fg = 'cyan')
tempo_value.place(x=120, y=20, width=75, height=40)
tempo_image = PhotoImage(file = 'icons\\tempo.png')
Label(root, image = tempo_image, font=10).place(x=10, y=20, width=60, height=40)
equal_image = PhotoImage(file = 'icons\\equal.png')
Label(root, image = equal_image, font=10).place(x=70, y=20, width=32, height=40)

drum_order = {0: 'kick', 1: 'snare', 2: 'rim', 3: 'c_hihat', 4: 'o_hihat', 5: 'crash', 6: 'ride', 7: 'high_tom',
              8: 'mid_tom', 9: 'floor_tom'}
for i in range(10):
    icon = PhotoImage(file = "icons\\" + drum_order[i] + ".png")
    label = Label(image=icon)
    label.image = icon
    label.place(x=30, y=100 + (45 * i))

for i in range(16):
    value = ['1', 'e', '+', 'a', '2', 'e', '+', 'a', '3', 'e', '+', 'a', '4', 'e', '+', 'a']
    color = ['cyan', 'MediumPurple1']
    Label(root, font=10, text=value[i], bg = 'grey21', fg = color[i%2]).place(x=110 + (35 * i) + (25 * (i // 4)), y=70, width=30, height=30)

checkcount = {}
for i in range(16):
    checkcount[i] = []
    for j in range(10):
        checkcount[i].append(IntVar())

for i in range(16):
    for j in range(10):
        Checkbutton(root, variable=checkcount[i][j], bg = 'grey21', activebackground = 'pink', activeforeground = 'blue').place(x=115 + (35 * i) + (25 * (i // 4)), y=110 + (45 * j),
                                                           width=20, height=20)

checkcount_dict = {1: {}}
for i in range(16):
    checkcount_dict[1][i] = []
    for j in range(10):
        checkcount_dict[1][i].append(0)
bar_number = 1
prev_bar = 1
play_button = Thread(target=playing)
play_1 = PhotoImage(file = 'icons\\play.png')
play_2 = PhotoImage(file = 'icons\\play_click.png')
play_b = Button(root, image = play_1, font=10, command=lambda: alive(), bg = 'grey21', activebackground = 'grey21', bd = 0)
play_b.place(x=270, y=20, width=60, height=40)

stop = False
pause_1 = PhotoImage(file = 'icons\\pause.png')
pause_2 = PhotoImage(file = 'icons\\pause_click.png')
pause_b = Button(root, image = pause_2, font=10, command=lambda: Thread(target=pause).start(), bg = 'grey21', activebackground = 'grey21', bd = 0)
pause_b.place(x=340, y=20, width=60, height=40)

Button(root, text="Clear", font=10, command=lambda: Thread(target=clear).start(), bg = 'grey36', fg = 'aquamarine2', activebackground = 'grey36', activeforeground = 'MediumPurple1').place(x=640, y=20, width=100, height=40)

add_i = PhotoImage(file = 'icons\\add.png')
Button(root, image = add_i, font=10, command=lambda: Thread(target=add).start(), bg = 'grey45', bd = 0, activebackground = 'grey21').place(x=360, y=550, width=60, height=40)
sub_i = PhotoImage(file = 'icons\\sub.png')
Button(root, image = sub_i, font=10, command=lambda: Thread(target=remove).start(), bg = 'grey45', bd = 0, activebackground = 'grey21').place(x=420, y=550, width=60, height=40)
Button(root, text="Open", font=10, command=lambda: Thread(target=bar_list).start(), bg = 'grey36', fg = 'turquoise3', activebackground = 'grey36', activeforeground = 'MediumPurple1').place(x=470, y=600, width=100, height=35)
Open()

mydb = mysql.connector.connect(host='localhost', user='root', passwd='Vishal1116')
mycursor = mydb.cursor()

mycursor.execute('create database if not exists music_sequencer')
mycursor.execute('use music_sequencer')
mycursor.execute('create table if not exists beat_sequencer (name char(27) unique, checklist text)')

s_name = Entry(root, font=10, bg = 'grey81', fg = 'purple4')
s_name.place(x=100, y=551, width=120, height=32)
Button(root, text="Save", font=10, command=lambda: Thread(target=save).start(), bg = 'grey45', fg = 'turquoise1', activebackground = 'grey45', activeforeground = 'MediumPurple1').place(x=220, y=550, width=100, height=35)

Button(root, text="Load", font=10, command=lambda: Thread(target=load).start(), bg = 'grey45', fg = 'turquoise1', activebackground = 'grey45', activeforeground = 'MediumPurple1').place(x=220, y=600, width=100, height=35)
loadlist()
Button(root, text="Delete", font=10, command=lambda: Thread(target=delete).start(), bg = 'grey45', fg = 'turquoise1', activebackground = 'grey45', activeforeground = 'MediumPurple1').place(x=20, y=600, width=100, height=35)

Button(root, text="Export", font=10, command=lambda: Thread(target=export).start(), bg = 'grey72', fg = 'purple3', activebackground = 'grey72', activeforeground = 'cyan').place(x=640, y=550, width=100, height=70)
dvar = DoubleVar()
scale = Scale(root, variable=dvar, from_=1, to=256, orient=HORIZONTAL, bg = 'grey21', fg = 'cyan', bd = 0, troughcolor = 'MediumPurple3')
scale.place(x=455, y=22, width=150, height=35)
dvar_dict = {1: dvar.get()}
e_name = Entry(root, font=10, bg = 'grey81', fg = 'purple4')
e_name.place(x=530, y=553, width=110, height=30)

root.mainloop()
