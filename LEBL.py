from airport import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os


class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = ""
        self.aircraft_comp = ""


class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type
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
                icao = parts[-1]
                terminal.airlines.append(icao)

        f.close()
        return 0

    except FileNotFoundError:
        return -1


def LoadAirportStructure(filename):
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

    for area in terminal.boarding_areas:
        if area.type == area_type:
            for gate in area.gates:
                if not gate.occupied:
                    gate.occupied = True
                    gate.aircraft_id = aircraft.id
                    gate.aircraft_comp = aircraft.comp
                    return 0

    return -1