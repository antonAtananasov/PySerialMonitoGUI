from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import serial
import serial.tools.list_ports
from time import sleep
from datetime import datetime
import os
from os.path import exists
from TkToolTip import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from random import randint
# Window setup ==============================================================================v
window = tk.Tk()
window.title("Tonziss Serial Monitor")
window.option_add( "*font", "Courier 10" )

style = ttk.Style(window)
style.theme_use('vista')


#widgets
panel = ttk.Frame(window)
topFrame1 = ttk.Frame(panel)
topFrame2 = ttk.Frame(panel)
middleFrame=ttk.Frame(panel)
bottomFrame=ttk.Frame(panel)
#layout
panel.pack(side='top',expand=True,padx=10,pady=10,anchor='n',fill='x')
topFrame1.pack(fill='x', expand=True, anchor = 'n', pady=2)
topFrame2.pack(fill='x', expand=True,anchor='n',side='top', pady=2)
middleFrame.pack(fill='both', expand = True, pady=2)
bottomFrame.pack(fill='both', expand = True, side='bottom', pady=2)

closeSer=False
ser = False
def on_closing():
    global closeSer
    closeSer = True
window.protocol("WM_DELETE_WINDOW", on_closing)

#plotter
mpl.use('TkAgg')
mpl.rcParams['toolbar'] = 'None'
figure = Figure(figsize=(6, 4), dpi=100)
figure_canvas = FigureCanvasTkAgg(figure, window)
# NavigationToolbar2Tk(figure_canvas, window)

# create axes
ax = figure.add_subplot()

# create the barchart
figure_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

x,y=[],[]
xrange=30
xrange=5
def animate(i):
    if len(x) < 1:
        return
    ax.clear()
    ax.plot(x, y)
    # ax.set_xlim([x[-1]-xrange,x[-1]])
    # ax.set_ylim([0,10])
    ax.relim()
# ani = FuncAnimation(figure, animate, interval=20)

#end of window setup =======================================================================^

#list ports ===================================v
ports, descs, hwids = [],[],[]
choices = ['']

portChoice = StringVar(topFrame1)
popupMenu=ttk.OptionMenu(topFrame1, portChoice, *choices)

def reloadComports():
    portObjs=sorted(serial.tools.list_ports.comports())
    
    choices.clear()
    ports.clear()
    descs.clear()
    hwids.clear()
    popupMenu['menu'].delete(0,'end')
    for port, desc, hwid in portObjs:
        choice = str(port)+' '+str(desc)
        choices.append(choice)
        ports.append(port)
        descs.append(desc)
        hwids.append(hwid)
        popupMenu['menu'].add_command(label=choice, command=tk._setit(portChoice, choice))
    portChoice.set(str(choices[0]) if len(choices) > 0 else 'No detected ports')
    popupMenu.update()
reloadComports()
    
refreshBtn=ttk.Button(topFrame1, text='???',command=reloadComports)

#layout
refreshBtn.pack(side='left')
popupMenu.pack(side='left',fill='x',expand=True)
#end of listing ports =========================^

#connecting to serial ========================================================v
def connect():
    if len(choices) < 1:
        return
    global ser
    i = choices.index(portChoice.get())
    ser=serial.Serial(str(ports[i]), int(baudrate.get()))
    window.title(window.title()+' '+choices[i]+' '+baudrate.get())
    topFrame1.destroy()    
    
#widget
connectbtn = ttk.Button(topFrame1, text='Begin', command=connect)
baudrate = Entry(topFrame1, width=9)
baudrate.insert(0,'9600')
#layout
connectbtn.pack(side='right')
baudrate.pack(side='right', fill='y')
#end of connecting to serial ==================================================^


#serial input ======================================v
#widgets
serialInput = Entry(topFrame2)

def serialSend(e=''):
    global ser
    if not ser:
        return
    ser.write(serialInput.get().encode())
    serialInput.delete(0, END)
#widgets
serialInput.bind('<Return>', serialSend)
sendBtn = ttk.Button(topFrame2, text="Send", command=serialSend)
autoscrollVal = IntVar(value=1)
autoscroll = ttk.Checkbutton(topFrame2, variable=autoscrollVal)
#layout
serialInput.pack(side='left', expand=True, fill='both')
autoscroll.pack(side='right')
sendBtn.pack(side='right')
#end of serial input ==============================^

#file controls ==========================v
fileDirectory=os.getcwd()
fileName = 'log.txt'
logName = ttk.Label(bottomFrame, text='log.txt')
filePathTooltip = CreateToolTip(logName, os.path.join(fileDirectory, fileName))
def getFilePath():
    global fileDirectory
    global fileName
    #request a file and get its full path
    logToFileValue.set(0)
    f = filedialog.asksaveasfile(initialdir = fileDirectory,title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")),defaultextension=".txt", initialfile='log.txt')
    if not f:
        return
    path = f.name
    fileName = os.path.basename(path)
    fileDirectory = os.path.dirname(path)
    logName.configure(text=fileName)
    filePathTooltip.text=os.path.join(fileDirectory, fileName)
    
directoryBtn = ttk.Button(bottomFrame, text='????', command = getFilePath)


logToFileValue = IntVar()
logToFile = ttk.Checkbutton(bottomFrame, variable = logToFileValue)

#layout
directoryBtn.pack(side='left')
logName.pack(side='left', padx=4)
logToFile.pack(side='left')
#end of file controls ===================^

#output control ===================================================v
serialOutput = ScrolledText(panel)
serialOutput.pack(fill='both',expand=True)

def clearMonitor():
    serialOutput.delete('1.0','end')
    
    
clearMonitor()
serialOutput.configure(state='disabled')

def zoom(amount):
    fontTuple = serialOutput.cget('font').split(' ')
    font = fontTuple[0]
    size = int(fontTuple[1])+amount
    serialOutput.configure(font = (font,size))



clearBtn = ttk.Button(bottomFrame, text='Clear', command = clearMonitor)
zoomInBtn = ttk.Button(bottomFrame, text='+', command = lambda:zoom(2))
zoomOutBtn = ttk.Button(bottomFrame, text='-', command = lambda:zoom(-2))
#layout
clearBtn.pack(side='right')
zoomInBtn.pack(side='right')
zoomOutBtn.pack(side='right')
#end of output control ============================================^


#serial loop ===================================================================================v
serialBuffer=''
while True:
    sleep(.001)
    if closeSer:
        if ser != False:
            ser.close()
        window.destroy()
        break
    while ser != False and ser.in_waiting:
        output=ser.read().decode()
        if logToFileValue.get():
            path=os.path.join(fileDirectory, fileName)
            f = open(path,'a+' if exists(path) else 'a')
            f.write(output)
            f.close()
        serialOutput.configure(state='normal')
        serialOutput.insert('end',output)

        serialOutput.configure(state='disabled')
        if output != '\n':
            serialBuffer += output
        else:
            serialBuffer = serialBuffer.strip().encode()
            if serialBuffer.isdigit():
                x.append(datetime.timestamp(datetime.now()))
                y.append(float(serialBuffer))
                print(serialBuffer)
            serialBuffer = ''
        if autoscrollVal.get():
            serialOutput.see('end')

    window.update()
#end of serial loop ===========================================================================^

window.mainloop()

