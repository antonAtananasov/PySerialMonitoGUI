from tkinter import *
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import serial
import serial.tools.list_ports
from time import sleep

# Window setup ==============================================================================v
window = Tk()
window.title("Tonziss Serial Monitor")
# window.geometry('700x500')
#widgets
panel = Frame(window)
topFrame1 = Frame(panel)
topFrame2 = Frame(panel)
middleFrame=Frame(panel)
bottomFrame=Frame(panel)
#layout
panel.pack(side='top',expand=True,padx=10,pady=10,anchor='n',fill='x')
topFrame1.pack(fill='x', expand=True, anchor = 'n')
topFrame2.pack(fill='x', expand=True,anchor='n',side='top')
middleFrame.pack(fill='both', expand = True)
bottomFrame.pack(fill='both', expand = True, side='bottom')

closeSer=False
ser = False
def on_closing():
    global closeSer
    closeSer = True
window.protocol("WM_DELETE_WINDOW", on_closing)
#end of window setup =======================================================================^

#list ports ===================================v
ports, descs, hwids = [],[],[]
choices = ['']

portChoice = StringVar(topFrame1)
popupMenu=OptionMenu(topFrame1, portChoice, *choices)

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
    
refreshBtn=Button(topFrame1, text='↻',command=reloadComports)

#layout
refreshBtn.pack(side='left')
popupMenu.pack(side='left',fill='x',expand=True)
#end of listing ports =========================^

#connecting to serial ========================================================v
def connect():
    global ser
    i = choices.index(portChoice.get())
    ser=serial.Serial(str(ports[i]), int(baudrate.get()))
    window.title(window.title()+' '+choices[i]+' '+baudrate.get())
    topFrame1.destroy()    
    
#widget
connectbtn = Button(topFrame1, text='Begin', command=connect)
baudrate = Entry(topFrame1,width=10)
baudrate.insert(0,'9600')
#layout
connectbtn.pack(side='right')
baudrate.pack(side='right')
#end of connecting to serial ==================================================^


#serial input ======================================v
#widgets
serialInput = Entry(topFrame2)

def serialSend(e=''):
    ser.write(serialInput.get().encode())
    serialInput.delete(0, END)
#widgets
serialInput.bind('<Return>', serialSend)
sendBtn = Button(topFrame2, text="Send", command=serialSend)
autoscrollVal = IntVar(value=1)
autoscroll = Checkbutton(topFrame2, variable=autoscrollVal)
#layout
serialInput.pack(side='left', expand=True, fill='x')
autoscroll.pack(side='right')
sendBtn.pack(side='right')
#end of serial input ==============================^

#serial monitor ========================================================v
serialOutput = ScrolledText(panel)
serialOutput.pack(fill='both',expand=True)
# end of serial monitor ================================================^

#file controls ==========================v
def clearMonitor():
    serialOutput.delete('1.0','end')
clearBtn = Button(bottomFrame, text='Clear',command=clearMonitor)
clearBtn.pack(side='right')
#end of file controls ===================^

#serial loop ===================================================================================v
while True:
    sleep(.001)
    if closeSer:
        if ser != False:
            ser.close()
        window.destroy()
        break
    while ser != False and ser.in_waiting:
        output=ser.read()
        serialOutput.insert('end',output)
        if autoscrollVal.get():
            serialOutput.see('end')

    window.update()
#end of serial loop ===========================================================================^

window.mainloop()

