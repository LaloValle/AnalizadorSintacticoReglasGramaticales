# -*- coding: utf-8 -*-
#@author: Lalo Valle

from Automatas import *

class AnalizadorLexico():

	def __init__(self, automata, cadena):
		self._cadena = cadena

		self._estadoActual = automata.getEstadoInicial()
		self._indiceCadena = 0
		self._ultimoLexema = ''
		self._ultimoEstadoAceptacion = None

		#{EstadoAceptacion,índiceCadena,Lexema}
		self._historialEstadosAceptacion = [[Estado.estado(self._estadoActual),0,'']]

	def getToken(self):
		if self._indiceCadena == len(self._cadena):
			return 0

		while self._indiceCadena < len(self._cadena):
			estadoTransicion = self._estadoActual.getEstadosTransicion(self._cadena[self._indiceCadena])

			if estadoTransicion:
				self._estadoActual = estadoTransicion[0]
				self._ultimoLexema += self._cadena[self._indiceCadena]
				self._indiceCadena += 1

				if self._estadoActual.isAceptacion():

					self._ultimoEstadoAceptacion = Estado.estado(self._estadoActual)
					self._historialEstadosAceptacion.append([Estado.estado(self._estadoActual),int(int(self._indiceCadena)),self._ultimoLexema])
					
					if self._indiceCadena == len(self._cadena): return self._estadoActual.getToken()

			else:
				#No hay transiciones para el símbolo
				if self._ultimoEstadoAceptacion.getNombre() == self._historialEstadosAceptacion[-1][0].getNombre() and self._ultimoLexema != self._historialEstadosAceptacion[-1][2]:
					#Error de entrada: Él último estado de aceptación visto es el mismo que el del último lexema válido encontrado
					self._indiceCadena = len(self._cadena)
					self._ultimoLexema = ''

					return -1
				
				if len(self._historialEstadosAceptacion) > 1:
					self._estadoActual = self._historialEstadosAceptacion[0][0]
					self._ultimoLexema = self._ultimoLexema[len(self._historialEstadosAceptacion[-1][2])+1:len(self._ultimoLexema)]
					self._ultimoEstadoAceptacion = Estado.estado(self._historialEstadosAceptacion[-1][0])

					return self._historialEstadosAceptacion[-1][0].getToken()

	def rewind(self):
		self._historialEstadosAceptacion.pop()

		self._ultimoLexema = ''
		self._estadoActual = self._historialEstadosAceptacion[-1][0]
		self._indiceCadena = self._historialEstadosAceptacion[-1][1]
		self._ultimoEstadoAceptacion = self._historialEstadosAceptacion[-1][0]

	def getUltimoLexemaValido(self):
		return self._historialEstadosAceptacion[-1][2]

	def getUltimoLexema(self):
		return self._ultimoLexema

class TokenReglas():

    #Constantes referentes a los token de las Reglas
    FLECHA = 10

    PUNTO_COMA = 20

    UNION = 30

    SIMBOLO = 40