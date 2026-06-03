from airport import *
import matplotlib.pyplot as plt
import math
from tkinter import messagebox


# Clase que representa un avión con su información de llegada y salida
class Aircraft:
    def __init__(self, id, comp, origin, time_landing, destination, time_departure):
        self.id = id
        self.comp = comp
        self.origin = origin
        self.time_landing = time_landing
        self.destination = destination
        self.time_departure = time_departure


aircrafts = []


def LoadArrivals(filename):
    try:
        S = open(filename, "r")

        linea1 = S.readline()  # Saltar cabecera
        linea = S.readline()

        while linea != "":
            elementos = linea.split()

            if len(elementos) == 4:
                id = elementos[0]
                origin = elementos[1]
                time_landing = elementos[2]
                comp = elementos[3]

                avion = Aircraft(id, comp, origin, time_landing, '', '')
                aircrafts.append(avion)

            linea = S.readline()

        S.close()
        return aircrafts

    except FileNotFoundError:
        return []


def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        messagebox.showerror("Error", "The aircraft list is empty.\nPlease load arrivals first.")
        return

    # Contar cuántos vuelos llegan cada hora
    horas = [0] * 24

    for avion in aircrafts:
        hora = int(avion.time_landing.split(":")[0])
        horas[hora] = horas[hora] + 1

    plt.bar(range(24), horas)
    plt.xlabel("Hours")
    plt.ylabel("Number of arrivals")
    plt.show()


def SaveFlights(aircrafts, filename):
    if len(aircrafts) == 0:
        return -1

    R = open(filename, "w")
    R.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

    for avion in aircrafts:
        # Usar "-" o "0" para campos vacíos
        id_final = avion.id if avion.id != "" else "-"
        origen_final = avion.origin if avion.origin != "" else "-"
        tiempo_final = avion.time_landing if avion.time_landing != "" else "0"
        comp_final = avion.comp if avion.comp != "" else "-"

        linea = id_final + " " + origen_final + " " + tiempo_final + " " + comp_final + "\n"
        R.write(linea)

    R.close()


def PlotAirlines(aircrafts):
    if len(aircrafts) == 0:
        messagebox.showerror("Error", "The aircraft list is empty.\nPlease load arrivals first.")
        return

    flights = []
    comp = []

    # Contar vuelos por aerolínea
    for avion in aircrafts:
        aerolinea = avion.comp
        if aerolinea not in comp:
            comp.append(aerolinea)
            flights.append(1)
        else:
            i = comp.index(aerolinea)
            flights[i] = flights[i] + 1

    plt.bar(comp, flights)
    plt.xlabel("Airline")
    plt.ylabel("Number of flights")
    plt.title("Flights per Airline")
    plt.xticks(rotation=45, ha="right", fontsize=5)
    plt.tight_layout()
    plt.show()


def PlotFlightsType(aircrafts):
    if len(aircrafts) == 0:
        messagebox.showerror("Error", "The aircraft list is empty.\nPlease load arrivals first.")
        return

    cont_sch = 0
    cont_no_sch = 0

    for avion in aircrafts:
        if IsSchengenAirport(avion.origin):
            cont_sch = cont_sch + 1
        else:
            cont_no_sch = cont_no_sch + 1

    plt.bar(["Flights"], [cont_sch], label="Schengen", color="yellow")
    plt.bar(["Flights"], [cont_no_sch], bottom=[cont_sch], label="No Schengen", color="blue")
    plt.title("Schengen vs Non-Schengen Flights")
    plt.ylabel("Number of flights")
    plt.legend()
    plt.show()


def MapFlights(aircrafts, filename):
    T = open(filename, "w")

    T.write('<kml xmlns = "http://www.opengis.net/kml/2.2">\n')
    T.write("   <Document>\n")

    # Estilo para trayectorias Schengen (amarillo) y no Schengen (rojo)
    T.write('       <Style id="SchengenLine">\n')
    T.write('           <LineStyle>\n')
    T.write('               <color>ff00ffff</color>\n')
    T.write('           </LineStyle>\n')
    T.write('       </Style>\n')

    T.write('       <Style id="NoSchengenLine">\n')
    T.write('           <LineStyle>\n')
    T.write('               <color>ffff0000</color>\n')
    T.write('           </LineStyle>\n')
    T.write('       </Style>\n')

    # Coordenadas fijas de Barcelona El Prat (LEBL)
    lat_bcn = 41.297445
    lon_bcn = 2.0832941

    for avion in aircrafts:
        origen = avion.origin

        # Buscar el aeropuerto de origen en la lista global
        ap_origen = None
        for ap in airports:
            if ap.code == origen:
                ap_origen = ap
                break

        if ap_origen is None:
            continue

        if IsSchengenAirport(origen):
            style = '#SchengenLine'
        else:
            style = '#NoSchengenLine'

        T.write(f'       <Placemark>\n')
        T.write(f'           <name>{avion.id}</name>\n')
        T.write(f'           <styleUrl>{style}</styleUrl>\n')
        T.write(f'           <LineString>\n')
        T.write(f'               <coordinates>\n')
        T.write(f'                   {ap_origen.lon},{ap_origen.lat},0\n')
        T.write(f'                   {lon_bcn},{lat_bcn},0\n')
        T.write(f'               </coordinates>\n')
        T.write(f'           </LineString>\n')
        T.write(f'       </Placemark>\n')

    T.write("   </Document>\n")
    T.write("</kml>\n")
    T.close()


def LongDistanceArrivals(aircrafts):
    try:
        resultado = []

        lat_bcn = 41.297445
        lon_bcn = 2.0832941

        for a in aircrafts:
            origen = a.origin

            for ap in airports:
                if ap.code == origen:
                    distancia = Haversine(ap.lat, ap.lon, lat_bcn, lon_bcn)

                    # Solo incluir vuelos con origen a más de 2000 km
                    if distancia > 2000:
                        resultado.append(a)

                    break

        return resultado

    except FileNotFoundError:
        return []


def Haversine(lat1, lon1, lat2, lon2):
    # Fórmula de Haversine para calcular la distancia entre dos puntos en la Tierra
    R = 6371  # Radio de la Tierra en km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = (lat1 - lat2)
    dlon = (lon1 - lon2)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def LoadDepartures(filename):
    try:
        F = open(filename, "r")
        linea1 = F.readline()  # Saltar cabecera
        linea = F.readline()

        departures = []

        while linea != "":
            elementos = linea.split()

            if len(elementos) == 4:
                id = elementos[0]
                destination = elementos[1]
                time_departure = elementos[2]
                comp = elementos[3]

                avion = Aircraft(id, comp, "", "", destination, time_departure)
                departures.append(avion)

            linea = F.readline()

        F.close()
        return departures

    except FileNotFoundError:
        return []


def MergeMovements(arrivals, departures):
    if len(arrivals) == 0 or len(departures) == 0:
        return -1

    merged = []

    for arrival in arrivals:
        merged_with_departure = False

        for departure in departures:
            if arrival.id == departure.id:
                # Convertir tiempos a minutos totales para comparar
                arrival_hour = int(arrival.time_landing.split(":")[0])
                arrival_min = int(arrival.time_landing.split(":")[1])
                departure_hour = int(departure.time_departure.split(":")[0])
                departure_min = int(departure.time_departure.split(":")[1])

                arrival_total = arrival_hour * 60 + arrival_min
                departure_total = departure_hour * 60 + departure_min

                # Solo fusionar si llega antes de salir
                if arrival_total < departure_total:
                    avion = Aircraft(arrival.id, arrival.comp, arrival.origin,
                                     arrival.time_landing, departure.destination,
                                     departure.time_departure)
                    merged.append(avion)
                    merged_with_departure = True

        if not merged_with_departure:
            merged.append(arrival)

    # Añadir salidas que no tienen llegada correspondiente (aviones nocturnos)
    for departure in departures:
        tiene_llegada = False

        for arrival in arrivals:
            if departure.id == arrival.id:
                tiene_llegada = True
                break

        if not tiene_llegada:
            merged.append(departure)

    return merged


def NightAircraft(aircrafts):
    if len(aircrafts) == 0:
        return -1

    night_aircrafts = []

    # Un avión nocturno solo tiene datos de salida (sin llegada)
    for avion in aircrafts:
        if avion.origin == "" and avion.time_landing == "":
            night_aircrafts.append(avion)

    return night_aircrafts