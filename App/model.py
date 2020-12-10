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
            'name_travel': None,
            'name_taxi': None,
            'travel': None,
            'taxi': None,
            'date': None
        }

        # chicago['companies'] = om.newMap(omaptype='RBT',
        #                        comparefunction=compareroutes)
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
        chicago['name_travel'] = m.newMap(numelements=5500,
                                          maptype='PROBING',
                                          comparefunction=compareOffenses)
        # chicago['graph'] = gr.newGraph(datastructure='ADJ_LIST',
        #                              directed=True,
        #                             size=1000,
        #                            comparefunction=compareStopIds)
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
    # add_date_taxis(chicago, viaje, total_dinero, total_millas, date, taxi)
    add_companies_taxi(chicago, company, taxi)
    add_companies_viaje(chicago, company, viaje)


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
        m.put(chicago['name_travel'], viaje, 1)

    else:
        if m.contains(chicago['name_travel'], viaje) == False:
            m.put(chicago['name_travel'], viaje, 1)
            par_viaje = m.get(chicago['travel'], company)
            par_viaje['value'] += 1


def getDateTimeTaxiTrip(taxitrip):
    """
    Recibe la informacion de un servicio de taxi leido del archivo de datos (parametro).
    Retorna de forma separada la fecha (date) y el tiempo (time) del dato 'trip_start_timestamp'
    Los datos date se pueden comparar con <, >, <=, >=, ==, !=
    Los datos time se pueden comparar con <, >, <=, >=, ==, !=
    """
    tripstartdate = taxitrip['trip_start_timestamp']
    taxitripdatetime = datetime.datetime.strptime(
        tripstartdate, '%Y-%m-%dT%H:%M:%S.%f')
    return taxitripdatetime.date(), taxitripdatetime.time()
# ==============================
# Funciones de consulta
# ==============================


def primer_requerimiento(chicago, number_taxis, number_viajes):
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

    # WHILE PARA TAXIS
    number_tax = abs(mi.size(cola_prioridad_taxis)-int(number_taxis))
    i = 1
    while i <= number_tax:
        mi.delMin(cola_prioridad_taxis)
        i += 1
    respuesta_taxi = auxiliar_requerimiento_uno_taxis(
        cola_prioridad_taxis, number_taxis, tax)

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
    return resultado


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
