# -*- coding: utf-8 -*-
#@author: Lalo Valle

from AnalizadorLexico import *
from AnalizadorSintactico import *
from GeneradorAutomatas import *

import sys

rutaReglas = sys.argv[1]

with open(rutaReglas,'r') as archivo:
	cadena = archivo.read()

if cadena.find('\n'):
	cadena = cadena.replace('\n','')
if cadena.find(' '):
	cadena = cadena.replace(' ','')

tabular = ManejadorTabulares.recuperarTabular('TabularReglas.dat')

automata = ManejadorTabulares.generarAFDDeTabular(tabular)

lexico = AnalizadorLexico(automata, cadena)

sintactico = AnalizadorSintacticoReglas(lexico)

resultado = -1

valido = sintactico.analizar()

if valido:
	print('\n gramatica reconocida\n')
	gramatica = sintactico.getGramaticaGenerada()
	gramatica.imprimirGramaticaConsola()

	print('\n ahora sin recursión\n')

	gramatica.eliminarRecursionIzquierda()
	gramatica.imprimirGramaticaConsola()

	print('\n Simbolos terminales y no terminales\n')

	print(gramatica.getSimbolosNoTerminales())
	print(gramatica.getSimbolosTerminales())

	print('\n first de E\n')
	ll1 = AnalizadorSintacticoLL1(gramatica)
	resultado = ll1.first('E')
	print(resultado)
	print()

	print('\n follow de Tp\n')
	resultado = ll1.follow('Tp')
	print(resultado)
	print()

	print('\n tabla LL1\n')
	ll1.crearTablaLL1()

	cadena = '(SorS)?°S+°S°S+°((SorS)°(SorS)?°S+)'
	ll1.setCadena(cadena)
	print('\n analisis de la cadena {}\n'.format(cadena))
	valido,error = ll1.analizar()
	print(valido)
	print(error)

else:
	print('Error')