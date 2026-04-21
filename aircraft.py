import matplotlib.pyplot as plt
import math

class Aircraft:
    def __init__(self, id, comp, origin, time):
        self.id = id
        self.comp = comp
        self.origin = origin
        self.time = time

def LoadArrivals (Arrivals):
    aircrafts = []

    try:
        S = open("Arrivals", "r")

    except FileNotFoundError:
        return []

    linea1 = S.readline()
    linea = S.readline()

    while linea != "":
        elementos = linea.split()

        if len(elementos) == 4:
            id = elementos[0]
            origin = elementos[1]
            time = elementos[2]
            comp = elementos[3]

            avion = Aircraft(id, comp, origin, time)

            aircrafts.append(avion)

        linea = S.readline()

    S.close()
    return aircrafts

def PlotArrivals (aircrafts):
    try:
        hora = time.split(":")[0]
        horas = [0]*24

        for avion in aircrafts:
            hora = int(avion[2].split(":")[0])
            horas[hora] = horas[hora] + 1

        plt.bar(range(24), horas)
        plt.xlabel("Hours")
        plt.ylabel("Number of arrivals")
        plt.show()

    except FileNotFoundError:
        return []

def SaveFlights (aircrafts, Aircrafts):
    R =open("Aircrafts", "w")
    R.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

    if len(aircrafts) == 0:
        print ("The aircraft list is empty")
        return

    for avion in aircrafts:
        id_final = avion.id
        if id_final == "":
            id_final = "-"

        origen_final = avion.origin
        if origen_final == "":
            origen_final = "-"

        tiempo_final = avion.time
        if tiempo_final == "":
            tiempo_final = "0"

        comp_final = avion.comp
        if comp_final == "":
            comp_final = "-"

        linea = id_final + " " + origen_final + " " + tiempo_final + " " + comp_final + "\n"
        R.write(linea)

    R.close()

def PlotAirlines (aircrafts):
    try:
        flights = []
        comp = []
        P = open("Arrivals", "r")
        linea1 = P.readline()
        linea = P.readline()

        while linea != "":
            trozos = linea.split(" ")
            aerolinea = trozos[3]

            if aerolinea not in comp:
                comp.append(aerolinea)
                flights.append(1)

            else:
                i = comp.index(aerolinea)
                flights[i] = flights[i] + 1

            linea = P.readline()

        plt.bar(comp,flights)
        plt.show()

        P.close()

    except FileNotFoundError:
        return []

def PlotFlightsType (aircrafts):
    try:
        sch = []
        etiquetas = ["Schengen", "No Schengen"]
        cont_sch = 0
        cont_no_sch = 0
        if IsSchengenAirport(code) == True:
            cont_sch = cont_sch + 1

        else:
            cont_no_sch = cont_no_sch + 1

        sch [0] = cont_sch
        sch[1] = cont_no_sch

        plt.bar(sch, etiquetas)
        plt.show()

    except FileNotFoundError:
        return []

def MapFlights (aircrafts):
    T = open("GoogleEarth.kml", "w")
    D = open("Airports2", "r")
    linea1 = D.readline()
    linea = D.readline()

    T.write('<kml xmlns = "http://www.opengis.net/kml/2.2">\n')
    T.write("   <Document>\n")

    T.write('       <Style id="SchengenLine">\n')
    T.write('           <IconStyle>\n')
    T.write('               <color>ff00ffff</color>\n')
    T.write('           </IconStyle>\n')
    T.write('       </Style>\n')

    T.write('       <Style id="NoSchengenLine">\n')
    T.write('           <IconStyle>\n')
    T.write('               <color>ffff0000</color>\n')
    T.write('           </IconStyle>\n')
    T.write('       </Style>\n')

    i = 0
    while i < len(airports):
        elementos = linea.split("\t")
        code = elementos[0]
        lat = elementos[1]
        lon = elementos[2]

        if IsSchengenAirport(code) == True:
            style = '#SchengenLine'
        else:
            style = '#NoSchengenLine'

        T.write("       <Placemark> <name>", code, "</name>\n")
        T.write('           <styleUrl>', style, '</styleUrl>\n')
        T.write("           <LineString>\n")
        T.write("               <coordinates>\n")
        T.write('                   ', 2.0785, 41.2971, '\n')
        T.write('                      ', lat, lon, '\n')
        T.write("               </coordinates>\n")
        T.write("           </LineString>\n")
        T.write("       </Placemark>\n")
        T.write("   </Document>\n")
        T.write("</kml>\n")

        i = i + 1
        linea = D.readline()

    T.close()
    D.close()

def LongDistanceArrivals (aircrafts):
    try:
        resultado = []

        lat_bcn = 41.297445
        lon_bcn = 2.0832941

        for a in aircrafts:
            origen = a.origin

            for ap in airports:
                if ap.code == origen:
                    distancia = Haversine(ap.lat, ap.lon, lat_bcn, lon_bcn)

                    if distancia > 2000:
                        resultado.append(a)

                    break

        return resultado

    except FileNotFoundError:
        return []

def Haversine(lat1, lon1, lat2, lon2):
    R = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = (lat1 - lat2)
    dlon = (lon1 - lon2)

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c