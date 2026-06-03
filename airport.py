import matplotlib.pyplot as plt


# Clase que representa un aeropuerto con su código ICAO, posición y si es Schengen
class airport:
    def __init__(self, code, lat, lon):
        self.code = code
        self.lat = lat
        self.lon = lon
        self.schengen = IsSchengenAirport(code)


airports = []


def IsSchengenAirport(code):
    # El código ICAO debe tener exactamente 4 caracteres
    if len(code) != 4:
        return False

    first_character = code[0]
    second_character = code[1]
    prefix = first_character + second_character

    # Lista de prefijos de países del espacio Schengen
    schengen_prefixes = ["LO", "EB", "LK", "LC", "EK", "EE", "EF", "LF", "ED", "LG", "EH", "LH", "BI", "LI", "EV", "EY",
                         "EL", "LM", "EN", "EP", "LP", "LZ", "LJ", "LE", "ES", "LS"]

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


def SetSchengen(a):
    a.schengen = IsSchengenAirport(a.code)


def PrintAirport(airport):
    print("Airport Code: ", airport.code)
    print("Latitude: ", airport.lat)
    print("Longitude: ", airport.lon)
    print("Schengen: ", airport.schengen)


def LoadAirports(filename):
    try:
        F = open(filename, "r")
        linea1 = F.readline()  # Saltar la cabecera
        linea = F.readline()

        while linea != "":
            try:
                elementos = linea.split(" ")
                if len(elementos) < 3:
                    linea = F.readline()
                    continue

                code = elementos[0]
                lat = elementos[1]
                lon = elementos[2].strip()

                if len(code) != 4 or len(lat) < 7 or len(lon) < 7:
                    linea = F.readline()
                    continue

                # Convertir latitud de formato ICAO (GDMMSS) a grados decimales
                grados = int(lat[1:3])
                minutos = int(lat[3:5])
                segundos = int(lat[5:7])
                lat_decimal = grados + minutos / 60 + segundos / 3600
                if lat[0] == "S":
                    lat_decimal = -lat_decimal

                # Convertir longitud de formato ICAO (GDDDMMSS) a grados decimales
                grados = int(lon[1:4])
                minutos = int(lon[4:6])
                segundos = int(lon[6:8])
                lon_decimal = grados + minutos / 60 + segundos / 3600
                if lon[0] == "W":
                    lon_decimal = -lon_decimal

                a = airport(code, lat_decimal, lon_decimal)
                airports.append(a)

            except (ValueError, IndexError):
                pass  # Línea con formato incorrecto, se ignora

            linea = F.readline()

        F.close()
        return airports

    except FileNotFoundError:
        return []


def DecimalToICAO(degrees, is_lat):
    # Determinar dirección según el signo y si es latitud o longitud
    if is_lat:
        direction = "N" if degrees >= 0 else "S"
    else:
        direction = "E" if degrees >= 0 else "W"

    degrees = abs(degrees)
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int(round(((degrees - d) * 60 - m) * 60))

    # Ajustar desbordamientos de segundos y minutos
    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        d += 1

    if is_lat:
        return f"{direction}{d:02d}{m:02d}{s:02d}"
    else:
        return f"{direction}{d:03d}{m:02d}{s:02d}"


def SaveSchengenAirports(airports, filename):
    if len(airports) == 0:
        return -1

    schengen_airports = [a for a in airports if a.schengen]

    if len(schengen_airports) == 0:
        return -1

    H = open(filename, "w")
    H.write("CODE LAT LON\n")

    for a in schengen_airports:
        lat_str = DecimalToICAO(a.lat, is_lat=True)
        lon_str = DecimalToICAO(a.lon, is_lat=False)
        H.write(f"{a.code} {lat_str} {lon_str}\n")

    H.close()


def AddAirport(airports, airport):
    # Solo añadir si el código no existe ya en la lista
    encontrado = False
    i = 0

    while i < len(airports) and not encontrado:
        a = airports[i]
        if airport.code == a.code:
            encontrado = True
        i = i + 1

    if not encontrado:
        airports.append(airport)

    return airports


def RemoveAirport(airports, code):
    i = 0
    encontrado = False

    while i < len(airports) and not encontrado:
        ai = airports[i]
        if ai.code == code:
            encontrado = True
        i = i + 1

    if encontrado:
        # Desplazar elementos a la izquierda para eliminar el aeropuerto
        i = i - 1
        while i < len(airports) - 1:
            airports[i] = airports[i + 1]
            i = i + 1
        airports.pop()

    if not encontrado:
        return -1

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

    # Gráfico de barras apiladas: Schengen abajo, no Schengen encima
    plt.bar(["Airports"], [schengen], label="Schengen", color="yellow")
    plt.bar(["Airports"], [no_schengen], bottom=[schengen], label="No Schengen", color="blue")
    plt.title("Schengen Airports")
    plt.legend()
    plt.show()


def MapAirports(airports):
    T = open("GoogleEarth_Airports.kml", "w")

    # Cabecera del fichero KML
    T.write('<kml xmlns = "http://www.opengis.net/kml/2.2">\n')
    T.write("   <Document>\n")

    # Estilo para aeropuertos Schengen (amarillo)
    T.write('       <Style id="SchengenPoint">\n')
    T.write('           <IconStyle>\n')
    T.write('               <color>ff00ffff</color>\n')
    T.write('               <Icon>\n')
    T.write('                   <href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href>\n')
    T.write('               </Icon>\n')
    T.write('           </IconStyle>\n')
    T.write('       </Style>\n')

    # Estilo para aeropuertos no Schengen (azul)
    T.write('       <Style id="NoSchengenPoint">\n')
    T.write('           <IconStyle>\n')
    T.write('               <color>ffff0000</color>\n')
    T.write('               <Icon>\n')
    T.write('                   <href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href>\n')
    T.write('               </Icon>\n')
    T.write('           </IconStyle>\n')
    T.write('       </Style>\n')

    i = 0
    while i < len(airports):
        ai = airports[i]
        code = ai.code
        lat = ai.lat
        lon = ai.lon

        if IsSchengenAirport(code) == True:
            style = '#SchengenPoint'
        else:
            style = '#NoSchengenPoint'

        T.write(f"       <Placemark> <name> {code} </name>\n")
        T.write(f'           <styleUrl> {style} </styleUrl>\n')
        T.write("           <Point>\n")
        T.write("               <coordinates>\n")
        T.write(f'                    {lon},{lat}, 0\n')
        T.write("               </coordinates>\n")
        T.write("           </Point>\n")
        T.write("       </Placemark>\n")

        i = i + 1

    T.write("   </Document>\n")
    T.write("</kml>\n")
    T.close()