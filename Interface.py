import tkinter as tk
from aircraft import *
from tkinter import messagebox
from tkinter import *
from airport import *
from tkinter import filedialog
from LEBL import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import os

# Variables globales de estado de la aplicación
bcn = None
gates_assigned = False
current_terminal_index = 0
departures = []
movements = []
night_aircrafts = []
gates_assigned_at_time = False


def RefreshAirportList():
    airport_listbox.delete(0, tk.END)
    for a in airports:
        schengen_str = "S" if a.schengen else "NS"
        airport_listbox.insert(tk.END, f"{a.code}   {a.lat:.6f}   {a.lon:.6f}   [{schengen_str}]")


# ── Versión 1: gestión de aeropuertos ──────────────────────────────────────────

def LoadClick():
    filename = filedialog.askopenfilename()
    if not filename:
        return

    previous_count = len(airports)
    LoadAirports(filename)
    loaded = len(airports) - previous_count

    if loaded == 0:
        messagebox.showerror(
            "Error",
            "No airports were loaded.\n"
            "Make sure the file has the correct format:\n"
            "CODE LAT LON\n"
            "LEBL N412809 E0020500\n..."
        )
        return

    RefreshAirportList()
    messagebox.showinfo("Load Airports", f"{loaded} airports loaded successfully.")


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


def GoogleEarthClick():
    if len(airports) == 0:
        messagebox.showerror("Error", "No airports loaded.\nPlease load airports first.")
        return

    MapAirports(airports)
    os.startfile("GoogleEarth_Airports.kml")


airport_plot_canvas = None


def PlotAirportsInside():
    # Dibuja el gráfico dentro de la ventana en lugar de abrir una ventana nueva
    global airport_plot_canvas

    if len(airports) == 0:
        messagebox.showerror("Error", "No airports loaded.")
        return

    schengen = 0
    no_schengen = 0

    for a in airports:
        if a.schengen:
            schengen += 1
        else:
            no_schengen += 1

    fig = Figure(figsize=(4.4, 3.6), dpi=100)
    ax = fig.add_subplot(111)

    ax.bar(["Airports"], [schengen], label="Schengen", color="yellow")
    ax.bar(["Airports"], [no_schengen], bottom=[schengen], label="No Schengen", color="blue")

    ax.set_title("Schengen vs No Schengen")
    ax.set_ylabel("Number of airports")
    ax.legend()

    if airport_plot_canvas is not None:
        airport_plot_canvas.get_tk_widget().destroy()

    airport_plot_canvas = FigureCanvasTkAgg(fig, master=airport_plot_frame)
    airport_plot_canvas.draw()
    airport_plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def AddAirportFromEntries():
    code = add_code_entry.get().strip().upper()
    lat_text = add_lat_entry.get().strip()
    lon_text = add_lon_entry.get().strip()

    if len(code) != 4:
        messagebox.showerror("Error", "ICAO code must have 4 characters.")
        return

    try:
        lat = float(lat_text)
        lon = float(lon_text)
    except ValueError:
        messagebox.showerror("Error", "Latitude and longitude must be numbers.")
        return

    a = airport(code, lat, lon)
    AddAirport(airports, a)
    RefreshAirportList()

    # Limpiar los campos de entrada tras añadir
    add_code_entry.delete(0, tk.END)
    add_lat_entry.delete(0, tk.END)
    add_lon_entry.delete(0, tk.END)


def DeleteAirportFromEntry():
    code = delete_code_entry.get().strip().upper()

    if len(code) != 4:
        messagebox.showerror("Error", "ICAO code must have 4 characters.")
        return

    result = RemoveAirport(airports, code)

    if result == -1:
        messagebox.showerror("Error", f"Airport {code} not found.")
    else:
        RefreshAirportList()
        delete_code_entry.delete(0, tk.END)


def SetSchengenFromEntry():
    code = set_code_entry.get().strip().upper()

    if len(code) != 4:
        messagebox.showerror("Error", "ICAO code must have 4 characters.")
        return

    found = False

    i = 0
    while i < len(airports) and not found:
        a = airports[i]
        if a.code == code:
            SetSchengen(a)
            found = True
        i = i + 1

    if not found:
        messagebox.showerror("Error", f"Airport {code} not found.")
    else:
        RefreshAirportList()
        set_code_entry.delete(0, tk.END)
        messagebox.showinfo("Set Schengen", f"{code} -> Schengen: {a.schengen}")


# ── Versión 2: gestión de vuelos ───────────────────────────────────────────────

def ArrivalsClick():
    filename = filedialog.askopenfilename()
    if not filename:
        return

    aircrafts.clear()
    aircrafts.extend(LoadArrivals(filename))

    if len(aircrafts) == 0:
        messagebox.showerror(
            "Error",
            "No arrivals were loaded.\n"
            "Make sure the file has the correct format:\n"
            "AIRCRAFT ORIGIN ARRIVAL AIRLINE\n"
            "ECMKV LYBE 0:04 VLG\n..."
        )
        return

    RefreshArrivalsList()
    messagebox.showinfo("Load Arrivals", f"{len(aircrafts)} flights loaded.")


def LoadDeparturesClick():
    global departures
    global movements
    global night_aircrafts

    if len(aircrafts) == 0:
        messagebox.showerror(
            "Error",
            "No arrivals loaded.\nPlease load arrivals first."
        )
        return

    filename = filedialog.askopenfilename()

    if filename:
        departures.clear()
        departures.extend(LoadDepartures(filename))

        if len(departures) == 0:
            messagebox.showerror(
                "Error",
                "No departures were loaded.\n"
                "Make sure the file has the correct format:\n"
                "AIRCRAFT DESTINATION DEPARTURE AIRLINE\n"
                "ECMKV LYBE 0:04 VLG\n..."
            )
            return

        result = MergeMovements(aircrafts, departures)

        if result == -1:
            messagebox.showerror(
                "Error",
                "Could not merge arrivals and departures."
            )
            return

        movements.clear()
        movements.extend(result)

        night_result = NightAircraft(movements)

        if night_result == -1:
            night_aircrafts.clear()
        else:
            night_aircrafts.clear()
            night_aircrafts.extend(night_result)

        messagebox.showinfo("Load Departures",
                            f"Departures loaded: {len(departures)}\n"
                            f"Movements merged: {len(movements)}\n"
                            f"Night aircrafts: {len(night_aircrafts)}")


def SaveAircraftClick():
    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No flights loaded.\nPlease load arrivals before saving.")
        return

    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    if filename:
        SaveFlights(aircrafts, filename)


def ShowTrajectoriesClick():
    if len(aircrafts) == 0:
        messagebox.showinfo("Trajectories", "No hay vuelos cargados.")
        return

    if len(airports) == 0:
        messagebox.showerror("Error", "No airports loaded.\nPlease load airports first.")
        return

    # Mostrar ventana de confirmación con la lista de vuelos antes de generar el KML
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
        listbox.insert(tk.END, f"{av.id}  {av.origin}  {av.time_landing}  {av.comp}")

    def on_show():
        top.destroy()
        MapFlights(aircrafts, "GoogleEarth_Trajectories.kml")
        os.startfile("GoogleEarth_Trajectories.kml")

    tk.Button(top, text="Create Trajectories KML", command=on_show).pack(pady=8)


def LongTrajectoriesClick():
    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No arrivals loaded.")
        return

    if len(airports) == 0:
        messagebox.showerror("Error", "No airports loaded.\nPlease load airports first.")
        return

    long_flights = LongDistanceArrivals(aircrafts)

    if len(long_flights) == 0:
        messagebox.showinfo("Long Trajectories", "No long distance arrivals found (>2000 km).")
        return

    top = tk.Toplevel(window)
    top.title("Show Long Trajectories")
    top.geometry("420x400")

    tk.Label(top, text="Long distance flights:", font=("Courier", 10, "bold")).pack(pady=(10, 2))

    frame = tk.Frame(top)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    for av in long_flights:
        listbox.insert(tk.END, f"{av.id}  {av.origin}  {av.time_landing}  {av.comp}")

    def on_show():
        top.destroy()
        MapFlights(long_flights, "GoogleEarth_LongTrajectories.kml")
        os.startfile("GoogleEarth_LongTrajectories.kml")

    tk.Button(top, text="Create Long Trajectories KML", command=on_show).pack(pady=8)


def RefreshArrivalsList():
    arrivals_listbox.delete(0, tk.END)

    arrivals_listbox.insert(tk.END, f"{'ID':<10} {'ORIGIN':<8} {'TIME':<8} {'AIRLINE'}")
    arrivals_listbox.insert(tk.END, "-" * 40)

    for a in aircrafts:
        arrivals_listbox.insert(tk.END, f"{a.id:<10} {a.origin:<8} {a.time_landing:<8} {a.comp}")


def PlotArrivalsTimeInside():
    global arrivals_time_canvas

    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No arrivals loaded.")
        return

    horas = [0] * 24

    for avion in aircrafts:
        hora = int(avion.time_landing.split(":")[0])
        horas[hora] = horas[hora] + 1

    fig = Figure(figsize=(5.2, 3.5), dpi=100)
    ax = fig.add_subplot(111)

    ax.bar(range(24), horas)
    ax.set_title("Arrivals / Time")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Flights")

    if arrivals_time_canvas is not None:
        arrivals_time_canvas.get_tk_widget().destroy()

    arrivals_time_canvas = FigureCanvasTkAgg(fig, master=arrivals_time_frame)
    arrivals_time_canvas.draw()
    arrivals_time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=False)


def PlotAirlinesInside():
    global arrivals_company_canvas

    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No arrivals loaded.")
        return

    flights = []
    comp = []

    for avion in aircrafts:
        aerolinea = avion.comp

        if aerolinea not in comp:
            comp.append(aerolinea)
            flights.append(1)
        else:
            i = comp.index(aerolinea)
            flights[i] = flights[i] + 1

    fig = Figure(figsize=(5.2, 3.5), dpi=100)
    ax = fig.add_subplot(111)

    ax.bar(comp, flights)
    ax.set_title("Arrivals / Company")
    ax.set_xlabel("Airline")
    ax.set_ylabel("Flights")
    ax.tick_params(axis="x", labelrotation=90, labelsize=6)

    if arrivals_company_canvas is not None:
        arrivals_company_canvas.get_tk_widget().destroy()

    arrivals_company_canvas = FigureCanvasTkAgg(fig, master=arrivals_company_frame)
    arrivals_company_canvas.draw()
    arrivals_company_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=False)


def PlotFlightsTypeInside():
    global arrivals_schengen_canvas

    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No arrivals loaded.")
        return

    cont_sch = 0
    cont_no_sch = 0

    for avion in aircrafts:
        if IsSchengenAirport(avion.origin):
            cont_sch = cont_sch + 1
        else:
            cont_no_sch = cont_no_sch + 1

    fig = Figure(figsize=(5.2, 3.5), dpi=100)
    ax = fig.add_subplot(111)

    ax.bar(["Flights"], [cont_sch], label="Schengen", color="yellow")
    ax.bar(["Flights"], [cont_no_sch], bottom=[cont_sch], label="No Schengen", color="blue")
    ax.set_title("Schengen Arrivals")
    ax.set_ylabel("Flights")
    ax.legend()

    if arrivals_schengen_canvas is not None:
        arrivals_schengen_canvas.get_tk_widget().destroy()

    arrivals_schengen_canvas = FigureCanvasTkAgg(fig, master=arrivals_schengen_frame)
    arrivals_schengen_canvas.draw()
    arrivals_schengen_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=False)


# ── Versión 3 y 4: asignación de puertas ──────────────────────────────────────

def GatePlotClick():
    global gate_plot_canvas
    global current_terminal_index

    if bcn is None:
        messagebox.showerror("Error", "Airport structure not loaded.")
        return

    if not gates_assigned:
        messagebox.showerror("Error", "Gates have not been assigned yet.\nPlease press Assign Gates first.")
        return

    fig = PlotAirportOccupancy(bcn, current_terminal_index)

    if gate_plot_canvas is not None:
        gate_plot_canvas.get_tk_widget().destroy()

    gate_plot_canvas = FigureCanvasTkAgg(fig, master=gate_plot_frame)
    gate_plot_canvas.draw()
    gate_plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def PlotDayOccupancyClick():
    global day_occupancy_canvas

    if bcn is None:
        messagebox.showerror("Error", "Airport structure not loaded.")
        return

    # Usar movements si están disponibles, si no usar solo los arrivals
    if len(movements) > 0:
        aircrafts_to_plot = movements
    elif len(aircrafts) > 0:
        aircrafts_to_plot = aircrafts
    else:
        messagebox.showerror("Error", "No aircrafts loaded.")
        return

    fig = PlotDayOccupancy(bcn, aircrafts_to_plot)

    if fig == -1:
        messagebox.showerror("Error", "Could not create day occupancy plot.")
        return

    if day_occupancy_canvas is not None:
        day_occupancy_canvas.get_tk_widget().destroy()

    day_occupancy_canvas = FigureCanvasTkAgg(fig, master=day_occupancy_plot_frame)
    day_occupancy_canvas.draw()
    day_occupancy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


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


def ShowOccupancyClick():
    global gates_assigned

    if bcn is None:
        messagebox.showerror("Error", "Airport structure not loaded.")
        return

    if not gates_assigned:
        messagebox.showerror(
            "Error",
            "Gates have not been assigned yet.\nPlease press Assign Gates first."
        )
        return

    gate_occupancy_listbox.delete(0, tk.END)

    header = f"{'GATE':<16} {'STATUS':<10} {'AIRCRAFT':<12} {'AIRLINE'}"
    gate_occupancy_listbox.insert(tk.END, header)
    gate_occupancy_listbox.insert(tk.END, "-" * 55)

    occupancy = GateOccupancy(bcn)

    for gate_info in occupancy:
        gate_name = gate_info[0]
        status = gate_info[1]
        aircraft_id = gate_info[2]
        comp = gate_info[3]

        gate_occupancy_listbox.insert(tk.END, f"{gate_name:<16} {status.upper():<10} {aircraft_id:<12} {comp}")

def IsValidTimeFormat(time):
    # Acepta tanto H:MM como HH:MM
    parts = time.split(":")

    if len(parts) != 2:
        return False

    hour_text = parts[0]
    minute_text = parts[1]

    if not hour_text.isdigit() or not minute_text.isdigit():
        return False

    if len(minute_text) != 2:
        return False

    hour = int(hour_text)
    minute = int(minute_text)

    if hour < 0 or hour > 23:
        return False

    if minute < 0 or minute > 59:
        return False

    return True

def AssignGatesAtTimeClick():
    global bcn
    global gates_assigned
    global gates_assigned_at_time

    if bcn is None:
        messagebox.showerror("Error", "Airport structure not loaded.")
        return

    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No arrivals loaded.")
        return

    time = time_entry.get().strip()

    if time == "":
        messagebox.showerror("Error", "Please enter a time.")
        return

    if not IsValidTimeFormat(time):
        messagebox.showerror(
            "Error",
            "Invalid time format.\n"
            "Please enter the time as HH:MM or H:MM\n"
            "Examples: 08:00, 14:30, 9:00\n"
            "Hours must be 0-23, minutes 0-59."
        )
        return

    # Usar movements si hay salidas cargadas, si no solo arrivals
    if len(movements) > 0:
        aircrafts_to_assign = movements
    else:
        aircrafts_to_assign = aircrafts

    # Asignar puertas nocturnas solo la primera vez
    if len(night_aircrafts) > 0 and not gates_assigned_at_time:
        AssignNightGates(bcn, night_aircrafts)

    result = AssignGatesAtTime(bcn, aircrafts_to_assign, time)

    if result == -1:
        messagebox.showerror("Error", "Gate assignment failed.")
        return

    gates_assigned = True
    gates_assigned_at_time = True

    ShowOccupancyClick()
    GatePlotClick()

    messagebox.showinfo("Assign Gates At Time", f"Gates assigned at {time}.\nNot assigned: {result}")


def NextTerminalClick():
    global current_terminal_index

    if bcn is None:
        messagebox.showerror("Error", "Airport structure not loaded.")
        return

    # Avanzar al siguiente terminal, volviendo al primero si se llega al final
    current_terminal_index = current_terminal_index + 1

    if current_terminal_index >= len(bcn.terminals):
        current_terminal_index = 0

    GatePlotClick()


# ── Construcción de la ventana principal ──────────────────────────────────────

window = tk.Tk()
window.geometry("1920x1080")
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

tituloLabel = Label(window, text="Airport Management", font=("Courier", 20, "italic"))
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)

# Notebook con tres pestañas: aeropuertos, llegadas y puertas
notebook = ttk.Notebook(window)
notebook.grid(row=1, column=0, columnspan=5, sticky=N + S + E + W, padx=5, pady=5)

airports_tab = tk.Frame(notebook)
notebook.add(airports_tab, text="Airports")
arrivals_tab = tk.Frame(notebook)
notebook.add(arrivals_tab, text="Arrivals")
gates_tab = tk.Frame(notebook)
notebook.add(gates_tab, text="Gate Assignment")

# ── Pestaña Airports ───────────────────────────────────────────────────────────

airports_tab.columnconfigure(0, weight=0, minsize=360)
airports_tab.columnconfigure(1, weight=1)
airports_tab.rowconfigure(0, weight=1)

left_frame = tk.Frame(airports_tab, width=360)
left_frame.grid(row=0, column=0, sticky=N + S + E + W, padx=20, pady=20)
left_frame.grid_propagate(False)
left_frame.columnconfigure(0, weight=1)
left_frame.columnconfigure(1, weight=3)

right_frame = tk.Frame(airports_tab)
right_frame.grid(row=0, column=1, sticky=N + S + E + W, padx=(40, 10), pady=10)

# Columna izquierda: controles de añadir, eliminar y Schengen
tk.Label(left_frame, text="Add Airport", font=("Courier", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

tk.Label(left_frame, text="Code").grid(row=1, column=0, sticky=W)
add_code_entry = tk.Entry(left_frame, width=25)
add_code_entry.grid(row=1, column=1, pady=3, sticky=E + W)

tk.Label(left_frame, text="Latitude").grid(row=2, column=0, sticky=W)
add_lat_entry = tk.Entry(left_frame, width=25)
add_lat_entry.grid(row=2, column=1, pady=3, sticky=E + W)

tk.Label(left_frame, text="Longitude").grid(row=3, column=0, sticky=W)
add_lon_entry = tk.Entry(left_frame, width=25)
add_lon_entry.grid(row=3, column=1, pady=3, sticky=E + W)

tk.Button(left_frame, text="Add", width=50, command=AddAirportFromEntries, bg='#D0CFEC').grid(row=4, column=0,columnspan=2, pady=8,sticky=E + W)

tk.Label(left_frame, text="Delete Airport", font=("Courier", 12, "bold")).grid(row=5, column=0, columnspan=2, pady=10)

tk.Label(left_frame, text="Code").grid(row=6, column=0, sticky=W)
delete_code_entry = tk.Entry(left_frame, width=25)
delete_code_entry.grid(row=6, column=1, pady=3, sticky=E + W)

tk.Button(left_frame, text="Delete", width=50, command=DeleteAirportFromEntry, bg='#D0CFEC').grid(row=7, column=0,columnspan=2, pady=8,sticky=E + W)

tk.Label(left_frame, text="Set Schengen", font=("Courier", 12, "bold")).grid(row=8, column=0, columnspan=2, pady=10)

tk.Label(left_frame, text="Code").grid(row=9, column=0, sticky=W)
set_code_entry = tk.Entry(left_frame, width=25)
set_code_entry.grid(row=9, column=1, pady=3, sticky=E + W)

tk.Button(left_frame, text="Set Schengen", width=50, command=SetSchengenFromEntry, bg='#D0CFEC').grid(row=10, column=0,columnspan=2,pady=8,sticky=E + W)

tk.Button(left_frame, text="Save Schengen", width=50, command=SaveSchengenClick, bg='#FC8835').grid(row=11, column=0,columnspan=2,pady=(40, 8),sticky=E + W)

tk.Button(left_frame, text="Google Earth", width=50, command=GoogleEarthClick, bg='#45CB85').grid(row=12, column=0,columnspan=2,pady=(20, 8),sticky=E + W)

# Columna derecha: lista de aeropuertos y gráfico Schengen
right_frame.columnconfigure(0, weight=1)
right_frame.columnconfigure(1, weight=1)
right_frame.rowconfigure(0, weight=1)
right_frame.rowconfigure(1, weight=0)

list_frame = tk.LabelFrame(right_frame, text="Airport List", width=650, height=900)
list_frame.grid(row=0, column=0, padx=(20, 10), pady=(30, 5))
list_frame.grid_propagate(False)
list_frame.pack_propagate(False)

scrollbar_ap = tk.Scrollbar(list_frame)
scrollbar_ap.pack(side=tk.RIGHT, fill=tk.Y)

airport_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar_ap.set, font=("Courier", 10))
airport_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_ap.config(command=airport_listbox.yview)

LoadAirportsButton = tk.Button(right_frame, text="Load Airports", command=LoadClick, bg='#608CEB')
LoadAirportsButton.grid(row=1, column=0, pady=(0, 10))

airport_plot_frame = tk.LabelFrame(right_frame, text="Schengen Plot", width=800, height=900)
airport_plot_frame.grid(row=0, column=1, padx=(10, 20), pady=(30, 5))
airport_plot_frame.grid_propagate(False)
airport_plot_frame.pack_propagate(False)

PlotSchengenButton = tk.Button(right_frame, text="Schengen Plot", command=PlotAirportsInside, bg='#FFDD4A')
PlotSchengenButton.grid(row=1, column=1, pady=(0, 10))

# ── Pestaña Arrivals ───────────────────────────────────────────────────────────

arrivals_time_canvas = None
arrivals_company_canvas = None
arrivals_schengen_canvas = None

arrivals_tab.columnconfigure(0, weight=0, minsize=620)
arrivals_tab.columnconfigure(1, weight=0, minsize=650)

arrivals_tab.rowconfigure(0, weight=0, minsize=370)
arrivals_tab.rowconfigure(1, weight=0, minsize=370)

# Cuadrante superior izquierdo: botones y lista de llegadas
arrivals_top_left_frame = tk.Frame(arrivals_tab, width=700, height=370)
arrivals_top_left_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky=N)
arrivals_top_left_frame.grid_propagate(False)

arrivals_top_left_frame.columnconfigure(0, weight=0, minsize=210)
arrivals_top_left_frame.columnconfigure(1, weight=0, minsize=380)

arrivals_left_frame = tk.Frame(arrivals_top_left_frame, width=260, height=350)
arrivals_left_frame.grid(row=0, column=0, sticky=N, padx=(0, 10), pady=0)
arrivals_left_frame.grid_propagate(False)

tk.Button(arrivals_left_frame, text="Load Arrivals", width=25, command=ArrivalsClick, bg='#608CEB').grid(row=0, column=0,padx=(20, 10),pady=(20, 5),sticky=E)

tk.Button(arrivals_left_frame, text="Save Flights", width=25, command=SaveAircraftClick, bg='#FC8835').grid(row=1,column=0,padx=(20,10),pady=(5,20),sticky=E)

tk.Button(arrivals_left_frame, text="Plot Arrivals/Time", width=25, command=PlotArrivalsTimeInside, bg='#FFDD4A').grid(
    row=2, column=0, padx=(20, 10), pady=(20, 5), sticky=E)

tk.Button(arrivals_left_frame, text="Plot Arrivals/Company", width=25, command=PlotAirlinesInside, bg='#FFDD4A').grid(
    row=3, column=0, padx=(20, 10), pady=5, sticky=E)

tk.Button(arrivals_left_frame, text="Plot Schengen Arrivals", width=25, command=PlotFlightsTypeInside,
          bg='#FFDD4A').grid(row=4, column=0, padx=(20, 10), pady=(5, 20), sticky=E)

tk.Button(arrivals_left_frame, text="Show Trajectories", width=25, command=ShowTrajectoriesClick, bg='#45CB85').grid(
    row=5, column=0, padx=(20, 10), pady=(20, 5), sticky=E)

tk.Button(arrivals_left_frame, text="Show Long Trajectories", width=25, command=LongTrajectoriesClick,
          bg='#45CB85').grid(row=6, column=0, padx=(20, 10), pady=5, sticky=E)

arrivals_list_frame = tk.LabelFrame(arrivals_top_left_frame, text="Arrivals List", width=330, height=350)
arrivals_list_frame.grid(row=0, column=1, sticky=N, padx=(0, 0), pady=0)
arrivals_list_frame.grid_propagate(False)
arrivals_list_frame.pack_propagate(False)

scrollbar_arrivals = tk.Scrollbar(arrivals_list_frame)
scrollbar_arrivals.pack(side=tk.RIGHT, fill=tk.Y)

arrivals_listbox = tk.Listbox(arrivals_list_frame, yscrollcommand=scrollbar_arrivals.set, font=("Courier", 10))
arrivals_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_arrivals.config(command=arrivals_listbox.yview)

# Cuadrantes de gráficos (Schengen, por compañía, por hora)
arrivals_schengen_frame = tk.LabelFrame(arrivals_tab, text="Schengen Plot", width=550, height=320)
arrivals_schengen_frame.grid(row=0, column=1, padx=(10, 10), pady=20, sticky=N + W)
arrivals_schengen_frame.grid_propagate(False)
arrivals_schengen_frame.pack_propagate(False)

arrivals_company_frame = tk.LabelFrame(arrivals_tab, text="Arrivals Company", width=550, height=320)
arrivals_company_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky=N)
arrivals_company_frame.grid_propagate(False)
arrivals_company_frame.pack_propagate(False)

arrivals_time_frame = tk.LabelFrame(arrivals_tab, text="Arrivals Time", width=550, height=320)
arrivals_time_frame.grid(row=1, column=1, padx=(10, 10), pady=10, sticky=N + W)
arrivals_time_frame.grid_propagate(False)
arrivals_time_frame.pack_propagate(False)

# ── Pestaña Gate Assignment ────────────────────────────────────────────────────

gate_plot_canvas = None
day_occupancy_canvas = None

gates_tab.columnconfigure(0, minsize=420)
gates_tab.columnconfigure(1, minsize=650)

gates_tab.rowconfigure(0, weight=1)
gates_tab.rowconfigure(1, weight=1)

gates_left_container = tk.Frame(gates_tab, width=650, height=1100)
gates_left_container.grid(row=0, column=0, rowspan=2, sticky=N, padx=20, pady=20)
gates_left_container.grid_propagate(False)

gates_left_frame = tk.Frame(gates_left_container, width=500, height=210)
gates_left_frame.grid(row=0, column=0)
gates_left_frame.grid_propagate(False)

gate_occupancy_frame = tk.LabelFrame(gates_tab, text="Gate Occupancy", width=550, height=450)
gate_occupancy_frame.grid(row=0, column=1, padx=(0, 20), pady=(20, 10), sticky=W)
gate_occupancy_frame.grid_propagate(False)
gate_occupancy_frame.pack_propagate(False)

day_occupancy_plot_frame = tk.LabelFrame(gates_tab, text="Day Occupancy Plot", width=550, height=450)
day_occupancy_plot_frame.grid(row=1, column=1, padx=(0, 20), pady=(10, 20), sticky=W)
day_occupancy_plot_frame.grid_propagate(False)
day_occupancy_plot_frame.pack_propagate(False)

gate_plot_frame = tk.LabelFrame(gates_left_container, text="Gate Plot", width=600, height=495)
plot_controls = tk.Frame(gate_plot_frame)
plot_controls.pack(side=tk.TOP, pady=5)
gate_plot_frame.grid(row=1, column=0, padx=20, pady=(0, 20))
gate_plot_frame.grid_propagate(False)
gate_plot_frame.pack_propagate(False)

scrollbar_gates = tk.Scrollbar(gate_occupancy_frame)
scrollbar_gates.pack(side=tk.RIGHT, fill=tk.Y)

gate_occupancy_listbox = tk.Listbox(gate_occupancy_frame, yscrollcommand=scrollbar_gates.set, font=("Courier", 12))
gate_occupancy_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_gates.config(command=gate_occupancy_listbox.yview)

gates_left_frame.columnconfigure(0, weight=1)
gates_left_frame.columnconfigure(1, weight=1)

# Columna izquierda: cargar estructura y salidas
tk.Button(gates_left_frame, text="Load Airport Structure", width=25, command=LoadAirportStructureClick,
          bg='#608CEB').grid(row=0, column=0, padx=(20, 10), pady=(40, 8))

tk.Button(gates_left_frame, text="Load Departures", width=25, command=LoadDeparturesClick, bg='#608CEB').grid(row=1,column=0,padx=(20,10),pady=8)

# Campo para introducir la hora de asignación (formato HH:MM)
time_frame = tk.Frame(gates_left_frame)
time_frame.grid(row=2, column=0, padx=(20, 10), pady=(15, 8))

tk.Label(time_frame, text="Time (HH:MM)").pack(side=tk.LEFT, padx=(0, 5))

time_entry = tk.Entry(time_frame, width=10)
time_entry.pack(side=tk.LEFT)

# Columna derecha: asignar puertas y mostrar gráficos
tk.Button(gates_left_frame, text="Assign Gates At Time", width=25, command=AssignGatesAtTimeClick, bg='#D0CFEC').grid(
    row=0, column=1, padx=(10, 20), pady=(40, 8))

tk.Button(gates_left_frame, text="Plot Day Occupancy", width=25, command=PlotDayOccupancyClick, bg='#FFDD4A').grid(
    row=1, column=1, padx=(10, 20), pady=8)

# Botón para navegar entre terminales en el gráfico de puertas
tk.Button(plot_controls, text="Next Terminal", command=NextTerminalClick, bg='#D0CFEC').pack(side=tk.LEFT, padx=5)

window.mainloop()