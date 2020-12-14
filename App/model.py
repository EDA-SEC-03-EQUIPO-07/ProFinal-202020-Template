"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """

import config
from DISClib.ADT.graph import gr
from DISClib.Algorithms.Graphs import dfs as d
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import orderedmap as om
from DISClib.ADT import minpq as mi
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
import datetime
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------


def newAnalyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        chicago = {
            # 'name_travel': None,
            'name_taxi': None,
            'travel': None,
            'taxi': None,
            'date': None,
            'map_graph': None
        }

        chicago['date'] = om.newMap(omaptype='RBT',
                                    comparefunction=compareroutes)
        chicago['travel'] = m.newMap(numelements=100,
                                     maptype='PROBING',
                                     comparefunction=compareOffenses)
        chicago['taxi'] = m.newMap(numelements=100,
                                   maptype='PROBING',
                                   comparefunction=compareOffenses)
        chicago['name_taxi'] = m.newMap(numelements=5000,
                                        maptype='PROBING',
                                        comparefunction=compareOffenses)
        chicago['map_graph'] = m.newMap(numelements=200,
                                        maptype='CHAINING',
                                        comparefunction=compareStopIds)
        return chicago
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')


# Funciones para agregar informacion al grafo
def addTrip(chicago, trip):
    company = trip["company"]
    viaje = trip["trip_id"]
    taxi = trip["taxi_id"]
    total_dinero = trip["trip_total"]
    total_millas = trip["trip_miles"]
    date = trip["trip_start_timestamp"]
    add_date_taxis(chicago, total_dinero, total_millas, date, taxi, trip)
    add_companies_taxi(chicago, company, taxi)
    add_companies_viaje(chicago, company, viaje)

    start_community_area = trip["pickup_community_area"]
    end_community_area = trip["dropoff_community_area"]
    if start_community_area != end_community_area:
        seconds = trip["trip_seconds"]
        start_trip_hour = trip["trip_start_timestamp"]
        add_graph_trip(chicago, start_community_area, end_community_area, seconds, start_trip_hour)


def add_date_taxis(chicago, total_dinero, total_millas, date, taxi, trip):
    """
    Para calcular los puntos asignados a un taxi se calcula una función alfa diaria; 
    esta función se define como la división del total de millas recorridas entre el 
    total de dinero recibido, esto multiplicado por el total de servicios prestados
    """

    time = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
    present_date = om.contains(chicago['date'], time.date())
    if present_date == False:
        llave_valor = add_date(taxi, total_dinero, total_millas, trip)
        om.put(chicago['date'], time.date(), llave_valor)

    else:
        date_taxi = om.get(chicago['date'], time.date())
        ma_taxi = me.getValue(date_taxi)
        if m.contains(ma_taxi, taxi) == False:
            if ((total_dinero != '0.0') and (total_dinero != '')):
                if ((total_millas != '0.0') and (total_millas != '')):
                    helped = auxi(trip)
                    m.put(ma_taxi, taxi, helped)
                    om.put(chicago['date'], time.date(), ma_taxi)
        else:
            if ((total_dinero != '0.0') and (total_dinero != '')):
                if ((total_millas != '0.0') and (total_millas != '')):
                    obtener_taxi = m.get(ma_taxi, taxi)
                    get_value = me.getValue(obtener_taxi)
                    dicc = {'trip_total': trip["trip_total"],
                            'trip_miles': trip["trip_miles"]}
                    lt.addLast(get_value,  dicc)
                    m.put(ma_taxi, taxi, get_value)


def add_date(taxi, total_dinero, total_millas, trip):
    if ((total_dinero != '0.0') and (total_dinero != '')):
        if ((total_millas != '0.0') and (total_millas != '')):
            map_date = m.newMap(numelements=200, maptype='PROBING',
                                comparefunction=compareOffenses)
            res = auxi(trip)
            m.put(map_date, taxi, res)
    return map_date


def auxi(trip):
    dicc = {'trip_total': trip["trip_total"], 'trip_miles': trip["trip_miles"]}
    new_list = lt.newList('SINGLE_LINKED', compareroutes)

    lt.addLast(new_list, dicc)
    return new_list


def add_companies_taxi(chicago, company, taxi):
    if company == "":
        auxiliar(chicago, company, taxi)
    else:
        present_company = m.contains(chicago['taxi'], company)
        if present_company == False:
            m.put(chicago['taxi'], company, 1)
            m.put(chicago['name_taxi'], taxi, 1)
        else:
            if m.contains(chicago['name_taxi'], taxi) == False:
                m.put(chicago['name_taxi'], taxi, 1)
                par_company = m.get(chicago['taxi'], company)
                par_company['value'] += 1


def auxiliar(chicago, company, taxi):
    company = "Independent Owner"
    present_company = m.contains(chicago['taxi'], company)
    if present_company == False:
        m.put(chicago['taxi'], company, 1)
        m.put(chicago['name_taxi'], taxi, 1)

    else:
        if m.contains(chicago['name_taxi'], taxi) == False:
            m.put(chicago['name_taxi'], taxi, 1)
            par_company = m.get(chicago['taxi'], company)
            par_company['value'] += 1


def add_companies_viaje(chicago, company, viaje):
    present_company = m.contains(chicago['travel'], company)
    if present_company == False:
        m.put(chicago['travel'], company, 1)

    else:
        par_viaje = m.get(chicago['travel'], company)
        par_viaje['value'] += 1


def add_graph_trip(chicago, startstation, endstation, totaltime, datetime):
    start_trip_time = get_hour(datetime)
    present_community_area_map = m.contains(chicago['map_graph'], start_trip_time)

    if present_community_area_map:
        community_area_graph = m.get(chicago['map_graph'], start_trip_time)["value"]

    else:
        community_area_graph = gr.newGraph(datastructure='ADJ_LIST',
                                            directed=True,
                                            size=400,
                                            comparefunction=compareStopIds)

    addStation(community_area_graph, startstation)
    addStation(community_area_graph, endstation)
    addConnection(community_area_graph, startstation, endstation, totaltime)

    m.put(chicago['map_graph'],start_trip_time,community_area_graph)


def addConnection(chicago, origin, destination, duration):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(chicago, origin, destination)
    if edge is None:
        if duration != '':
            time_duration = float(duration)
        else:
            time_duration = 0.0
        gr.addEdge(chicago, origin, destination, time_duration)
    else:
        peso = edge['weight']
        if duration != '':
            edge['weight'] = (peso+float(duration))/2
        else:
            edge['weight'] = float(peso)
    return chicago


def addStation(chicago, stationid):
    if not gr.containsVertex(chicago, stationid):
        gr.insertVertex(chicago, stationid)
    return chicago


def get_hour(datetime):
    date, time = getDateTimeTaxiTrip(datetime)

    minute = str(time.minute)

    if int(minute) == 0:
        minute = "0"+minute

    hour = str(time.hour)

    if int(hour) < 10:
        hour = "0"+hour

    franja_horaria = hour+":"+minute

    return franja_horaria
# ==============================
# Funciones de consulta
# ==============================


def segundo_requerimiento_primera_consulta(chicago, number_taxis, initialDate):
    present_date = om.contains(chicago['date'], initialDate)
    if present_date == True:
        resultado = {}
        # MAP PARA LOS TAXIS
        tax = m.newMap(numelements=30, maptype='PROBING',
                       comparefunction=compareOffenses)
        cola_prioridad_taxis = mi.newMinPQ(compareroutes)
        date_value = om.get(chicago['date'], initialDate)
        list_value = m.keySet(date_value['value'])
        iterador = it.newIterator(list_value)
        while it.hasNext(iterador):
            name_taxi = it.next(iterador)
            pareja_taxi = m.get(date_value['value'], name_taxi)
            # FUNCION QUE DA LOS PUNTOS DE UN TAXI
            puntaje = funcion_auxiliar(pareja_taxi['value'])
            m.put(tax, puntaje, name_taxi)
            mi.insert(cola_prioridad_taxis, puntaje)
        # WHILE PARA TAXIS
        ayuda = comun(cola_prioridad_taxis, number_taxis)
        ranking = auxiliar_requerimiento_uno_taxis(
            ayuda, number_taxis, tax)
        resultado["Taxis con más puntos"] = ranking
        answer = resultado
    else:
        answer = "La llave no está almacenada."
    return answer


def segundo_requerimiento_segunda_consulta(chicago, number_taxis, initialDate,  finalDate):
    present_date = om.contains(chicago['date'], initialDate)
    present_final = om.contains(chicago['date'], finalDate)
    if (present_date == True) and (present_final == True):
        resultado = {}
        # MAP PARA LOS TAXIS
        date_total = m.newMap(numelements=1000, maptype='PROBING',
                              comparefunction=compareOffenses)
        date_key = om.keys(chicago['date'], initialDate, finalDate)
        iterador = it.newIterator(date_key)
        while it.hasNext(iterador):
            name_date = it.next(iterador)
            pareja_taxi = om.get(chicago['date'], name_date)
            total_viajes = m.keySet(pareja_taxi['value'])
            ite = it.newIterator(total_viajes)
            while it.hasNext(ite):
                name_taxi = it.next(ite)
                par_taxi = m.get(pareja_taxi['value'], name_taxi)
                # FUNCION QUE DA LOS PUNTOS DE UN TAXI
                puntuacion = funcion_auxiliar(par_taxi['value'])
                if (m.contains(date_total, name_taxi) == False):
                    m.put(date_total, name_taxi, puntuacion)
                else:
                    coinciden = m.get(date_total, name_taxi)
                    coinciden['value'] += puntuacion
        mapa_auxiliar = otra_auxiliar(date_total, number_taxis)
        resultado["Taxis con más puntos"] = mapa_auxiliar
        answer = resultado
    else:
        answer = "La(s) llave(s) no está(n) almacenada(s)."
    return answer


def funcion_auxiliar(lista):
    total_viajes = lt.size(lista)
    suma_pago = 0.0
    suma_millas = 0.0
    i = 1
    while i <= total_viajes:
        primero = lt.getElement(lista, i)
        suma_pago += float(primero['trip_total'])
        suma_millas += float((primero['trip_miles']))
        i += 1
    puntos = ((suma_millas/suma_pago)*total_viajes)
    return puntos


def otra_auxiliar(mapa, number_taxis):
    new_mapa = m.newMap(numelements=100, maptype='PROBING',
                        comparefunction=compareOffenses)
    cola_prioridad_taxis = mi.newMinPQ(compareroutes)
    list_taxi = m.keySet(mapa)
    ite = it.newIterator(list_taxi)
    while it.hasNext(ite):
        name_taxi = it.next(ite)
        par_taxi = m.get(mapa, name_taxi)
        m.put(new_mapa, par_taxi['value'], name_taxi)
        mi.insert(cola_prioridad_taxis, par_taxi['value'])
    restantes = comun(cola_prioridad_taxis, number_taxis)
    ranking = auxiliar_requerimiento_uno_taxis(
        restantes, number_taxis, new_mapa)
    return ranking


def primer_requerimiento(chicago, number_taxis, number_viajes):
    if (int(number_taxis) > m.size(chicago['travel'])) or (int(number_viajes) > m.size(chicago['travel'])):
        answer = "Uno o los dos números excede el total de compañias disponbles. Ingrese un número menor o igual a: " + \
            str(m.size(chicago['travel']))
    else:
        resultado = {}
        # MAP PARA LOS VIAJES
        tra = m.newMap(numelements=30, maptype='PROBING',
                       comparefunction=compareOffenses)
        cola_prioridad_viajes = mi.newMinPQ(compareroutes)
        # MAP PARA LOS TAXIS
        tax = m.newMap(numelements=30, maptype='PROBING',
                       comparefunction=compareOffenses)
        cola_prioridad_taxis = mi.newMinPQ(compareroutes)
        total_taxis = m.size(chicago['name_taxi'])
        total_companies = m.size(chicago['travel'])
        # LISTA DE LLAVES DE EMPRESAS PARA LOS TAXIS
        list_taxis = m.keySet(chicago['taxi'])
        iterador_taxis = it.newIterator(list_taxis)
        # LISTA DE LLAVES DE EMPRESAS PARA LOS VIAJES
        list_viajes = m.keySet(chicago['travel'])
        iterador_viajes = it.newIterator(list_viajes)
        while it.hasNext(iterador_taxis) and it.hasNext(iterador_viajes):
            empresa_taxi = it.next(iterador_taxis)
            empresa_viaje = it.next(iterador_viajes)
            # PARTE DE TAXIS
            pareja_taxi = m.get(chicago['taxi'], empresa_taxi)
            mi.insert(cola_prioridad_taxis, pareja_taxi['value'])
            m.put(tax, pareja_taxi['value'], empresa_taxi)
            # PARTE DE VIAJES
            pareja_viaje = m.get(chicago['travel'], empresa_viaje)
            mi.insert(cola_prioridad_viajes, pareja_viaje['value'])
            m.put(tra, pareja_viaje['value'], empresa_viaje)

        ayuda = comun(cola_prioridad_taxis, number_taxis)
        respuesta_taxi = auxiliar_requerimiento_uno_taxis(
            ayuda, number_taxis, tax)

        # WHILE PARA VIAJES
        number_tra = abs(mi.size(cola_prioridad_viajes)-int(number_viajes))
        iterar = 1
        while iterar <= number_tra:
            mi.delMin(cola_prioridad_viajes)
            iterar += 1
        respuesta_viajes = auxiliar_requerimiento_uno_viajes(
            cola_prioridad_viajes, number_viajes, tra)
        resultado['Número de taxis'] = total_taxis
        resultado['Número de compañias'] = total_companies
        resultado['Compañias con más taxis'] = respuesta_taxi
        resultado['Compañias con más servicios'] = respuesta_viajes
        answer = resultado
    return answer


def comun(cola_prioridad_taxis, number_taxis):
    number_tax = abs(mi.size(cola_prioridad_taxis)-int(number_taxis))
    i = 1
    while i <= number_tax:
        mi.delMin(cola_prioridad_taxis)
        i += 1
    return cola_prioridad_taxis


def auxiliar_requerimiento_uno_taxis(cola, number_taxis, tax):
    res = []
    ite = 1
    while ite <= int(number_taxis):
        menor = mi.delMin(cola)
        par = m.get(tax, menor)
        llave = me.getValue(par)
        res.append((llave, menor))
        ite += 1
    res.reverse()
    return res


def auxiliar_requerimiento_uno_viajes(cola, number_viajes, tra):
    re = []
    te = 1
    while te <= int(number_viajes):
        meno = mi.delMin(cola)
        pa = m.get(tra, meno)
        llav = me.getValue(pa)
        re.append((llav, meno))
        te += 1
    re.reverse()
    return re


def tercer_requerimiento(chicago, initialArea, finalArea, initialHour, finalHour):
    start_hour = initialHour
    rutas = None
    tiempo = 86400
    best_hour = ""

    while start_hour <= finalHour:
        if m.contains(chicago["map_graph"], str(start_hour)):
            map_graph = m.get(chicago["map_graph"], str(start_hour))["value"]
            if gr.containsVertex(map_graph,initialArea):
                dijk_graph = djk.Dijkstra(map_graph, initialArea)
                t = djk.distTo(dijk_graph, finalArea)

                if t < tiempo:
                    rutas = djk.pathTo(dijk_graph, finalArea)
                    tiempo = t
                    best_hour = start_hour
        
        start_hour = get_next_hour(start_hour)


    return best_hour, rutas, tiempo


def get_next_hour(datetime):
    hour = datetime.split(":")[0]
    minute = datetime.split(":")[1]

    if minute == "00":
        minute = "15"
    elif minute == "15":
        minute = "30"
    elif minute == "30":
        minute = "45"
    elif minute == "45":
        if int(hour)+1 < 10:
            hour = "0"+str(int(hour)+1)
        else:
            hour = str(int(hour)+1)
        minute = "00"


    next_hour = hour+":"+minute
    return next_hour


# ==============================
# Funciones Helper
# ==============================


def numSCC_2(graph):
    return scc.KosarajuSCC(graph)


def numSCC(graph):
    sc = scc.KosarajuSCC(graph)
    return scc.connectedComponents(sc)


def sameCC(sc, station1, station2):
    return scc.stronglyConnected(sc, station1, station2)


def getDateTimeTaxiTrip(taxitrip):

    """

    Recibe la informacion de un servicio de taxi leido del archivo de datos (parametro).

    Retorna de forma separada la fecha (date) y el tiempo (time) del dato 'trip_start_timestamp'

    Los datos date se pueden comparar con <, >, <=, >=, ==, !=

    Los datos time se pueden comparar con <, >, <=, >=, ==, !=

    """

    tripstartdate = taxitrip

    taxitripdatetime = datetime.datetime.strptime(tripstartdate, '%Y-%m-%dT%H:%M:%S.%f')

    return taxitripdatetime.date(), taxitripdatetime.time()

    
# ==============================
# Funciones de Comparacion
# ==============================

def compareStopIds(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1


def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1


def compareOffenses(offense1, offense2):
    """
    Compara dos ids de libros, id es un identificador
    y entry una pareja llave-valor
    """
    offense = me.getKey(offense2)
    if (offense1 == offense):
        return 0
    elif (offense1 > offense):
        return 1
    else:
        return -1
