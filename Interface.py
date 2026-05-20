import tkinter as tk
from aircraft import *
from tkinter import messagebox
from tkinter import *
from airport import *
from tkinter import filedialog
from LEBL import *

bcn = None


def RefreshAirportList():
    airport_listbox.delete(0, tk.END)
    for a in airports:
        schengen_str = "S" if a.schengen else "NS"
        airport_listbox.insert(tk.END, f"{a.code}   {a.lat:.6f}   {a.lon:.6f}   [{schengen_str}]")


def GetSelectedAirportCode():
    sel = airport_listbox.curselection()
    if not sel:
        return None
    line = airport_listbox.get(sel[0])
    return line.split()[0]


# Versión 1

def AddClick():
    def ask_code():
        dialog = tk.Toplevel(window)
        dialog.title("A")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Código ICAO (4 letras):").pack(padx=20, pady=(15, 5))
        code_entry = tk.Entry(dialog, width=20)
        code_entry.pack(padx=20)
        code_entry.focus()

        def on_ok():
            code = code_entry.get().strip().upper()
            if len(code) != 4:
                messagebox.showerror("Error", "El código debe tener 4 letras.", parent=dialog)
                return
            dialog.destroy()
            ask_lat(code)

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="OK", width=8, command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", width=8, command=on_cancel).pack(side=tk.LEFT, padx=5)
        code_entry.bind("<Return>", lambda e: on_ok())

    def ask_lat(code):
        dialog = tk.Toplevel(window)
        dialog.title("L...")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Latitud decimal (ej. 41.297445):").pack(padx=20, pady=(15, 5))
        lat_entry = tk.Entry(dialog, width=20)
        lat_entry.pack(padx=20)
        lat_entry.focus()

        def on_ok():
            try:
                lat = float(lat_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Introduce un número decimal válido.", parent=dialog)
                return
            dialog.destroy()
            ask_lon(code, lat)

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="OK", width=8, command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", width=8, command=on_cancel).pack(side=tk.LEFT, padx=5)
        lat_entry.bind("<Return>", lambda e: on_ok())

    def ask_lon(code, lat):
        dialog = tk.Toplevel(window)
        dialog.title("Lo...")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Longitud decimal (ej. 2.083294):").pack(padx=20, pady=(15, 5))
        lon_entry = tk.Entry(dialog, width=20)
        lon_entry.pack(padx=20)
        lon_entry.focus()

        def on_ok():
            try:
                lon = float(lon_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Introduce un número decimal válido.", parent=dialog)
                return
            dialog.destroy()
            a1 = airport(code, lat, lon)
            AddAirport(airports, a1)
            RefreshAirportList()
            messagebox.showinfo("Add Airport", f"Aeropuerto {code} añadido.")

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="OK", width=8, command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", width=8, command=on_cancel).pack(side=tk.LEFT, padx=5)
        lon_entry.bind("<Return>", lambda e: on_ok())

    ask_code()


def DeleteClick():
    dialog = tk.Toplevel(window)
    dialog.title("Delete Airport")
    dialog.resizable(False, False)
    dialog.grab_set()

    tk.Label(dialog, text="Airport ICAO code to delete:").pack(padx=20, pady=(15, 5))
    entry = tk.Entry(dialog, width=20)

    selected = GetSelectedAirportCode()
    if selected:
        entry.insert(0, selected)

    entry.pack(padx=20)
    entry.focus()
    entry.select_range(0, tk.END)

    def on_ok():
        code = entry.get().strip().upper()
        if len(code) == 0:
            messagebox.showerror("Error", "Please enter an airport code.", parent=dialog)
            return
        result = RemoveAirport(airports, code)
        if result == -1:
            messagebox.showerror("Error", f"Airport '{code}' not found in the list.", parent=dialog)
        else:
            dialog.destroy()
            RefreshAirportList()
            messagebox.showinfo("Delete Airport", f"Airport '{code}' removed.")

    entry.bind("<Return>", lambda e: on_ok())

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="Delete", width=8, command=on_ok).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancel", width=8, command=dialog.destroy).pack(side=tk.LEFT, padx=5)


def LoadClick():
    filename = filedialog.askopenfilename()
    if filename:
        LoadAirports(filename)
        RefreshAirportList()


def SetSchengenClick():
    code = GetSelectedAirportCode()
    if code is None:
        messagebox.showerror("Error", "Selecciona un aeropuerto de la lista.")
        return
    for a in airports:
        if a.code == code:
            SetSchengen(a)
            RefreshAirportList()
            messagebox.showinfo("Set Schengen", f"{code} -> Schengen: {a.schengen}")
            break


def ShowClick():
    if len(airports) == 0:
        messagebox.showinfo("Airport List", "No airports loaded.")
        return
    texto = ""
    for a in airports:
        texto = texto + f"{a.code} Lat:{a.lat:.4f} Lon:{a.lon:.4f} Schengen:{a.schengen}\n"
    messagebox.showinfo("Airport List", texto)


def SaveSchengenClick():
    if len(airports) == 0:
        messagebox.showerror("Error", "No airports loaded.\nPlease load airports first.")
        return
    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    if filename:
        result = SaveSchengenAirports(airports, filename)
        if result == -1:
            messagebox.showerror("Error", "No Schengen airports to save.")
        else:
            messagebox.showinfo("Save Schengen", "Schengen airports saved successfully.")


def PlotAirportsClick():
    PlotAirports(airports)


def GoogleEarthClick():
    MapAirports(airports)


# Versión 2

def ArrivalsClick():
    filename = filedialog.askopenfilename()
    if filename:
        LoadArrivals(filename)


def SaveAircraftClick():
    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No flights loaded.\nPlease load arrivals before saving.")
        return

    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    if filename:
        SaveFlights(aircrafts, filename)


def PlotArrivalsTimeClick():
    PlotArrivals(aircrafts)


def PlotArrivalsCompanyClick():
    PlotAirlines(aircrafts)


def PlotSchengenClick():
    PlotFlightsType(aircrafts)


def ShowTrajectoriesClick():
    if len(aircrafts) == 0:
        messagebox.showinfo("Trajectories", "No hay vuelos cargados.")
        return

    top = tk.Toplevel(window)
    top.title("Show Trajectories")
    top.geometry("420x400")

    tk.Label(top, text="Vuelos cargados:", font=("Courier", 10, "bold")).pack(pady=(10, 2))

    frame = tk.Frame(top)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    for av in aircrafts:
        listbox.insert(tk.END, f"{av.id}  {av.origin}  {av.time}  {av.comp}")

    def on_show():
        top.destroy()
        MapFlights(aircrafts)

    tk.Button(top, text="Mostrar en Google Earth (KML)", command=on_show).pack(pady=8)


def LongTrajectoriesClick():
    long_flights = LongDistanceArrivals(aircrafts)
    if len(long_flights) == 0:
        messagebox.showinfo("Long Trajectories", "No long distance arrivals found (>2000 km).")
        return
    MapFlights(long_flights)


# Versión 3

def LoadAirportStructureClick():
    global bcn
    filename = filedialog.askopenfilename(
        title="Select airport structure file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename:
        result = LoadAirportStructure(filename)
        if result == -1:
            messagebox.showerror("Error",
                                 "Could not load airport structure.\nCheck that the file and airline files exist.")
        else:
            bcn = result
            messagebox.showinfo("Airport Structure", f"Airport {bcn.code} loaded successfully.\n"
                                                     f"{len(bcn.terminals)} terminal(s) found.")


def AssignGatesClick():
    global bcn

    if bcn is None:
        messagebox.showerror("Error", "Airport structure not loaded.\nPlease load the airport structure first.")
        return

    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No arrivals loaded.\nPlease load arrivals first.")
        return

    assigned = 0
    no_terminal = 0
    no_gate = 0

    for aircraft in aircrafts:
        terminal_name = SearchTerminal(bcn, aircraft.comp)
        if terminal_name == "":
            no_terminal += 1
        else:
            result = AssignGate(bcn, aircraft)
            if result == -1:
                no_gate += 1
            else:
                assigned += 1

    # Mostrar ventana con tabla de resultados
    top = tk.Toplevel(window)
    top.title("Gate Assignment")
    top.geometry("600x450")

    tk.Label(top, text=f"Assigned: {assigned}   |   No terminal found: {no_terminal}   |   No free gate: {no_gate}",
             font=("Courier", 10, "bold")).pack(pady=(10, 2))

    frame = tk.Frame(top)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    header = f"{'GATE':<22} {'STATUS':<10} {'AIRCRAFT':<12} {'AIRLINE'}"
    listbox.insert(tk.END, header)
    listbox.insert(tk.END, "-" * 55)

    occupancy = GateOccupancy(bcn)
    for gate_info in occupancy:
        gate_name = gate_info[0]
        status = gate_info[1]
        aircraft_id = gate_info[2]
        comp = gate_info[3]

        if status == "occupied":
            listbox.insert(tk.END, f"{gate_name:<22} {'OCCUPIED':<10} {aircraft_id:<12} {comp}")
        else:
            listbox.insert(tk.END, f"{gate_name:<22} {'FREE':<10} {'':<12} {''}")

    tk.Button(top, text="Close", command=top.destroy).pack(pady=8)


# Construcción de la ventana

window = tk.Tk()
window.geometry("800x600")
window.title("Airport project")
window.rowconfigure(0, weight=0)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=0)
window.rowconfigure(3, weight=0)
window.rowconfigure(4, weight=0)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=1)

tituloLabel = Label(window, text="Versión 3", font=("Courier", 20, "italic"))
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)

list_frame = tk.LabelFrame(window, text="Aeropuertos")
list_frame.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
list_frame.rowconfigure(0, weight=1)
list_frame.columnconfigure(0, weight=1)

scrollbar_ap = tk.Scrollbar(list_frame)
scrollbar_ap.grid(row=0, column=1, sticky=tk.N + tk.S)

airport_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar_ap.set, font=("Courier", 10))
airport_listbox.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
scrollbar_ap.config(command=airport_listbox.yview)

# Frame Versión 1

button_version1_frame = tk.LabelFrame(window, text="Versión 1")
button_version1_frame.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

AddButton = tk.Button(button_version1_frame, text="Add Airport", command=AddClick)
AddButton.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

DeleteButton = tk.Button(button_version1_frame, text="Delete Airport", command=DeleteClick)
DeleteButton.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

LoadButton = tk.Button(button_version1_frame, text="Load Airports", command=LoadClick)
LoadButton.grid(row=0, column=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

SetSchengenButton = tk.Button(button_version1_frame, text="Set Schengen", command=SetSchengenClick)
SetSchengenButton.grid(row=0, column=3, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

ShowButton = tk.Button(button_version1_frame, text="Airport List", command=ShowClick)
ShowButton.grid(row=0, column=4, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

SaveSchengenButton = tk.Button(button_version1_frame, text="Save Schengen", command=SaveSchengenClick)
SaveSchengenButton.grid(row=0, column=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

PlotSchengenButton = tk.Button(button_version1_frame, text="Plot Schengen", command=PlotAirportsClick)
PlotSchengenButton.grid(row=0, column=6, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

GoogleEarthButton = tk.Button(button_version1_frame, text="Google Earth", command=GoogleEarthClick)
GoogleEarthButton.grid(row=0, column=7, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

# Frame Versión 2

button_version2_frame = tk.LabelFrame(window, text="Versión 2")
button_version2_frame.grid(row=3, column=0, columnspan=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

ArrivalsButton = tk.Button(button_version2_frame, text="Load Arrivals", command=ArrivalsClick)
ArrivalsButton.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

SaveAircraftButton = tk.Button(button_version2_frame, text="Save Aircraft", command=SaveAircraftClick)
SaveAircraftButton.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

PlotArrivalsTimeButton = tk.Button(button_version2_frame, text="Plot Arrivals/Time", command=PlotArrivalsTimeClick)
PlotArrivalsTimeButton.grid(row=0, column=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

PlotArrivalsCompanyButton = tk.Button(button_version2_frame, text="Plot Arrivals/Company",
                                      command=PlotArrivalsCompanyClick)
PlotArrivalsCompanyButton.grid(row=0, column=3, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

PlotSchengenArrivalsButton = tk.Button(button_version2_frame, text="Plot Schengen Arrivals", command=PlotSchengenClick)
PlotSchengenArrivalsButton.grid(row=0, column=4, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

ShowTrajectoriesButton = tk.Button(button_version2_frame, text="Show Trajectories", command=ShowTrajectoriesClick)
ShowTrajectoriesButton.grid(row=0, column=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

ShowLongTrajectoriesButton = tk.Button(button_version2_frame, text="Show Long Trajectories",
                                       command=LongTrajectoriesClick)
ShowLongTrajectoriesButton.grid(row=0, column=6, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

# Frame Versión 3

button_version3_frame = tk.LabelFrame(window, text="Versión 3")
button_version3_frame.grid(row=4, column=0, columnspan=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

LoadStructureButton = tk.Button(button_version3_frame, text="Load Airport Structure", command=LoadAirportStructureClick)
LoadStructureButton.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

AssignGatesButton = tk.Button(button_version3_frame, text="Assign Gates", command=AssignGatesClick)
AssignGatesButton.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

window.mainloop()