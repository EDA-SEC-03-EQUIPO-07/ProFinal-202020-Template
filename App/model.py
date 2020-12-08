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
            'companies': None,
            'name_taxi': None,
            'travel': None,
            'taxi': None,
            'date': None
        }

        # chicago['companies'] = om.newMap(omaptype='RBT',
        #                        comparefunction=compareroutes)
        # chicago['companies_2'] = om.newMap(omaptype='RBT',
        #                          comparefunction=compareroutes)
        chicago['travel'] = m.newMap(numelements=100,
                                     maptype='PROBING',
                                     comparefunction=compareOffenses)
        chicago['taxi'] = m.newMap(numelements=100,
                                   maptype='PROBING',
                                   comparefunction=compareOffenses)
        #chicago['name_taxi'] = lt.newList('ARRAY_LIST', compareroutes)
        #chicago['date'] = lt.newList('ARRAY_LIST', compareroutes)
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
    total_dinero = trip["fare"]
    total_millas = trip["trip_miles"]
    add_companies_taxi(chicago, company, taxi)
    add_companies_viaje(chicago, company, viaje)


def add_companies_taxi(chicago, company, taxi):
    if company == "":
        auxiliar(chicago, company, taxi)
    else:
        present_taxi = m.contains(chicago['taxi'], company)
        if present_taxi == False:
            answer_taxi = add_taxi(taxi)
            m.put(chicago['taxi'], company, answer_taxi)

        else:
            par_taxi = m.get(chicago['taxi'], company)
            value_taxi = me.getValue(par_taxi)
            if m.contains(value_taxi, taxi) == False:
                m.put(value_taxi, taxi, 1)
                m.put(chicago['taxi'], company, value_taxi)


def add_taxi(taxi):
    map_taxi = m.newMap(numelements=200, maptype='PROBING',
                        comparefunction=compareOffenses)
    m.put(map_taxi, taxi, 1)
    return map_taxi


def auxiliar(chicago, company, taxi):
    company = "Independent Owner"
    present_taxi = m.contains(chicago['taxi'], company)
    if present_taxi == False:
        answer_taxi = add_taxi(taxi)
        m.put(chicago['taxi'], company, answer_taxi)

    else:
        par_taxi = m.get(chicago['taxi'], company)
        value_taxi = me.getValue(par_taxi)
        if m.contains(value_taxi, taxi) == False:
            m.put(value_taxi, taxi, 1)
            m.put(chicago['taxi'], company, value_taxi)


def add_companies_viaje(chicago, company, viaje):
    present_viaje = m.contains(chicago['travel'], company)
    if present_viaje == False:
        answer_viaje = add_viaje(viaje)
        m.put(chicago['travel'], company, answer_viaje)

    else:
        par_viaje = m.get(chicago['travel'], company)
        value_viaje = me.getValue(par_viaje)
        if m.contains(value_viaje, viaje) == False:
            m.put(value_viaje, viaje, 1)
            m.put(chicago['travel'], company, value_viaje)


def add_viaje(viaje):
    map_travel = m.newMap(numelements=200, maptype='PROBING',
                          comparefunction=compareOffenses)
    m.put(map_travel, viaje, 1)
    return map_travel
# ==============================
# Funciones de consulta
# ==============================


def primer_requerimiento(chicago, number_taxis, number_viajes):
    tra = m.newMap(numelements=30, maptype='PROBING',
                   comparefunction=compareOffenses)
    tax = m.newMap(numelements=30, maptype='PROBING',
                   comparefunction=compareOffenses)
    cola_prioridad_taxis = mi.newMinPQ(compareroutes)
    cola_prioridad_viajes = mi.newMinPQ(compareroutes)
    number = m.size(chicago['taxi'])
    total_taxis = 0
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
        value_company_taxi = me.getValue(pareja_taxi)
        total_taxis += m.size(value_company_taxi)
        mi.insert(cola_prioridad_taxis, m.size(value_company_taxi))
        m.put(tax, m.size(value_company_taxi), empresa_taxi)
        # PARTE DE VIAJES
        pareja_viaje = m.get(chicago['travel'], empresa_viaje)
        value_company_viaje = me.getValue(pareja_viaje)
        mi.insert(cola_prioridad_viajes, m.size(value_company_viaje))
        m.put(tra, m.size(value_company_viaje), empresa_viaje)
        print((empresa_viaje, m.size(value_company_viaje)))
    # print(cola_prioridad_taxis)
    # print(cola_prioridad_viajes)

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
    while i <= number_tra:
        mi.delMin(cola_prioridad_viajes)
        iterar += 1
    respuesta_viajes = auxiliar_requerimiento_uno_viajes(
        cola_prioridad_viajes, number_viajes, tra)
    return respuesta_viajes
    # return (total_taxis, number, respuesta_taxi, respuesta_viajes)


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
    res = []
    ite = 1
    while ite <= int(number_viajes):
        menor = mi.delMin(cola)
        par = m.get(tra, menor)
        llave = me.getValue(par)
        res.append((llave, menor))
        ite += 1
    res.reverse()
    return res
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
