from Automatas import *
from tabulate import *

"""
	Para la instalación de graphviz:

	Ubuntu $ sudo apt install python-pydot python-pydot-ng graphviz

"""

class GeneradorAFN():

	"""

		Clase generadora de AFNs con el paso de símbolos pertenecientes al alfabeto de una expresión regular o de AFNs también generados por algún método de esta clase

	"""

	def _generarAutomata(self,simbolo):
		""" Función que genera un AFN de un símbolo dado
			@param simbolo : string
			@returns afn : AFN """
		nombre = simbolo

		ef = Estado(nombre+'f',{},True)
		e0 = Estado(nombre+'0',{nombre:[ef]},False,True)

		afn = AFN(nombre)
		afn.setEstados([e0,ef])

		return afn

	def _generarUnion(self,automatas):
		""" Función que genera un AFN con la operación de union para dos símbolos o dos AFN dado
			@param automatas : list
			@returns afn : AFN """

		nombre = automatas[1].getNombre() + '|' + automatas[0].getNombre()

		afn = AFN(nombre)

		#Creación de estados comunes
		ef = Estado(nombre+'f',{},True)
		e0 = Estado(nombre+'0',{},False,True)

		afn.agregarEstado(e0)

		for automata in automatas:
			estadoInicial = automata.getEstadoInicial()
			estadoAceptacion = automata.getEstadosAceptacion()[0]

			estadoInicial.setInicial(False)
			estadoAceptacion.setAceptacion(False)
			estadoAceptacion.setToken(-1)

			e0.agregarTransicion('ε',[estadoInicial])
			estadoAceptacion.agregarTransicion('ε',[ef])

			afn.agregarEstados(automata.getEstados())

		#Se agrega el estado de aceptación
		afn.agregarEstado(ef)

		afn.renombreAutomaticoEstados('e')

		return afn

	def _generarConcatenacion(self,automatas):
		""" Función que genera un AFN con la operación de concatenación para dos símbolos o dos AFN dado
			@param automatas : list
			@returns afn : AFN """

		nombre = automatas[0].getNombre() + '°' + automatas[1].getNombre()

		afn = AFN(nombre)

		#El estado final del primer autómata se convierte en el primer estado del segundo
		automatas[0].getEstadosAceptacion()[0].setTransiciones(automatas[1].getEstadoInicial().getTransiciones())

		#Se le elimina al estado de aceptación del primer automata la propiedad de ser aceptación
		automatas[0].getEstadosAceptacion()[0].setAceptacion(False)
		#Se elimina el estado inicial del segundo autómata
		automatas[1].eliminarEstado(automatas[1].getEstadoInicial())

		#Se conforma el nuevo autómata con las modificaciones realizadas
		afn.agregarEstados(automatas[0].getEstados())
		afn.agregarEstados(automatas[1].getEstados())

		afn.renombreAutomaticoEstados('e')

		return afn


	def _generarCerraduraPositiva(self,automata):
		""" Función que genera un AFN con la operación de cerradura para un símbolo o un AFN dado
			@param automata : list
			@returns afn : AFN """
		automata = automata[0]
		nombre = automata.getNombre()

		afn = AFN(nombre)

		ef = Estado(nombre+'f',{},True)
		e0 = Estado(nombre+'0',{},False,True)

		estadoInicial = automata.getEstadoInicial()
		estadoAceptacion = automata.getEstadosAceptacion()[0]

		estadoInicial.setInicial(False)
		estadoAceptacion.setAceptacion(False)
		estadoAceptacion.setToken(-1)

		estadoAceptacion.agregarTransicion('ε',[estadoInicial,ef])
		e0.agregarTransicion('ε',[estadoInicial])

		afn.agregarEstados([e0] + automata.getEstados() + [ef])

		afn.renombreAutomaticoEstados('e')

		return afn

	def _generarCerraduraKleene(self,automata):
		""" Función que genera un AFN con la operación de cerradura de Kleene para un símbolo o un AFN dado
			@param automata : list
			@returns afn : AFN """

		afn = self._generarCerraduraPositiva(automata)

		afn.getEstadoInicial().agregarTransicion('ε',[afn.getEstadosAceptacion()[0]])

		afn.renombreAutomaticoEstados('e')

		return afn

	def _generarOpcional(self,automata):
		""" Función que genera un AFN con la operación de opcional para un símbolo o un AFN dado
			@param automata : list
			@returns afn : AFN """
		automata = automata[0]
		nombre = automata.getNombre()

		afn = AFN(nombre)

		ef = Estado(nombre+'f',{},True)
		e0 = Estado(nombre+'0',{},False,True)

		estadoInicial = automata.getEstadoInicial()
		estadoAceptacion = automata.getEstadosAceptacion()[0]

		estadoInicial.setInicial(False)
		estadoAceptacion.setAceptacion(False)
		estadoAceptacion.setToken(-1)

		estadoAceptacion.agregarTransicion('ε',[ef])
		e0.agregarTransicion('ε',[estadoInicial,ef])

		#Se agregan los estados que conforman al automata antes de realizar la operación
		afn.agregarEstados([e0] + automata.getEstados() + [ef])

		afn.renombreAutomaticoEstados('e')

		return afn

	@staticmethod
	def generarAFNDePostfija(postfija, alfabeto):
		generador = GeneradorAFN()

		operaciones = {'|':[2,generador._generarUnion], '°':[2,generador._generarConcatenacion], '⁺':[1,generador._generarCerraduraPositiva],'^+':[1,generador._generarCerraduraPositiva], '*':[1,generador._generarCerraduraKleene], '?':[1,generador._generarOpcional]}

		pilaSimbolos = []
		afn = None

		for s in postfija:
			if s in operaciones:
				#Es una operación

				automatasOperar = []

				#Se obtiene los automatas que serán operados
				for _ in range(operaciones[s][0]):
					automatasOperar.append(pilaSimbolos.pop())

				if s == '|' or s == '°':
					automatasOperar.reverse()

				#Se llama la función para operar los símbolos o AFN
				pilaSimbolos.append(operaciones[s][1](automatasOperar))

			else:
				#Es un símbolo perteneciente al alfabeto
				if s in alfabeto:
					pilaSimbolos.append(generador._generarAutomata(s))
				else:
					return -1,'Símbolo no reconocido como operación ni perteneciente al alfabeto'

		if type(pilaSimbolos[-1]) == AFN and len(pilaSimbolos) == 1:
			afn = pilaSimbolos.pop()
		else:
			return -1,'El resultado de la pila no es un autómata o existen más elementos'

		afn.setAlfabeto(alfabeto)

		return afn,'Generación correcta del AFN'


class GeneradorAFD():

	"""

		Clase generadora de los AFD a partir de los estados que conforman a un AFN

	"""

	def _mover(self, estados, simbolo):
		conjuntoResultado = set()

		for _ in range(len(estados)):
			estado = estados.pop()

			conjuntoResultado |= set(estado.getEstadosTransicion(simbolo))

		return conjuntoResultado

	def _cerraduraEpsilon(self, estados):
		conjuntoResultado = set(estados)

		for _ in range(len(estados)):
			estado = estados.pop()

			auxResultado = set(estado.getEstadosTransicion('ε'))

			conjuntoResultado |= self._cerraduraEpsilon(auxResultado)

		return conjuntoResultado

	def _irA(self, estados, simbolo):
		return self._cerraduraEpsilon(self._mover(estados, simbolo))

	def _crearNuevoEstadoConvertido(self, estadosAFN, numEstado, inicial = False):
		aceptacion = False
		estadoAux = None
		token = -1

		for auxEstado in range(len(estadosAFN)):
			token = estadosAFN.pop().getToken()
			if token > -1:
				aceptacion = True
				break

		estadoAux = Estado('s{}'.format(str(numEstado)),{},aceptacion, inicial)
		estadoAux.setToken(token)

		return estadoAux

	def _imprimirConjuntoEstados(self, conjunto):
		cadena = '{'

		while len(conjunto) > 0:
			aux = conjunto.pop()
			cadena += aux.getNombre() + ','

		cadena += '}'

		return cadena


	@staticmethod
	def generarAFDDeAFN(automata):
		#La llave se refiere al conjunto de estados del AFN resultados de una operación irA, y el valor asociado el estado instancia de la clase Estado que es utilizado en el nuevo AFD
		estadosConvertidos = {}
		#La llave se refiere al conjunto de estados obtenidos de la operación mover, y el valor asociado al conjunto de estados del autómata AFN que resulta de la operación irA con dicho conjunto de la operación Mover
		resultadosMover = {}
		estadosNoAnalizados = []

		numEstado = 1

		generador = GeneradorAFD()
		afd = AFD(automata.getNombre())
		afd.setAlfabeto(automata.getAlfabeto())

		#Creación estado S0
		estadoInicial = generador._cerraduraEpsilon([automata.getEstadoInicial()])
		estadosConvertidos[frozenset(estadoInicial)] = generador._crearNuevoEstadoConvertido(set(estadoInicial) , 0, True)
		estadosNoAnalizados.append(estadoInicial)

		while estadosNoAnalizados:

			estado = estadosNoAnalizados[0]
			estadosNoAnalizados.remove(estado)

			for simbolo in afd.getAlfabeto():
				resultadoMover = generador._mover(set(estado), simbolo)

				inResultadoMover = False
				for resMover in resultadosMover.keys():
					if set(resMover) == resultadoMover:
						inResultadoMover = True
						resultadoMover = resMover
						break

				if not inResultadoMover:
					estadoNuevo = generador._irA(set(estado), simbolo)

					#Se verifica que existan estados en la operación 
					if len(estadoNuevo) > 0:
						estadosConvertidos[frozenset(estadoNuevo)] = generador._crearNuevoEstadoConvertido(set(estadoNuevo), numEstado)
						estadosNoAnalizados.append(estadoNuevo)

						#Se agrega la transición al estado que se está analizando con el símbolo ingresado
						for estados in estadosConvertidos.keys():
							if set(estados) == estado:
								estadosConvertidos[estados].agregarTransicion(simbolo, [estadosConvertidos[frozenset(estadoNuevo)]])

						#Se agrega el resultado Mover
						resultadosMover[frozenset(resultadoMover)] = estadoNuevo

						numEstado += 1

				else:
					#Ya se existe el estado y solo se crea la transición
					for est in estadosConvertidos.keys():
						if set(est) == estado:
							estado = est
							break

					for estados in estadosConvertidos.keys():
							if set(estados) == resultadosMover[resultadoMover]:
								estadosConvertidos[estado].agregarTransicion(simbolo, [estadosConvertidos[estados]])

		#Se agregan los estados al AFD
		for conjunto,estado in estadosConvertidos.items():
			afd.agregarEstado(estado)

		return afd

class ManejadorTabulares():

	"""
		Clase convertidora de AFD a su versión tabular y viceversa

	"""

	def _guardarTabular(self, nombre, tabla):
		with open(nombre , 'w') as archivo:
			if type(tabla) == list:
				for fila in tabla:
					for i in range(len(fila)):
						cadenaImpresion = fila[i] + ('|' if i < len(fila)-1 else '\n')

						archivo.write(cadenaImpresion)
			else:
				archivo.write(tabla)

	@staticmethod
	def recuperarTabular(ruta):
		tabular = []

		with open(ruta, 'r') as archivo:
			filas = archivo.readlines()

			for fila in filas:
				cadenaAux = ''
				eraCaracter = False
				filaAux = []

				if fila[0] != '+':
					for i in range(len(fila)):
						#Es una fila que contiene los datos tabulados
						caracter = fila[i]

						if caracter != '|' and ord(caracter) != 32:
							if caracter != '\\':
								cadenaAux += caracter
							elif fila[i-1] == '\\':
								cadenaAux += '\\\\'
						elif caracter == '|' or ord(caracter) == 32:
							if caracter == '|' and i > 0:
								if fila[i-1:i+1] == '\|':
									cadenaAux += caracter
									if ord(fila[i+1]) == 32 or ord(fila[i-2]) == 32:
										#Es solo el símbolo
										filaAux.append(cadenaAux)
										cadenaAux = ''

							elif eraCaracter:
								filaAux.append(cadenaAux)
								cadenaAux = ''

						eraCaracter = False if (caracter == '|' or ord(caracter) == 32) else True

					tabular.append(filaAux)

		return tabular

	@staticmethod
	def generarAFDDeTabular(tabular):
		alfabetoAux = tabular[0][1:len(tabular[0])-1]
		afd = AFD('AFDTabular')
		afd.setAlfabeto(alfabetoAux)

		estadosAux = []

		numeroEstados = 0

		for i in range(1,len(tabular)):
			fila = tabular[i]
			estadosAux.append(Estado('s'+fila[0], inicial= True if fila[0] == '0' else False, aceptacion= True if fila[-1] != '-1' else False, token = int(fila[-1])))
			numeroEstados += 1

		afd.setEstados(estadosAux)

		numeroEstados -= 1

		while len(tabular) > 1:
			fila = tabular.pop()
			transiciones = {}

			for i in range(1, len(fila)-1):
				if fila[i] != '-1':
					estadosPorAgregar = fila[i].split(',')
					for agregar in estadosPorAgregar:
						if alfabetoAux[i-1] in transiciones:
							transiciones[alfabetoAux[i-1]] += [afd.getEstado('s'+agregar)]
						else:
							transiciones[alfabetoAux[i-1]] = [afd.getEstado('s'+agregar)]

			afd.getEstado('s'+str(numeroEstados)).setTransiciones(dict(transiciones))
			numeroEstados -= 1

			transiciones.clear()

		return afd

	@staticmethod
	def imprimirTablaConsola(tabla):
		print(tabulate(tabla, headers='firstrow', tablefmt='psql'))

	@staticmethod	
	def generarTabular(automata, nombreArchivo):
		estadosAux = list(automata.getEstados())
		alfabetoAux = automata.getAlfabeto()
		ordenEstados = 0

		tablaFinal = [['Estado']+alfabetoAux+['Token']]

		while estadosAux:
			estado = estadosAux.pop(0)

			nombreAux = estado.getNombre()[1:len(estado.getNombre())]
			if nombreAux == str(ordenEstados):
				#Estado siguiente según el orden numérico

				filaAux = [nombreAux]

				for simbolo in alfabetoAux:
					if estado.getEstadosTransicion(simbolo):
						cadenaEstados = ''

						for estadoTransicion in estado.getEstadosTransicion(simbolo):
							cadenaEstados += estadoTransicion.getNombre()[1:len(estadoTransicion.getNombre())] + ','
						cadenaEstados = cadenaEstados[0:len(cadenaEstados)-1]

						filaAux.append(cadenaEstados)

					else:
						filaAux.append('-1')

				filaAux.append(str(estado.getToken()))

				ordenEstados += 1

			else:
				#Estado no consecutivo
				estadosAux.append(estado)

			tablaFinal.append(filaAux)

		ManejadorTabulares()._guardarTabular(nombreArchivo,tabulate(tablaFinal, headers='firstrow', tablefmt='grid'))

		return tablaFinal