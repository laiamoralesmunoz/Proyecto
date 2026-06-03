from airport import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from matplotlib.figure import Figure


# Clases que representan la estructura de puertas del aeropuerto
class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = ""
        self.aircraft_comp = ""


class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type  # "Schengen" o "non-Schengen"
        self.gates = []


class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = []


class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []


def SetGates(area, init_gate, end_gate, prefix):
    if end_gate <= init_gate:
        return -1

    area.gates = []

    i = init_gate
    while i <= end_gate:
        name = prefix + str(i)
        gate = Gate(name)
        area.gates.append(gate)
        i = i + 1

    return 0


def LoadAirlines(terminal, t_name, folder):
    filename = os.path.join(folder, t_name + "_Airlines.txt")

    try:
        f = open(filename, 'r')

        terminal.airlines = []

        for line in f:
            parts = line.split()
            if len(parts) > 0:
                icao = parts[-1]  # El código ICAO es el último elemento de la línea
                terminal.airlines.append(icao)

        f.close()
        return 0

    except FileNotFoundError:
        return -1


def LoadAirportStructure(filename):
    # La carpeta del fichero es necesaria para encontrar los ficheros de aerolíneas
    folder = os.path.dirname(os.path.abspath(filename))

    try:
        file = open(filename, "r")

        line = file.readline()
        parts = line.split()

        code = parts[0]
        num_terminals = int(parts[1])

        bcn = BarcelonaAP(code)

        for i in range(num_terminals):
            line = file.readline()
            parts = line.split()

            t_name = parts[1]
            num_areas = int(parts[2])

            terminal = Terminal(t_name)

            LoadAirlines(terminal, t_name, folder)

            for j in range(num_areas):
                line = file.readline()
                parts = line.split()

                area_name = parts[1]
                area_type = parts[2]

                init_gate = int(parts[4])
                end_gate = int(parts[6])

                area = BoardingArea(area_name, area_type)

                # El prefijo combina terminal y área para que cada puerta tenga nombre único
                prefix = t_name + area_name + "G"

                SetGates(area, init_gate, end_gate, prefix)

                terminal.boarding_areas.append(area)

            bcn.terminals.append(terminal)

        file.close()

        return bcn

    except:
        return -1


def GateOccupancy(bcn):
    occupancy = []

    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if gate.occupied:
                    status = "occupied"
                else:
                    status = "free"
                occupancy.append([gate.name, status, gate.aircraft_id, gate.aircraft_comp])

    return occupancy


def PlotAirportOccupancy(bcn, terminal_index=0):
    import matplotlib.patches as mpatches
    from matplotlib.figure import Figure

    COLOR_TERMINAL = "#2e7ea6"
    COLOR_FREE = "#27ae60"
    COLOR_OCCUPIED = "#e74c3c"

    bar_height = 0.5
    corr_width = 0.35
    gate_w = 0.55
    gate_h = 0.28
    gate_gap = 0.38
    area_spacing = 2.0

    terminal = bcn.terminals[terminal_index]

    num_areas = len(terminal.boarding_areas)

    # Calcular el máximo de puertas para dimensionar el gráfico
    max_gates = 0
    for area in terminal.boarding_areas:
        if len(area.gates) > max_gates:
            max_gates = len(area.gates)

    fig_w = max(10, num_areas * area_spacing + 2.5)
    fig_h = max(5, max_gates * gate_gap + 3.5)

    fig = Figure(figsize=(fig_w, fig_h), dpi=100)
    ax = fig.add_subplot(111)
    ax.axis('off')

    ax.text(0.3, fig_h - 0.3, terminal.name, fontsize=14, fontweight='bold', va='top')

    bar_y = fig_h - 1.4
    total_w = (num_areas - 1) * area_spacing + corr_width + 0.6

    bar_rect = mpatches.FancyBboxPatch((0.2, bar_y), total_w, bar_height, boxstyle="square,pad=0",
                                       facecolor=COLOR_TERMINAL, edgecolor="none")
    ax.add_patch(bar_rect)

    for a_idx, area in enumerate(terminal.boarding_areas):
        cx = 0.5 + a_idx * area_spacing

        num_gates = len(area.gates)
        corr_height = num_gates * gate_gap + 0.3

        corr_rect = mpatches.FancyBboxPatch(
            (cx - corr_width / 2, bar_y - corr_height), corr_width, corr_height, boxstyle="square,pad=0",
            facecolor=COLOR_TERMINAL, edgecolor="none")
        ax.add_patch(corr_rect)

        ax.text(cx, bar_y - corr_height - 0.2, terminal.name + area.name, ha='center', va='top', fontsize=9,
                fontweight='bold')

        gate_x = cx + corr_width / 2 + 0.06

        for g_idx, gate in enumerate(area.gates):
            gate_cy = bar_y - 0.2 - g_idx * gate_gap
            color = COLOR_OCCUPIED if gate.occupied else COLOR_FREE

            g_rect = mpatches.FancyBboxPatch((gate_x, gate_cy - gate_h / 2), gate_w, gate_h, boxstyle="round,pad=0.02",
                                             facecolor=color, edgecolor="white", linewidth=0.5)
            ax.add_patch(g_rect)

            # Extraer solo los dígitos del nombre para mostrar dentro del rectángulo
            digits = ""
            for ch in gate.name:
                if ch.isdigit():
                    digits = digits + ch

            gate_label = "G" + digits

            ax.text(gate_x + gate_w / 2, gate_cy, gate_label, ha='center', va='center', fontsize=5, color='white',
                    fontweight='bold')

    ax.set_xlim(-0.3, fig_w)
    ax.set_ylim(-0.8, fig_h)
    fig.tight_layout()

    return fig


def IsAirlineInTerminal(terminal, name):
    if name == "":
        return False, -1

    if len(terminal.airlines) == 0:
        return False

    encontrado = False
    i = 0

    while i < len(terminal.airlines) and not encontrado:
        if terminal.airlines[i] == name:
            encontrado = True
        else:
            i = i + 1

    if encontrado:
        return True
    else:
        return False


def SearchTerminal(bcn, name):
    if name == "":
        return ""

    i = 0
    encontrado = False
    terminal_name = ""

    while i < len(bcn.terminals) and not encontrado:
        terminal = bcn.terminals[i]
        result = IsAirlineInTerminal(terminal, name)

        if result == True:
            encontrado = True
            terminal_name = terminal.name
        else:
            i = i + 1

    return terminal_name


def AssignGate(bcn, aircraft):
    terminal_name = SearchTerminal(bcn, aircraft.comp)

    if terminal_name == "":
        return -1

    # Determinar el tipo de área según si el vuelo es Schengen o no
    schengen = IsSchengenAirport(aircraft.origin)

    if schengen:
        area_type = "Schengen"
    else:
        area_type = "non-Schengen"

    terminal = None
    for t in bcn.terminals:
        if t.name == terminal_name:
            terminal = t
            break

    # Buscar la primera puerta libre del área correcta
    for area in terminal.boarding_areas:
        if area.type == area_type:
            for gate in area.gates:
                if not gate.occupied:
                    gate.occupied = True
                    gate.aircraft_id = aircraft.id
                    gate.aircraft_comp = aircraft.comp
                    return 0

    return -1


def AssignNightGates(bcn, aircrafts):
    if len(aircrafts) == 0:
        return -1

    for avion in aircrafts:
        if avion.origin == "" and avion.time_landing == "":
            AssignGate(bcn, avion)

    return 0


def FreeGate(bcn, id):
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if gate.aircraft_id == id:
                    gate.occupied = False
                    gate.aircraft_id = ""
                    gate.aircraft_comp = ""
                    return 0

    return -1


def AssignGatesAtTime(bcn, aircrafts, time):
    not_assigned = 0

    hour = int(time.split(":")[0])
    min = int(time.split(":")[1])
    time_total = hour * 60 + min
    time_end = time_total + 60

    # Primero liberar las puertas de aviones que ya han salido
    for avion in aircrafts:
        if avion.time_departure != "":
            departure_hour = int(avion.time_departure.split(":")[0])
            departure_min = int(avion.time_departure.split(":")[1])
            departure_total = departure_hour * 60 + departure_min

            if departure_total <= time_total:
                FreeGate(bcn, avion.id)

    # Asignar puertas a los aviones que aterrizan en esta hora
    for avion in aircrafts:
        if avion.time_landing != "":
            landing_hour = int(avion.time_landing.split(":")[0])
            landing_min = int(avion.time_landing.split(":")[1])
            landing_total = landing_hour * 60 + landing_min

            if time_total <= landing_total < time_end:
                result = AssignGate(bcn, avion)
                if result == -1:
                    not_assigned = not_assigned + 1

    return not_assigned


def PlotDayOccupancy(bcn, aircrafts):
    if len(aircrafts) == 0:
        return -1

    hours = list(range(24))

    terminal_names = []
    for terminal in bcn.terminals:
        terminal_names.append(terminal.name)

    # Inicializar contadores de puertas ocupadas por terminal y hora
    occupied_per_terminal = []
    for t in range(len(bcn.terminals)):
        occupied_per_terminal.append([0] * 24)

    not_assigned_per_hour = [0] * 24

    for h in range(24):
        time_str = str(h) + ":00"

        not_assigned = AssignGatesAtTime(bcn, aircrafts, time_str)
        not_assigned_per_hour[h] = not_assigned

        for t_idx, terminal in enumerate(bcn.terminals):
            count = 0
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    if gate.occupied:
                        count = count + 1
            occupied_per_terminal[t_idx][h] = count

    fig = Figure(figsize=(5.2, 3.2), dpi=100)
    ax1 = fig.add_subplot(111)
    bar_width = 0.35
    x = list(range(24))

    colors = ["#2e86c1", "#e67e22", "#27ae60", "#8e44ad", "#c0392b"]

    # Gráfico de barras apiladas por terminal
    bottom = [0] * 24
    for t_idx in range(len(terminal_names)):
        ax1.bar(x, occupied_per_terminal[t_idx],
                bottom=bottom,
                width=bar_width,
                label=terminal_names[t_idx],
                color=colors[t_idx % len(colors)],
                alpha=0.85)

        for h in range(24):
            bottom[h] = bottom[h] + occupied_per_terminal[t_idx][h]

    ax1.set_xlabel("Hour of the day")
    ax1.set_ylabel("Number of occupied gates")
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(h) + ":00" for h in hours], rotation=45, ha='right', fontsize=7)
    ax1.set_title("Gate Occupancy and Unassigned Aircraft per Hour - " + bcn.code)
    ax1.legend(loc='upper left')

    # Segundo eje Y para mostrar los aviones no asignados
    ax2 = ax1.twinx()
    ax2.plot(x, not_assigned_per_hour,
             color='red', marker='o', linewidth=2, label='Not assigned')
    ax2.set_ylabel("Aircraft not assigned", color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.legend(loc='upper right')

    fig.tight_layout()
    return fig