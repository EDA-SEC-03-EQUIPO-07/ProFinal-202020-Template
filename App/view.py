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
import sys
import config
from App import controller
from DISClib.ADT import stack
import timeit
assert config

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________
initialStation = None
recursionLimit = 2000

# ___________________________________________________
#  Menu principal
# ___________________________________________________


def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Inicializar Analizador")
    print("2- Cargar información del servicio de taxis")
    print("3- Primer requerimiento ")
    print("4- Segundo requerimiento")
    print("0- Salir")
    print("*******************************************")


"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n>')

    if int(inputs[0]) == 1:
        print("\nInicializando....")
        # cont es el controlador que se usará de acá en adelante
        cont = controller.init()

    elif int(inputs[0]) == 2:
        print("\nCargando información....")
        controller.loadTrips(cont)
        executiontime = timeit.timeit(number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 3:
        number_taxis = input("Ingrese el numero de compañias con más taxis ")
        number_viajes = input("Ingrese el numero de compañias con más viajes ")
        value_1 = controller.primer_requerimiento(
            cont, number_taxis, number_viajes)
        executiontime = timeit.timeit(number=1)
        print("Los resultados son los siguientes " + str(value_1))
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 4:
        number_taxis = input("Ingrese el de taxis ")
        date = input("Ingrese la fecha ")
        value_2 = controller.segunda_consulta(cont, number_taxis, date)
        executiontime = timeit.timeit(number=1)
        print("La información es la siguiente: " + str(value_2))
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 5:
        value_3 = controller.tercera_consulta(cont)
        executiontime = timeit.timeit(number=1)
        print("La información es la siguiente: " + str(value_3))
        print("Tiempo de ejecución: " + str(executiontime))

    else:
        sys.exit(0)
sys.exit(0)
