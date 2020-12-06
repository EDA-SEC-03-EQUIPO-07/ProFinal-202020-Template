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
            'companies_2': None,
            'values_2': None,
            'values': None,
            'values': None,
            'date': None
        }

        chicago['companies'] = om.newMap(omaptype='RBT',
                                         comparefunction=compareroutes)
        chicago['companies_2'] = om.newMap(omaptype='RBT',
                                           comparefunction=compareroutes)
        chicago['values_2'] = m.newMap(numelements=30,
                                       maptype='PROBING',
                                       comparefunction=compareroutes)
        chicago['values'] = m.newMap(numelements=30,
                                     maptype='PROBING',
                                     comparefunction=compareroutes)

        chicago['date'] = om.newMap(omaptype='RBT',
                                    comparefunction=compareroutes)

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
    add_companies(chicago, company, taxi, viaje)


def totalStops(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['graph'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['graph'])
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
