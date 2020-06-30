import PySimpleGUI as sg
from AnalizadorLexico import *
from AnalizadorSintactico import *
from GeneradorAutomatas import *

sg.theme('GreenTan')
btnSintactico = 'Analizar sintácticamente'
btnCadena = 'Analizar cadena'
txtInput= 'texto entrada'
txtSin = 'Caja de texto Sintac'
archivo = 'FILE'
ll1 = None


# STEP 1 define the layout
layout = [
		[
			sg.Text('Gramática para analizar'),
			sg.In(key=archivo),
			sg.FileBrowse(file_types=(("Archivos de texto plano", "*.txt"),))
		],

		[
        sg.Multiline(key=txtSin, default_text='', size=(100, 40)) #análisis sin
        ],

        [
			sg.Text('Analizar cadena'),
			sg.In(key=txtInput),
		],
        
        [
        	sg.Button(btnSintactico), sg.Button(btnCadena)
        ]
	]

#STEP 2 - create the window
window = sg.Window('My new window', layout, grab_anywhere=True)

# STEP3 - the event loop
while True:
	event, values = window.read()   # Read the event that happened and the values dictionary
	if event == sg.WIN_CLOSED:     # If user closed window with X or if user clicked "Exit" button then exit
		break
	elif event == btnSintactico:
		#Se limpia la caja con los resultados del sintáctico
		window[txtSin]('')
		if window[archivo].get() is not None and window[archivo].get() is not '':
			
			cadena = open(window[archivo].get(),'r').read()
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
				window[txtSin].Update(value='\n GRAMÁTICA RECONOCIDA\n', append=True)
				gramatica = sintactico.getGramaticaGenerada()

				window[txtSin].Update(value=gramatica.imprimirGramatica(), append=True)
				#gramatica.imprimirGramaticaConsola()

				window[txtSin].Update(value='\n AHORA SIN RECURSIÓN\n', append=True)

				gramatica.eliminarRecursionIzquierda()
				window[txtSin].Update(value=gramatica.imprimirGramatica(), append=True)
				#gramatica.imprimirGramaticaConsola()

				window[txtSin].Update(value='\n Simbolos terminales y no terminales\n', append=True)

				window[txtSin].Update(value=gramatica.getSimbolosNoTerminales(), append=True)
				window[txtSin].Update(value=gramatica.getSimbolosTerminales(), append=True)

				#window[txtSin].Update(value='\n FIRST de E\n', append=True)
				
				ll1 = AnalizadorSintacticoLL1(gramatica)
				#Verificando que funcionan el first y el follow :
				#resultado = ll1.first('E')
				#window[txtSin].Update(value=resultado, append=True)

				#window[txtSin].Update(value='\n FOLLOW de Tp\n', append=True)
				#resultado = ll1.follow('Tp')
				#window[txtSin].Update(value=resultado, append=True)

				window[txtSin].Update(value='\n Tabla LL1\n', append=True)
				window[txtSin].Update(value=ll1.crearTablaLL1(), append=True)

				#cadena = '(SorS)?°S+°S°S+°((SorS)°(SorS)?°S+)'
				#ll1.setCadena(cadena)
				#print('\n analisis de la cadena {}\n'.format(cadena))
				#valido,error = ll1.analizar()
				#print(valido)
				#print(error)

			else:
				window[txtSin].Update(value='ERROR!!!', append=True)

	elif event == btnCadena:

		if window[txtInput].get() is not None and ll1 is not None:
			cadena = window[txtInput].get() #'(SorS)?°S+°S°S+°((SorS)°(SorS)?°S+)'
			ll1.setCadena(cadena)
			valido,error = ll1.analizar()

			window[txtSin].Update(value='\n' + error, append=True)

window.close()