# -*- coding: utf-8 -*-
#@author: Lalo Valle

from AnalizadorLexico import *
from GeneradorAutomatas import GeneradorAFN
from tabulate import *
from Gramatica import *

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
            self._gramatica.agregarLadoDerecho(self._ladoIzquierdoActual, [self._lexico.getUltimoLexemaValido()])
            if self._listaSimbolo():
                return True
        else:
            self._lexico.rewind()
            return True
        return False


class AnalizadorSintacticoLR():

    def __init__(self, gramatica, cadena=''):
        self._gramatica = gramatica
        # Estados resultados del análisis y aplicación de la operación IrA
        self._conjuntoEstados = []
        # En la tabla se identificarán los desplazamientos cuando el tipo de dato en la celda sea un objeto de tipo EstadoItems, de otra forma, si el tipo de dato es un int se trata de una reducción indicando el número de regla
        self._tablaLR = []

        self._cadena = cadena
        # Utilizada como ayuda para conocer la columna en la que cada símbolo se ha colocado
        self._posicionesSimbolos = {}
        """
            Las siguientes listas sirven para evitar la realización de operaciones redundantes, tanto como para first y follow
            La estructura que tienen será la siguiente, con la particularidad de no tener índice aquel usado para el follow
            {
                {resultado}:[(regla,indice),(regla,indice),...]
            }
        """
        self._firstCalculados = {}
        self._followCalculados = {}

    def getConjuntoEstados(self):
        return self._conjuntoEstados

    def agregarConjuntoItem(self,conjunto):
        self._conjuntosItems.append(conjunto)

    def setCadena(self, cadena):
        self._cadena = cadena

    def identificarSimbolos(self,regla,indice=0):
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
            simbolo,reconocido = self.identificarSimbolos(regla, indice)[0]

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
        resultado = None

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
                                simboloAux = self._gramatica.identificarSimbolosEnCadena(regla[posicion+len(simbolo):],1)[0]

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

    def cerradura(self,items,LR1=False):
        resultado = EstadoItems('EC',[],[])
        itemsSinAnalizar = None
        # Lista utilizada para evitar la redundancia al analizar las reglas de lado derecho de un símbolo que ya ha sido analizado
        simbolosAnalizados = []
        cabezera = 0

        # Se identifica si el elemento ingresado es una lista de items o un objeto de tipo EstadoItems
        if type(items) == EstadoItems:
            items = items.getItems()

        # Añade los items a ser analizados dependiendo del formato de la lista(con cabezera o sin esta)
        if type(items[0]) == int:
            cabezera = items.pop(0)
            itemsSinAnalizar = list(items[0:cabezera])
        else:
            cabezera = len(items)
            itemsSinAnalizar = list(items)

        # Ciclo del análisis de los items generados
        while itemsSinAnalizar:
            item = itemsSinAnalizar.pop(0).item()
            # Se decide si se agrega a los items de la cabezera o a los derivados
            if cabezera > 0:
                resultado.agregarItemCabezera(item)
                cabezera -= 1
            else: resultado.agregarItemDerivado(item)

            simbolo = item.getCaracterPrecedenteAlPunto(self._gramatica)

            # Si el simbolo después del punto no es termninal o None entonces se obtienen los lados derechos de la regla
            if simbolo != None:
                if simbolo not in simbolosAnalizados:
                    if self._gramatica.isSimboloNoTerminal(simbolo):
                        simbolosAnalizados.append(simbolo)
                        terminalesValidosAux = set()

                        # Se identifica el conjunto de terminales válidos para los items generados
                        if LR1:
                            segundoSimbolo = item.getCaracterPrecedenteAlPunto(self._gramatica,caracterPrecedente=2)
                            # Se verifica el segundo símbolo que procede al punto para decidir el conjunto de símbolos terminales válidos del nuevo item
                            if self._gramatica.isSimboloTerminal(segundoSimbolo): terminalesValidosAux.add(segundoSimbolo)
                            else: terminalesValidosAux = set(item.getTerminalesValidos())

                        # Se agregan las reglas a los items sin analizar
                        ladosDerechos = list(self._gramatica.getLadoDerecho(simbolo))
                        for lado in ladosDerechos:
                            itemsSinAnalizar.append(Item(simbolo,lado,terminalesValidos=set(terminalesValidosAux)))
                elif LR1:
                    # El símbolo que se analiza ya ha generado las reglas correspondientes pero deben de integrarse los símbolos terminales válidos del item actual a aquellos con la misma regla izquierda
                    segundoSimbolo = item.getCaracterPrecedenteAlPunto(self._gramatica,caracterPrecedente=2)
                    # Se verifica el segundo símbolo que procede al punto para decidir el conjunto de símbolos terminales válidos del nuevo item
                    if self._gramatica.isSimboloTerminal(segundoSimbolo): terminalesValidosAux.add(segundoSimbolo)
                    else: terminalesValidosAux = set(item.getTerminalesValidos())
                    # Se busca el item con la regla izquierda igual
                    for itemAux in resultado.getItems()[1:]+itemsSinAnalizar:
                        if itemAux.getLadoIzquierdo() == simbolo:
                            itemAux.agregarTerminalesValidos(set(terminalesValidosAux))

        return resultado


    def mover(self,items,caracter):
        resultado = EstadoItems('EM',[],[])

        # Se identifica si el elemento ingresado es una lista de items o un objeto de tipo EstadoItems
        if type(items) == EstadoItems:
            items = items.getItems()

        # Se elimina el número que corresponde a la cabezera
        if type(items[0]) == int:
            items.pop(0)

        itemsAux = list(items)
        for item in itemsAux:
            # Se evalúa si el caracter siguiente al punto es el caracter indicado en la operación
            if caracter == item.getCaracterPrecedenteAlPunto(self._gramatica):
                item = item.item()
                item.incrementarPosicionPunto(len(caracter))

                resultado.agregarItemCabezera(item)

        return resultado

    def getTablaLREnCadena(self):
        tablaAux = [['' for _ in range(len(self._tablaLR[0]))] for _ in range(len(self._tablaLR))]

        # Se copia la primer fila y la primer columna
        for i in range((len(self._tablaLR[0]) if len(self._tablaLR[0]) > len(self._tablaLR) else len(self._tablaLR))):
            if i < len(self._tablaLR[0]):
                tablaAux[0][i] = self._tablaLR[0][i]
            if i < len(self._tablaLR):
                tablaAux[i][0] = self._tablaLR[i][0]
        
        for i in range(1,len(self._tablaLR)):
            for j in range(1,len(self._tablaLR[0])):
                elemento = self._tablaLR[i][j]

                if elemento != '':
                    if type(elemento) == int:
                        # Se trata de el número de regla de una reducción
                        tablaAux[i][j] = 'r{}'.format(elemento) if elemento != 0 else 'Aceptar'
                    elif type(elemento) == EstadoItems:
                        # Se trata de un desplazamiento
                        if self._gramatica.isSimboloTerminal(self._tablaLR[0][j]):
                            tablaAux[i][j] = 'd{}'.format(elemento.getNombre())
                        else:
                            tablaAux[i][j] = elemento.getNombre()

        return tabulate(tablaAux, headers="firstrow",tablefmt="fancy_grid")


    def generarTablaSLR(self,LR1=False):
        """
            
            Creación y Análisis de los conjuntos de items mediante la operación IrA(la cerradura de la operación mover con cierto simbolo)
        
        """
        numeroEstado = 1
        estadosSinAnalizar = [self.cerradura([Item(self._gramatica.getSimboloInicial(), self._gramatica.getLadoDerecho(self._gramatica.getSimboloInicial())[0],terminalesValidos = set('$') if LR1 else set())],LR1=LR1)]
        self._conjuntoEstados = []
        # Se le asigna el nombre al primer estado
        estadosSinAnalizar[0].setNombre('E0')

        # Inicia el ciclo de análisis de los conjuntos generados
        while estadosSinAnalizar:
            estado = estadosSinAnalizar.pop(0)

            simbolosMover = estado.getCaracteresPrecedentesALosPuntos(self._gramatica)

            # Se realizará la operación mover si existen simbolos posibles después del punto en los items
            if simbolosMover:
                while simbolosMover:
                    estadoExistente = False
                    simbolo = simbolosMover.pop()

                    estadoNuevo = self.mover(estado,simbolo)

                    # Se verifica si existe algún estado de los creados hasta el momento contiene la misma cabezera que el obtenido resultado de la operación mover
                    if self._conjuntoEstados:
                        for creados in self._conjuntoEstados+estadosSinAnalizar+[estado]:
                            if creados.isCabezeraIgual(estadoNuevo):
                                estado.agregarTransicion(simbolo,creados)
                                estadoExistente = True
                                break

                    if not estadoExistente:
                        # Se realiza la operación de cerradura al estado obtenido de mover
                        estadoNuevo = self.cerradura(estadoNuevo,LR1)

                        estadoNuevo.setNombre('E{}'.format(numeroEstado))
                        numeroEstado += 1
                        estado.agregarTransicion(simbolo,estadoNuevo)

                        estadosSinAnalizar.append(estadoNuevo)

            self._conjuntoEstados.append(estado)
        
        """

            Proceso de reducción en estados con puntos finales

        """
        # La llave del diccionario reducciones indica el número del estado y su valor será una tupla que tiene dos elementos: El número de regla a reducir y una lista con los terminales válidos para la reducción
        reducciones = {}
        for i in range(len(self._conjuntoEstados)):
            terminales = []
            estado = self._conjuntoEstados[i]
            item = None

            puntoFinal, regla = estado.tienePuntosFinales(self._gramatica)
            if puntoFinal:
                numeroRegla = self._gramatica.getNumeroRegla(regla[0],regla[1])
                # Se obtiene el item con el punto final
                if LR1:
                    for itemCandidato in estado.getItemsCabezera():
                        if itemCandidato.getLadoIzquierdo() == regla[0] and itemCandidato.getLadoDerecho() == regla[1]:
                            item = itemCandidato
                            break
                terminalesValidos = self.follow(regla[0]) if item == None else set(item.getTerminalesValidos())
                reducciones[i] = (numeroRegla,terminalesValidos)
        """
            
            Creación e inicialización gráfica de la tabla

        """
        simbolos = list(self._gramatica.getSimbolosTerminales()) + ['$'] + list(self._gramatica.getSimbolosNoTerminales())
        simbolos.remove(self._gramatica.getSimboloInicial())
        # Creación de la tabla
        self._tablaLR = [['' for _ in range(len(simbolos)+1)] for _ in range(len(self._conjuntoEstados)+1)]
        self._tablaLR[0][0] = 'SLR'
        # Se colocan en la parte superior los símbolos
        for i in range(1,len(simbolos)+1):
            simbolo = simbolos.pop(0)
            self._posicionesSimbolos[simbolo] = i

            self._tablaLR[0][i] = simbolo
        # Se colocan los números de los estados en la primer columna
        for i in range(1,len(self._conjuntoEstados)+1):
            self._tablaLR[i][0] = 'E{}'.format(i-1)

        """

            Relleno de la tabla con desplazamientos y reducciones

        """
        # Inicio de la colocación de los desplazamientos
        for i in range(len(self._conjuntoEstados)):
            estado = self._conjuntoEstados[i]
            for simbolo,estadoTransicionado in estado.getTransiciones().items():
                self._tablaLR[i+1][self._posicionesSimbolos[simbolo]] = estadoTransicionado
        # Colocación de las reducciones
        for fila,tupla in reducciones.items():
            numeroRegla = tupla[0]
            simbolos = tupla[1]

            for simbolo in simbolos:
                self._tablaLR[fila+1][self._posicionesSimbolos[simbolo]] = numeroRegla

    def analizarCadena(self):
        cadenaAux = self._gramatica.identificarSimbolosEnCadena(self._cadena) + ['$']
        pila = ['$',0]

        tablaImpresion = [['Pila','Cadena','Acción']]

        # Ciclo principal del proceso de analisis
        while True:
            cadenaPila = ''
            cadenaFilaAux = ''
            # Se crean las cadenas que muestrán el proceso de analisis de forma gráfica como una tabla
            for elemento in pila: cadenaPila = cadenaPila+'{} '.format(str(elemento) if type(elemento) == int else elemento)
            for simbolo in cadenaAux: cadenaFilaAux += '{} '.format(simbolo) 
            filaAux = [cadenaPila,cadenaFilaAux]

            if cadenaAux[0] != None:
                accion = self._tablaLR[pila[-1]+1][self._posicionesSimbolos[cadenaAux[0]]]

                if type(accion) == EstadoItems:
                    # Es un desplazamiento al estado indicado
                    pila += [cadenaAux.pop(0),int(accion.getNombre()[1:])]
                    filaAux.append('d{}'.format(accion.getNombre()))
                elif type(accion) == int:
                    # Se trata de una reducción
                    filaAux.append('r{}'.format(accion))
                    if accion > 0:
                        regla = self._gramatica.getReglaPorNumero(accion)
                        # Se desencolan los elementos de la pila correspondientes al número de símbolos de la regla
                        for _ in range(len(self._gramatica.identificarSimbolosEnCadena(regla[1]))*2): pila.pop()

                        pila += [regla[0],int(self._tablaLR[pila[-1]+1][self._posicionesSimbolos[regla[0]]].getNombre()[1:])]

                    else:
                        # Se reduce a la regla 0 lo que equivale a una cadena válida
                        filaAux.append('Aceptar')
                        break
                else:
                    # Se trata de una celda vacía, por lo que indica que la gramática no puede reconocer esta cadena ingresada
                    print('ERROR >> La estructura de la cadena no se reconoce con la gramática especificada')
                    return False
            else:
                print('ERROR >> Existe un caracter en la cadena no reconocido para la gramatica especificada')
                return False

            tablaImpresion.append(filaAux)

        return True,tablaImpresion