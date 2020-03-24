# -*- coding: utf-8 -*-
#@author: Lalo Valle

import graphviz as gv

class Estado():

	"""

		Clase definitoria de un estado para un AFN o un AFD

			nombre: 		Nombre del estado
			transiciones:	Diccionario que define las transiciones del estado con otros estados, la llave es un síbolo del alfabeto y los elementos descritos por la llave los estados a los que transiciona
			aceptacion:		Valor Booleano lo denota como estado de aceptación

		Se puede expresar un complemento de un conjunto de símbolos de la forma:
			símbolo = '!,s1,s2,...,sn'

	"""

	@staticmethod
	def estado(estado):
		nuevoEstado = Estado(str(estado.getNombre()),aceptacion=bool(estado.isAceptacion),inicial=bool(estado.isInicial),token=int(estado.getToken()))
		for simbolo,estados in estado.getTransiciones().items():
			nuevoEstado.agregarTransicion(str(simbolo),estados)

		return nuevoEstado

	def __init__(self, nombre, transiciones = {} , aceptacion = False, inicial = False, token=-1):
		self._nombre = nombre
		self._transiciones = transiciones
		self._aceptacion = aceptacion
		self._inicial = inicial
		self._token = token

	# Getters

	def getNombre(self):
		return self._nombre

	def getTransiciones(self):
		return self._transiciones

	def getEstadosTransicion(self, simbolo):
		if len(simbolo) == 1:
			if ord(simbolo) == 92:
				simbolo = '\\\\'

		if simbolo in self._transiciones:
			return self._transiciones[simbolo]
		else:
			#Se verifica que exista un conjunto de símbolos en el estado
			simbolosComplemento = []
			estadosTransicion = []

			for simbolos in self._transiciones.keys():
				if simbolos.find(',') >= 0:
					#existe un complemento
					simbolosConjunto = simbolos.split(',')

					if simbolosConjunto[0] == '!':
						#Conjunto complemento
						if simbolo not in simbolosConjunto:
							estadosTransicion = self._transiciones[simbolos]
							break
					elif simbolo in simbolosConjunto:
						estadosTransicion = self._transiciones[simbolos]
						break

			return estadosTransicion

	def isAceptacion(self):
		return self._aceptacion

	def isInicial(self):
		return self._inicial

	def getToken(self):
		return self._token

	# Setters

	def setNombre(self, nombre):
		self._nombre = nombre

	def setTransiciones(self, transiciones):
		self._transiciones = transiciones

	def setAceptacion(self, aceptacion = True):
		self._aceptacion = aceptacion

	def setInicial(self, inicial = True):
		self._inicial = inicial

	def agregarTransicion(self, simbolo, estados = []):
		if simbolo in self._transiciones:
			for estado in estados:
				if estado not in self._transiciones[simbolo]:
					self._transiciones[simbolo].append(estado)
		else:
			self._transiciones[simbolo] = estados

	def setToken(self, token):
		self._token = token

	# Operaciones

	def mover(self, simbolo):
		""" Operación que retorna un conjunto de estados al que transiciona un estado con el símbolo dado

			@param simbolo: string
			@returns transiciones[simbolo] : list(Estado)"""

		return self._transiciones[simbolo]


class Automata():
	"""

		Clase definitoria de un Automata y los elementos que lo componen:

			nombre: 	Nombre para identificación del autómata
			estados: 	Lista del conjunto de objetos tipo Estado
			alfabeto: 	Conjunto de símbolos que conforman al alfabeto del Automata

	"""

	def __init__(self, nombre, estados = [], alfabeto = []):
		self._nombre = nombre
		self._estados = []
		self._alfabeto = []

	# Getters

	def getNombre(self):
		return self._nombre

	def getEstados(self):
		return self._estados

	def getAlfabeto(self):
		return self._alfabeto

	def getEstado(self, nombre):
		for estado in self._estados:
			if estado.getNombre() == nombre:
				return estado

		return None

	def getEstadosAceptacion(self):
		estadosAceptacion = []

		for estado in self._estados:
			if estado.isAceptacion():
				estadosAceptacion.append(estado)

		return estadosAceptacion

	def getEstadoInicial(self):
		for estado in self._estados:
			if estado.isInicial():
				return estado

	def inAlfabeto(self, simbolo):
		return simbolo in self._alfabeto

	# Setters

	def setEstados(self, estados):
		self._estados = estados

	def setAlfabeto(self, alfabeto):
		self._alfabeto = alfabeto

	def agregarEstado(self, estado):
		""" Método que permite agregar un estado al conjunto perteneciente al Autómata

			@param estado: Estado
			@returns 0 : en caso correcto // -1 : estado no es una instancia de la clase Estado """

		if type(estado) == Estado and estado not in self._estados:
			self._estados.append(estado)
			return 0

		return -1

	def agregarEstados(self, estados):

		for estado in estados:
			if estado not in self._estados:
				self._estados.append(estado)

	def agregarSimboloAlfabeto(self, simbolo):
		""" Método que permite agregar un símbolo al Alfabeto perteneciente al Autómata

			@param simbolo: string
			@returns 0 : en caso correcto // -1 : el símbolo ya es parte del Alfabeto """

		if simbolo not in self._alfabeto:
			self._alfabeto.append(simbolo)
			return 0

		return -1

	def agregarAlfabeto(self, alfabeto):
		for simbolo in alfabeto:
			if simbolo not in self._alfabeto:
				self._alfabeto.append(simbolo)

	# Operaciones

	def imprimirAutomataConsola(self):

		print('Automata: ' + self._nombre + '\n')
		#Se imprime el estado inicial y sus transiciones

		estadosAceptacion = []

		#Se imprimen los demás estados
		for estado in self._estados:
			if estado.isAceptacion():
				estadosAceptacion.append(estado)

			else:
				print(estado.getNombre() + ': ', end='')

				for simbolo,es in estado.getTransiciones().items():
					print('{' + simbolo + '=>',end='')

					for n in es:
						print(',' + n.getNombre(),end='')

					print('}')

			#Finalmente los estados de aceptación
			for aceptacion in estadosAceptacion:
				print(aceptacion.getNombre() + '(f): ',end='')
				for simbolo,es in aceptacion.getTransiciones().items():
					print('{' + simbolo + '=>',end='')

					for n in es:
						print(',' + n.getNombre(),end='')

					print('}')

			estadosAceptacion.clear()

			print('>>>>>>>>>>>>>>>>>>>>>>\n')

	def imprimirAutomata(self):

		graficador = gv.Digraph(format='svg')
		graficador.graph_attr['rankdir'] = 'LR'
		graficador.node('ini', shape="point")

		for estado in self._estados:
			nombre = estado.getNombre()

			if estado.isAceptacion():
				graficador.node(nombre, shape="doublecircle")
			else:
				graficador.node(nombre)

			if estado.isInicial():
				graficador.edge('ini',nombre)

		for estado in self._estados:
			for simbolo, estadosTransiciones in estado.getTransiciones().items():
				nombre = estado.getNombre()

				for estadoTransicion in estadosTransiciones:
					graficador.edge(nombre,estadoTransicion.getNombre(), label=simbolo)

		graficador.render(view=True)


	def eliminarEstado(self,estado):
		self._estados.remove(estado)

	def renombreAutomaticoEstados(self,letra):

		numero = 0
		pilaRevisados = []
		pilaPendientes = []
		estadoInicial = self.getEstadoInicial()

		estadoInicial.setNombre(letra + str(numero))

		pilaRevisados.append(estadoInicial)

		#Se ingresan los primeros estados, transiciones del estado inicial, a la pila para la revisión
		for simbolo,estados in estadoInicial.getTransiciones().items():
			for estado in estados:
				if estado not in pilaRevisados:
					pilaPendientes.append(estado)

		while pilaPendientes:
			estadoAux = pilaPendientes.pop()

			pilaRevisados.append(estadoAux)

			if not estadoAux.isAceptacion():
				numero += 1
				estadoAux.setNombre(letra + str(numero))
			else:
				if estadoAux.getToken() == 0:
					estadoAux.setNombre(letra + 'f')
				else:
					estadoAux.setNombre('T' + str(estadoAux.getToken()))

			for simbolo,estados in estadoAux.getTransiciones().items():
				for estado in estados:
					if estado not in pilaRevisados:
						pilaPendientes.append(estado)

		#Se verifica si ya no hay estados pendientes por revisar y que el conjunto de estados revisados tenga el mismo número de elementos que el de los 'estados' de la clase
		if not pilaPendientes and len(pilaRevisados) == len(self._estados):
			return 0,'Renombre Correcto'
		else:
			return -1,'Error en el Renombre'

	def automata(self, automata):
		self._nombre = automata.getNombre()
		self._estados = automata.getEstados()
		self._alfabeto = automata.getAlfabeto()



class AFN(Automata):

	"""

		Clase definitoria de un AFN

	"""

	def __init__(self, nombre, estados =[], alfabeto = []):
		Automata.__init__(self, nombre, estados, alfabeto)


class AFD(Automata):

	"""

		Clase definitori de una AFD

	"""
	def __init__(self, nombre, estados = [], alfabeto = []):
		Automata.__init__(self, nombre, estados, alfabeto)
