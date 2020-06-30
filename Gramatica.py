# -*- coding: utf-8 -*-
#@author: Lalo Valle

from AnalizadorLexico import *
from GeneradorAutomatas import GeneradorAFN
from tabulate import *


class Gramatica():

    def __init__(self):
        # Las llave del diccionario será el símbolo no terminal del lado izquierdo y el valor de este será una lista con las reglas del lado derecho
        self._reglas = {}

        self._simbolosTerminales = set()
        self._simbolosNoTerminales = set()

        self._simboloInicial = ''

    def getReglas(self):
        return self._reglas

    def getSimbolosTerminales(self):
        if len(self._simbolosTerminales) == 0:
            self._identificarSimbolosTerminales()
        return self._simbolosTerminales

    def getSimbolosNoTerminales(self):
        if len(self._simbolosNoTerminales) == 0:
            self._identificarSimbolosNoTerminales()
        return self._simbolosNoTerminales

    def getLadoDerecho(self, simbolosIzquierdos):
        ladosDerechos = []
        if type(simbolosIzquierdos) != list: simbolosIzquierdos = [simbolosIzquierdos]
        
        for simbolo in simbolosIzquierdos:
            if simbolo in self._reglas:
                ladosDerechos.append(self._reglas[simbolo])
        return ladosDerechos[0] if len(ladosDerechos) == 1 else ladosDerechos

    def getLadoIzquierdo(self, ladoDerecho):
        for izquierdo,ladosDerechos in self._reglas.items():
            if ladoDerecho in ladosDerechos:
                return izquierdo

    def getTodosLadosDerechos(self):
        ladosDerechos = []

    def getSimboloInicial(self):
        return self._simboloInicial

    def isSimboloTerminal(self,simbolo):
        return simbolo in self._simbolosTerminales

    def isSimboloNoTerminal(self,simbolo):
        return simbolo in self._simbolosNoTerminales

    def crearNuevaRegla(self, simbolo):
        if not self._reglas:
            self._simboloInicial = simbolo
        self._reglas[simbolo] = []

    def agregarLadoDerecho(self, simboloIzquierdo, reglas=[]):
        if simboloIzquierdo in self._reglas:
            for regla in reglas:
                if regla not in self._reglas[simboloIzquierdo]:
                    self._reglas[simboloIzquierdo].append(regla)

    def _identificarSimbolosNoTerminales(self):
        for simbolo in self._reglas.keys():
            self._simbolosNoTerminales.add(simbolo)

    def _identificarSimbolosTerminales(self):
        if len(self._simbolosNoTerminales) > 0:
            for _, reglas in self._reglas.items():
                for regla in reglas:
                    simboloAux = ''
                    eraTerminal = True

                    for i in range(len(regla)):
                        simbolo = regla[i]
                        simboloAux += simbolo

                        if simbolo in self._simbolosNoTerminales or simboloAux in self._simbolosNoTerminales:
                            if not eraTerminal:
                                self._simbolosTerminales.add(
                                    simboloAux[0:len(simboloAux) - 1])
                                simboloAux = simboloAux[len(
                                    simboloAux) - 1:len(simboloAux)]
                            eraTerminal = True

                        if simboloAux not in self._simbolosNoTerminales:
                            if eraTerminal:
                                simboloAux = simboloAux[len(
                                    simboloAux) - 1:len(simboloAux)]

                            if simbolo not in self._simbolosNoTerminales:
                                eraTerminal = False

                        if i == len(regla) - 1:
                            if simboloAux not in self._simbolosNoTerminales:
                                self._simbolosTerminales.add(simboloAux)

    def imprimirGramatica(self):
        g = ""
        for izquierdo, reglas in self._reglas.items():
            g += '{}=>'.format(izquierdo)
            for regla in reglas:
                g += '{}|'.format(regla)
            g += ";\n"
        return g

    def eliminarRecursionIzquierda(self):
        reglasPrimas = {}

        for simboloIzquierdo, reglas in self._reglas.items():
            alfas = []
            betas = []

            for regla in reglas:
                if regla[0] == simboloIzquierdo:
                    alfas.append(regla[1:len(regla)])
                else:
                    betas.append(regla)

            if alfas and betas:
                simboloPrimo = simboloIzquierdo + 'p'

                self._reglas[simboloIzquierdo].clear()
                for beta in betas:
                    self._reglas[simboloIzquierdo].append(beta + simboloPrimo)

                reglasPrimas[simboloPrimo] = []
                for alfa in alfas:
                    reglasPrimas[simboloPrimo].append(alfa + simboloPrimo)
                reglasPrimas[simboloPrimo].append('ε')

        self._reglas.update(reglasPrimas)


class AnalizadorSintacticoReglas():

    def __init__(self, lexico):
        self._lexico = lexico

        self._ladoIzquierdoActual = ''

        self._gramatica = Gramatica()

    def analizar(self):
        analisisValido = self._G()

        if analisisValido:
            # Se verifica que todos los caracteres de la cadena hayan sido analizados
            if self._lexico.getToken() != 0:
                analisisValido = False
                self._gramatica = Gramatica()

        return analisisValido

    def getGramaticaGenerada(self):
        return self._gramatica

    def _G(self):
        if self._listaReglas():
            return True
        return False

    def _listaReglas(self):
        if self._regla():
            if self._listaReglas():
                pass
            return True
        return False

    def _regla(self):
        if self._ladoIzquierdo():
            token = self._lexico.getToken()

            if token == TokenReglas.FLECHA:
                if self._listaLadosDerecho():
                    token = self._lexico.getToken()

                    if token == TokenReglas.PUNTO_COMA:
                        self._ladoIzquierdoActual = ''
                        return True
        return False

    def _ladoIzquierdo(self):
        token = self._lexico.getToken()

        if token == TokenReglas.SIMBOLO:
            self._ladoIzquierdoActual = self._lexico.getUltimoLexemaValido()
            self._gramatica.crearNuevaRegla(self._ladoIzquierdoActual)
            return True
        return False

    def _listaLadosDerecho(self):
        if self._ladoDerecho():
            token = self._lexico.getToken()

            if token == TokenReglas.UNION:
                if self._listaLadosDerecho():
                    return True
                return False
            else:
                self._lexico.rewind()
                return True

        return False

    def _ladoDerecho(self):
        if self._listaSimbolo():
            return True
        return False

    def _listaSimbolo(self):
        token = self._lexico.getToken()

        if token == TokenReglas.SIMBOLO:
            self._gramatica.agregarLadoDerecho(self._ladoIzquierdoActual, [
                                               self._lexico.getUltimoLexemaValido()])
            if self._listaSimbolo():
                return True
        else:
            self._lexico.rewind()
            return True
        return False


class AnalizadorSintacticoLL1():

    def __init__(self, gramatica, cadena=''):
        self._gramatica = gramatica

        self._tablaLL1 = []
        self._simbolosPosicionesTabla = {'$':-1}

        self._cadena = cadena

        """
            Las siguientes listas sirven para evitar la realización de operaciones redundantes, tanto como para first y follow
            La estructura que tienen será la siguiente, con la particularidad de no tener índice aquel usado para el follow
            {
                {resultado}:[(regla,indice),(regla,indice),...]
            }
        """
        self._firstCalculados = {}
        self._followCalculados = {}

    def setCadena(self, cadena):
        self._cadena = cadena+'$'

    def _identificarSimbolos(self,regla,indice=0):
        simbolosIdentificados = []

        reconocido = None
        simbolo = ''

        #Identifica si el símbolo que se analizará es un terminal o no terminal
        for i in range(indice,len(regla)):
            simbolo += regla[i]

            if self._gramatica.isSimboloTerminal(simbolo) or self._gramatica.isSimboloNoTerminal(simbolo):
                reconocido = 'N' if self._gramatica.isSimboloNoTerminal(simbolo) else 'T'
            else:
                if reconocido != None:
                    simbolosIdentificados.append((simbolo[0:len(simbolo)-1],reconocido))
                    simbolo = simbolo[len(simbolo)-1:len(simbolo)]
        simbolosIdentificados.append((simbolo,reconocido))

        return simbolosIdentificados

    def agregarFirstCalculados(self,resultado,regla,indice=0):
        resultado = frozenset(resultado)

        if resultado in self._firstCalculados:
            self._firstCalculados[resultado].append((regla,indice))
        else:
            self._firstCalculados[resultado] = [(regla,indice)]

    def getResultadoFirstCalculados(self,regla,indice=0):
        for resultado,reglas in self._firstCalculados.items():
            if (regla,indice) in reglas:
                return set(resultado)

        return None

    def agregarFollowCalculados(self,resultado,simbolo):
        resultado = frozenset(resultado)

        if resultado in self._followCalculados:
            self._followCalculados[resultado].append(simbolo)
        else:
            self._followCalculados[resultado] = [simbolo]

    def getResultadoFollowCalculados(self,simbolo):
        for resultado,simbolos in self._followCalculados.items():
            if simbolo in simbolos:
                return set(resultado)

        return None

    def first(self,regla,indice=0):
        resultado = None

        if resultado == None:
            #Aún no se ha calculado el first de la regla ingresada
            resultado = set()

            terminales = self._gramatica.getSimbolosTerminales()
            noTerminales = self._gramatica.getSimbolosNoTerminales()

            #Identifica si el símbolo que se analizará es un terminal o no terminal
            simbolo,reconocido = self._identificarSimbolos(regla, indice)[0]

            #Acciones si se trata de un terminal o un no terminal
            if reconocido == 'N':
                #Se genera el árbol que analiza las reglas del no terminal hasta encontrar los primeros terminales de forma recursiva
                ladoDerecho = self._gramatica.getLadoDerecho(simbolo)

                for reglaAux in ladoDerecho:
                    resultadoAux = self.first(reglaAux)
                    resultado |= resultadoAux

            elif reconocido == 'T':
                #Ya se ha encontrado el primer terminal y se agrega al conjunto resultado
                resultado.add(simbolo)

            self.agregarFirstCalculados(resultado, regla, indice)

        return resultado

    def follow(self,simbolo):
        resultado = None#self.getResultadoFollowCalculados(simbolo)

        if resultado == None:
            resultado = set()
            #Se agrega al conjunto resultado el signo $ por ser el símbolo inicial de la gramática
            if simbolo == self._gramatica.getSimboloInicial():
                resultado.add('$')

            if not self._gramatica.isSimboloTerminal(simbolo):
                reglasConSimbolo = []

                #Se obtienen todas las reglas de lado derecho que tengan al símbolo de entrada
                for ladoDerecho in self._gramatica.getLadoDerecho(list(self._gramatica.getSimbolosNoTerminales())):
                    for regla in ladoDerecho:
                        posicion = regla.find(simbolo)

                        if posicion >= 0:
                            #Se debe verificar que es esta regla tiene exclusivamente a ese símbolo y no a otro símbolo que contenga a este mismo
                            if posicion+len(simbolo) < len(regla):
                                simboloAux = regla[posicion+len(simbolo)]
                                if self._gramatica.isSimboloTerminal(simboloAux) or self._gramatica.isSimboloNoTerminal(simboloAux):
                                    reglasConSimbolo.append(regla)
                            else: reglasConSimbolo.append(regla)

                for regla in reglasConSimbolo:
                    posicion = regla.find(simbolo)

                    if posicion+len(simbolo) == len(regla):
                        #El símbolo ingresado es el último de la regla o un epsilon
                        simboloFollow = self._gramatica.getLadoIzquierdo(regla)
                        if simboloFollow != simbolo:
                            followAux = self.getResultadoFollowCalculados(simboloFollow)
                            resultado |= self.follow(simboloFollow) if followAux == None else followAux

                    else:
                        #Se encontró un símbolo que procede al ingresado para la operación follow
                        simboloFirst = regla[posicion+len(simbolo)]
                        
                        firstAux = self.getResultadoFirstCalculados(regla,posicion+len(simbolo))
                        resultadoAux = self.first(regla,posicion+len(simbolo)) if firstAux == None else firstAux

                        while True:
                            #Se debe verificar que el cojunto resultado del first no contenga a epsilon
                            if 'ε' in resultadoAux:
                                resultadoAux.discard('ε')
                                followAux = self.getResultadoFollowCalculados(self._gramatica.getLadoIzquierdo(regla))
                                resultadoAux |= self.follow(self._gramatica.getLadoIzquierdo(regla)) if followAux == None else followAux

                            else:
                                break

                        resultado |= resultadoAux

            self.agregarFollowCalculados(resultado, simbolo)

        return resultado

    def crearTablaLL1(self):
        if self._tablaLL1:
            self._tablaLL1.clear()

        terminales = set(self._gramatica.getSimbolosTerminales())
        noTerminales = set(self._gramatica.getSimbolosNoTerminales())

        #Se crea la tabla
        self._tablaLL1 = [['' for _ in range(len(terminales)+2)] for _ in range(len(noTerminales)+2)]

        #Se agregan los símbolos terminales a la primer fila y los no terminales a la primer columna
        terminalesAux = set(terminales)
        noTerminalesAux = set(noTerminales)
        for i in range(len(noTerminales)+1):
            if i == 0:
                for j in range(1,len(terminales)):
                    simbolo = terminalesAux.pop()
                    if simbolo == 'ε':
                        if len(terminalesAux) > 0:
                            simbolo = terminalesAux.pop()
                        else:
                            break

                    self._tablaLL1[i][j] = simbolo
                    self._simbolosPosicionesTabla[simbolo] = j
                self._tablaLL1[i][-1] = '$'
            else:
                simbolo = noTerminalesAux.pop()

                self._tablaLL1[i][0] = simbolo
                self._simbolosPosicionesTabla[simbolo] = i
        self._tablaLL1[-1][0] = '$'

        #Inicia el llenado de la tabla
        for ladoIzquierdo,reglas in self._gramatica.getReglas().items():
            for ladoDerecho in reglas:
                if ladoDerecho != 'ε':
                    resultado = set(self.first(ladoDerecho))
                else:
                    #Se realizará el follow del lado izquierdo por ser ε
                    resultado = set(self.follow(ladoIzquierdo))

                #Se agregan los reglas a la tabla
                fila = self._simbolosPosicionesTabla[ladoIzquierdo]
                while resultado:
                    columna = self._simbolosPosicionesTabla[resultado.pop()]

                    self._tablaLL1[fila][columna] = ladoDerecho
        self._tablaLL1[-1][-1] = True

        return tabulate(self._tablaLL1)

    def analizar(self):
        pila = ['$','E']
        subCadena = self._cadena

        indiceSimbolo = 0
        simbolo = ''

        while len(subCadena) > 0:
            if simbolo in self._simbolosPosicionesTabla:
                ultimaRegla = pila.pop()
                pasar = False

                if ultimaRegla != '$':
                    if self._gramatica.isSimboloTerminal(ultimaRegla):
                        #Se verifica que la ultima regla y el primer caracter de la cadena sean iguales
                        if ultimaRegla == simbolo:
                            #Se acorta la cadena y se evita realizar alguna acción
                            subCadena = subCadena[len(simbolo):len(subCadena)]
                            pasar = True

                if not pasar:
                    accion = self._tablaLL1[self._simbolosPosicionesTabla[ultimaRegla]][self._simbolosPosicionesTabla[simbolo]]

                    if type(accion) != bool:
                        #Convertimos la regla obtenida y la ingresamos de forma inversa a la pila
                        accion = self._identificarSimbolos(accion)
                        for i in range(len(accion)-1,-1,-1):
                            if accion[i][0] != 'ε':
                                pila.append(accion[i][0])
                    
                    else: return accion,'Cadena correcta'

                simbolo = ''
                indiceSimbolo = 0

            elif indiceSimbolo < len(subCadena):
                #El símbolo es mayor a un solo caracter
                simbolo += subCadena[indiceSimbolo]

                indiceSimbolo += 1
            else:
                #Se han concatendado todos los caracteres restantes de la cadena y no fue reconocio como símbolo de la gramática
                return False,'ERROR>> Símbolo no perteneciente a la gramática(posición {})'.format(self._cadena.find(simbolo[0]))
        
        return False,''