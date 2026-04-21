import matplotlib.pyplot as plt

class Airport:
    def __init__(self, code, lat, lon):
        self.code = code
        self.lat = lat
        self.lon = lon
        self.schengen = IsSchengenAirport(code)

def IsSchengenAirport (code):
    if len(code) != 4:
        return False

    first_character = code[0]
    second_character = code[1]
    prefix = first_character + second_character

    schengen_prefixes = ["LO", "EB", "LK", "LC", "EK", "EE", "EF", "LF", "ED", "LG", "EH", "LH", "BI", "LI", "EV", "EY", "EL", "LM", "EN", "EP", "LP", "LZ", "LJ", "LE", "ES", "LS"]

    encontrado = False
    i = 0
    while i < len(schengen_prefixes) and not encontrado:

        if prefix == schengen_prefixes[i]:
            encontrado = True

        else:
            i = i + 1

    if encontrado:
        return True
    else:
        return False

def SetSchengen (airport):
    airport.schengen = IsSchengenAirport(airport.code)

def PrintAirport (airport):
    print("Airport Code: ", airport.code)
    print("Latitude: ", airport.lat)
    print("Longitude: ", airport.lon)
    print("Schengen: ", airport.schengen)

def LoadAirports (Airports):

    F = open("Airports", "r")
    D = open("Airports2", "w")
    linea1 = F.readline()
    linea = F.readline()

    while linea != "":
        elementos = linea.split("\t")
        code = elementos[0]
        lat = elementos[1]
        lon = elementos[2]

        grados = int(lat[1:3])
        minutos = int(lat[3:5])
        segundos = int(lat[5:7])

        lat_decimal = grados + minutos/60 + segundos/3600

        if lat[0] == "S":
            lat_decimal = -lat_decimal

        grados = int(lon[1:3])
        minutos = int(lon[3:5])
        segundos = int(lon[5:7])

        lon_decimal = grados + minutos / 60 + segundos / 3600

        if lon[0] == "W":
            lon_decimal = -lon_decimal

        a = Airport(code, lat_decimal, lon_decimal)
        D.write(a)
        linea = F.readline()

    F.close()
    D.close()
    return airports

def SaveSchengenAirports (airports, Airports):

    F = open("Airports", "r")
    linea1 = F.readline()
    linea = F.readline()

    H = open("SchengenAirports", "w")
    H.write("CODE" + "LAT" + "LON" + "\n")

    while linea != "":
        elementos = linea.split("\t")
        code = elementos[0]
        lat = elementos[1]
        lon = elementos[2]

    if IsSchengenAirport (code) == True:
        H.write(code + lat + lon + "\n")

    F.close()
    H.close()

    return H

def AddAirport (airports, airport):

    F = open("Airports", "r")
    linea1 = F.readline()
    linea = F.readline()
    encontrado = False
    i = 0

    while i < len(airports) and not encontrado:
        elementos = linea.split("\t")
        code = elementos[0]
        lat = elementos[1]
        lon = elementos[2]

        if airport.code == code:
            encontrado = True

        i = i + 1

        linea = F.readline()


    if not encontrado:
        F = open("Airports", "a")
        F.write(code + lat + lon)

    F.close()
    return F

def RemoveAirport (airports, code):

    F = open("Airports", "r")
    linea1 = F.readline()
    linea = F.readline()
    encontrado = False

    while linea != "" and not encontrado:
        elementos = linea.split("\t")
        code = elementos[0]
        lat = elementos[1]
        lon = elementos[2]

        if airport.code == code:
            encontrado = True

        linea = F.readline()

    if not encontrado:
        print("Introduce un aeropuerto válido")

    F.close()
    return

def PlotAirports(airports):

    schengen = 0
    no_schengen = 0

    i = 0
    while i < len(airports):

        if airports[i].schengen == True:
            schengen = schengen + 1
        else:
            no_schengen = no_schengen + 1

        i = i + 1

    etiquetas = ["Schengen", "No Schengen"]
    valores = [schengen, no_schengen]

    plt.bar(etiquetas, valores)
    plt.title("Airports")
    plt.show()

def MapAirports (airports):
    T = open("GoogleEarth.kml", "w")
    D = open("Airports2","r")
    linea1 = D.readline()
    linea = D.readline()

    T.write('<kml xmlns = "http://www.opengis.net/kml/2.2">\n')
    T.write("   <Document>\n")

    T.write('       <Style id="SchengenPoint">\n')
    T.write('           <IconStyle>\n')
    T.write('               <color>ff00ffff</color>\n')
    T.write('           </IconStyle>\n')
    T.write('       </Style>\n')

    T.write('       <Style id="NoSchengenPoint">\n')
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

        if IsSchengenAirport (code) == True:
            style = '#SchengenPoint'
        else:
            style = '#NoSchengenPoint'

        T.write("       <Placemark> <name>", code, "</name>\n")
        T.write('           <styleUrl>', style, '</styleUrl>\n')
        T.write("           <Point>\n")
        T.write("               <coordinates>\n")
        T.write('                   ', lat,lon, '\n')
        T.write("               </coordinates>\n")
        T.write("           </Point>\n")
        T.write("       </Placemark>\n")
        T.write("   </Document>\n")
        T.write("</kml>\n")

        i = i + 1
        linea = D.readline()

    T.close()
    D.close()