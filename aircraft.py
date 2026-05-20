from airport import *
import matplotlib.pyplot as plt
import math
from tkinter import messagebox


class Aircraft:
  def __init__(self, id, comp, origin, time):
      self.id = id
      self.comp = comp
      self.origin = origin
      self.time = time

aircrafts = []


def LoadArrivals (filename):

  try:
      S = open(filename, "r")

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

  except FileNotFoundError:
      return []


def PlotArrivals (aircrafts):
    if len(aircrafts) == 0:
        messagebox.showerror("Error", "The aircraft list is empty.\nPlease load arrivals first.")
        return

    horas = [0]*24

    for avion in aircrafts:
        hora = int(avion.time.split(":")[0])
        horas[hora] = horas[hora] + 1

    plt.bar(range(24), horas)
    plt.xlabel("Hours")
    plt.ylabel("Number of arrivals")
    plt.show()


def SaveFlights (aircrafts, filename):

  if len(aircrafts) == 0:
      return -1

  R =open(filename, "w")
  R.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

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

    if len(aircrafts) == 0:
        messagebox.showerror("Error", "The aircraft list is empty.\nPlease load arrivals first.")
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


    plt.bar(comp, flights)
    plt.xlabel("Airline")
    plt.ylabel("Number of flights")
    plt.title("Flights per Airline")
    plt.xticks(rotation=45, ha="right", fontsize=5)
    plt.tight_layout()
    plt.show()



def PlotFlightsType (aircrafts):

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



def MapFlights (aircrafts):
  T = open("GoogleEarth.kml", "w")

  T.write('<kml xmlns = "http://www.opengis.net/kml/2.2">\n')
  T.write("   <Document>\n")

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


  lat_bcn = 41.297445
  lon_bcn = 2.0832941

  for avion in aircrafts:
      origen = avion.origin

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