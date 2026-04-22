import tkinter as tk
from aircraft import *
from tkinter import messagebox
from tkinter import *
from airport import *


def AddClick ():
   a1 = airport
   frase = fraseEntry.get()
   elementos = frase.split(" ")
   a1.code = elementos[0]
   AddAirport(airports, a1.code)


def DeleteClick ():
   a1 = fraseEntry.get()
   elementos = a1.split(" ")
   code = elementos[0]
   RemoveAirport(airports, code)


def LoadClick ():
   LoadAirports(airports)
   print(airports)


def SetSchengenClick ():
   a1 = fraseEntry.get()
   elementos = a1.split(" ")
   code = elementos[0]
   SetSchengen(code)
   print("done")


def ShowClick ():
   messagebox.showinfo("Airport List: ", airports)


def SaveSchengenClick ():
   SaveSchengenAirports(airports)


def PlotSchengenClick ():
   PlotAirports(airports)


def GoogleEarthClick ():
   MapAirports(airports)


def ArrivalsClick ():
   LoadArrivals(aircrafts)
   print(aircrafts)


def SaveAircraftClick ():
   SaveFlights(aircrafts)


def PlotArrivalsTimeClick ():
   PlotArrivals(aircrafts)


def PlotArrivalsCompanyClick ():
   PlotAirlines(aircrafts)


def PlotSchengenClick ():
   PlotFlightsType(aircrafts)


def ShowTrajectoriesClick ():
   MapFlights(aircrafts)


def LongTrajectoriesClick ():
   LongDistanceArrivals(aircrafts)


window = tk.Tk()
window.geometry("800x600")
window.title("Airport project")
window.rowconfigure(0, weight=0)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=1)


tituloLabel = Label(window, text = "Versión 1", font=("Courier", 20, "italic"))
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)


fraseEntry = Entry(window)
fraseEntry.grid(row=1, column=0, columnspan = 3, padx=5, pady=5, sticky=N + S + E + W)


button_version1_frame = tk.LabelFrame(window, text ="Versión 1")
button_version1_frame.grid(row=2,column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
button_version1_frame.rowconfigure(0, weight=0)
button_version1_frame.columnconfigure(0, weight=0)
button_version1_frame.columnconfigure(1, weight=0)
button_version1_frame.columnconfigure(2, weight=0)
button_version1_frame.columnconfigure(3, weight=0)
button_version1_frame.columnconfigure(4, weight=0)
button_version1_frame.columnconfigure(5, weight=0)
button_version1_frame.columnconfigure(6, weight=0)
button_version1_frame.columnconfigure(7, weight=0)


AddButton = tk.Button(button_version1_frame, text="Add Airport", command=AddClick)
AddButton.grid(row=0,column=0,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


DeleteButton = tk.Button(button_version1_frame, text="Delete Airport", command=DeleteClick)
DeleteButton.grid(row=0,column=1,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


LoadButton = tk.Button(button_version1_frame, text="Load Airports", command=LoadClick)
LoadButton.grid(row=0,column=2,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


SetSchengenButton = tk.Button(button_version1_frame, text="Set Schengen", command=SetSchengenClick)
SetSchengenButton.grid(row=0,column=3,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


ShowButton = tk.Button(button_version1_frame, text="Airport List", command=ShowClick)
ShowButton.grid(row=0,column=4,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


SaveSchengenButton = tk.Button(button_version1_frame, text="Save Schengen", command=SaveSchengenClick)
SaveSchengenButton.grid(row=0,column=5,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


PlotSchengenButton = tk.Button(button_version1_frame, text="Plot Schengen", command=PlotSchengenClick)
PlotSchengenButton.grid(row=0,column=6,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


GoogleEarthButton = tk.Button(button_version1_frame, text="Google Earth", command=GoogleEarthClick)
GoogleEarthButton.grid(row=0,column=7,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


button_version2_frame = tk.LabelFrame(window, text ="Versión 2")
button_version2_frame.grid(row=3,column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
button_version2_frame.rowconfigure(0, weight=0)
button_version2_frame.columnconfigure(0, weight=0)
button_version2_frame.columnconfigure(1, weight=0)
button_version2_frame.columnconfigure(2, weight=0)
button_version2_frame.columnconfigure(3, weight=0)
button_version2_frame.columnconfigure(4, weight=0)
button_version2_frame.columnconfigure(5, weight=0)
button_version2_frame.columnconfigure(6, weight=0)
button_version2_frame.columnconfigure(7, weight=0)


ArrivalsButton = tk.Button(button_version2_frame, text="Load Arrivals", command=ArrivalsClick)
ArrivalsButton.grid(row=0,column=0,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


SaveAircraftButton = tk.Button(button_version2_frame, text="Save Aircraft", command=SaveAircraftClick)
SaveAircraftButton.grid(row=0,column=1,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


PlotArrivalsTimeButton = tk.Button(button_version2_frame, text="Plot Arrivals/Time", command=PlotArrivalsTimeClick)
PlotArrivalsTimeButton.grid(row=0,column=2,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


PlotArrivalsCompanyButton = tk.Button(button_version2_frame, text="Plot Arrivals/Company", command=PlotArrivalsCompanyClick)
PlotArrivalsCompanyButton.grid(row=0,column=3,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


PlotSchengenArrivalsButton = tk.Button(button_version2_frame, text="Plot Schengen Arrivals", command=PlotSchengenClick)
PlotSchengenArrivalsButton.grid(row=0,column=4,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


ShowTrajectoriesButton = tk.Button(button_version2_frame, text="Show Trajectories", command=ShowTrajectoriesClick)
ShowTrajectoriesButton.grid(row=0,column=5,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


ShowLongTrajectoriesButton = tk.Button(button_version2_frame, text="Show Long Trajectories", command=LongTrajectoriesClick)
ShowLongTrajectoriesButton.grid(row=0,column=6,padx=5,pady=5,sticky=tk.N + tk.S + tk.E + tk.W)


window.mainloop()