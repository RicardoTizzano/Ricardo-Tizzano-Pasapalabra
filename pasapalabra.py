"""
Esta aplicacion es como el PasaPalabra de la televisión
"""
import sys
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QDialog, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import numpy as np
import sqlite3
import random
import time

qtCreatorFile = "pasapalabra.ui" 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile) 

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    listaNombres=[]
    #abrir base de datos
    con = sqlite3.connect('diccionario.db')
    cur = con.cursor()
    totalJugadores = 1
    totalTiempo = 120
    letras ="ABCDEFGHIJLMNÑOPQRSTUVXYZ"
    comienzaCon = "0000000000000100100000110"
    
    def __init__(self): 
        QtWidgets.QMainWindow.__init__(self) 
        Ui_MainWindow.__init__(self) 
        self.setupUi(self) 
        self.setGraphicsEffect(None)
        
        self.wstart.hide()
        self.jugadorTurno = 0
        self.wjugadores.valueChanged.connect(self.cambiaJugadores)
        self.wtiempo.valueChanged.connect(self.cambiaTiempo)
        self.wsalir.clicked.connect(self.close)
        self.winicio.clicked.connect(self.iniciar)
        self.wstart.clicked.connect(self.start)
        
        self.wstart.hide()
        self.wpregunta.hide()
        self.wrespuestaL.hide()
        self.wtimer.hide()
        self.wrespuesta.hide()
        self.wmensaje.hide()
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000) # cada 1000 ms / 1 segundo
        self.timer.timeout.connect(self.actualizaTiempo)
        
        self.x, self.y  = self.estableceRueda()
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return or event.key() ==  QtCore.Qt.Key_Enter:
            self.responderClick()
            
    @QtCore.pyqtSlot()
    def actualizaTiempo(self):
        self.jugadores[self.jugadorTurno].tiempoRestante -=1
        self.wtimer.setText(str(self.jugadores[self.jugadorTurno].tiempoRestante))
        self.listaWTiempoL[self.jugadorTurno].setText(str(self.jugadores[self.jugadorTurno].tiempoRestante))
        if self.jugadores[self.jugadorTurno].tiempoRestante <= 0:
            self.mensaje("Tiempo agotado de " + self.jugadores[self.jugadorTurno].nombre,3, "rojo")
            self.seteoJugadorTurno()    
            self.mensaje("Turno de "+self.jugadores[self.jugadorTurno].nombre, 1,"rojo")
            self.start(True)
        self.repaint()
        
    @QtCore.pyqtSlot()
    def responderClick(self):  
        letra = self.jugadores[self.jugadorTurno].proximaLetra        

        if self.wrespuesta.text() !=   "":
            if self.wrespuesta.text() == self.jugadores[self.jugadorTurno].rosco[self.jugadores[self.jugadorTurno].proximaLetra][1] :
                # Respuesta correcta
                self.mensaje("Correcta!", 1,"verde")
                self.jugadores[self.jugadorTurno].rosco[self.jugadores[self.jugadorTurno].proximaLetra][0] = 1
                self.estableceColorFondoLetra( letra )
                self.jugadores[self.jugadorTurno].proximaLetra = self.fProximaLetra(False)
                if self.jugadores[self.jugadorTurno].proximaLetra == 99:
                    self.mensaje("Rosco Terminado !", 2,"rojo")
                    self.jugadores[self.jugadorTurno].tiempoRestante = 0
                    self.seteoJugadorTurno()    
            else:
                # Respuesta incorrecta
                self.wrespuestaL.setText(self.jugadores[self.jugadorTurno].rosco[self.jugadores[self.jugadorTurno].proximaLetra][1])
                self.mensaje("Incorrecta!", 1,"rojo")
                self.jugadores[self.jugadorTurno].rosco[self.jugadores[self.jugadorTurno].proximaLetra][0] = 2
                self.estableceColorFondoLetra( letra)
                self.jugadores[self.jugadorTurno].proximaLetra = self.fProximaLetra(False)
                if self.jugadores[self.jugadorTurno].proximaLetra == 99:
                    self.mensaje("Rosco Terminado !", 2,"rojo")
                    self.jugadores[self.jugadorTurno].tiempoRestante = 0
                
                self.seteoJugadorTurno()    
                self.mensaje("Turno de "+self.jugadores[self.jugadorTurno].nombre, 1,"rojo")
                
        else:
            # Respuesta Pasapalabra
            self.mensaje("Pasapalabra!", 1,"azul")
            self.jugadores[self.jugadorTurno].proximaLetra = self.fProximaLetra(True)
            self.seteoJugadorTurno()    
            self.mensaje("Turno de "+self.jugadores[self.jugadorTurno].nombre, 1,"rojo")
            
        self.start(True)
        
    def seteoJugadorTurno(self):
        self.jugadorTurno += 1
        if self.jugadorTurno > self.totalJugadores - 1:
            self.jugadorTurno = 0
        contador = 0    
        while self.jugadores[self.jugadorTurno].tiempoRestante <= 0 :
            self.jugadorTurno += 1
            contador += 1
            if contador > self.totalJugadores:
                # Todos los jugadores agotaron el tiempo
                self.finalDeJuego()
                break
            if self.jugadorTurno > self.totalJugadores - 1:
                self.jugadorTurno = 0

    def armaLetras(self, primerLetra, pasaPalabra):
        salida = ""
        
        if pasaPalabra == True:
            primerLetra += 1
            
        for l in range(primerLetra,25):
            if self.jugadores[self.jugadorTurno].rosco[l][0] == 0:
                salida += self.letras[l]
        for l in range(1,primerLetra):
            if self.jugadores[self.jugadorTurno].rosco[l][0] == 0:
                salida += self.letras[l]
        return salida
        
    def fProximaLetra(self, pasaPalabra):
        letras = self.armaLetras(self.jugadores[self.jugadorTurno].proximaLetra, pasaPalabra)
        encuentra = 0
        if pasaPalabra == True :
            encuentra = 0
        if letras == "":
            # Terminó con todas las letras
            return 99
        else:
            return self.letras.find(letras[encuentra])
            
    def iniciar(self):
        self.totalJugadores = self.wjugadores.value()                                                                                                                                                                                                                                                                                                                            
        totalTiempo = self.wtiempo.value()
        
        Dialog(self.totalJugadores, self.listaNombres)
        
        self.wjugadoresL.setText("Jugador")
        self.seteo_tablero_estetic(self.wjugadoresL, 50,30,230,61)
        
        self.wtiempoL.setText("Tiempo restante")
        self.seteo_tablero_estetic(self.wtiempoL, 330,30,140,61)
        
        self.jugadores=[]

        for i in range(self.totalJugadores):
            self.jugadores.append(Jugador(totalTiempo, self.listaNombres[i]))
        
        # funcion poneJugadores() muestra los jugadores en el tablero
        self.poneJugadores()
        self.wjugadores.hide()
        self.wtiempo.hide()
        self.winicio.hide()   
        self.wstart.show()
        
    def start(self, acertada):

        self.wstart.hide()
        self.wrespuesta.hide()
        self.wrespuesta.setFocus()
        self.wrespuesta.setText("")
        self.wrespuestaL.show()
        self.wpregunta.show()
        self.wtimer.show()
        self.wrespuesta.show()
        self.muestraRosco(self.jugadorTurno)
        self.parar= False
        self.wpregunta.setText(self.jugadores[self.jugadorTurno].rosco[self.jugadores[self.jugadorTurno].proximaLetra][2])
        if self.jugadores[self.jugadorTurno].rosco[self.jugadores[self.jugadorTurno].proximaLetra][3] == True:
            self.wrespuestaL.setText("contiene " + self.letras[(self.jugadores[self.jugadorTurno].proximaLetra)])
        else:
            self.wrespuestaL.setText(self.letras[(self.jugadores[self.jugadorTurno].proximaLetra)])
            
        self.timer.start()
        self.wtimer.setText(str(self.jugadores[self.jugadorTurno].tiempoRestante))
     
    def muestraRosco(self, jugador):
        self.listaLetras = []
        
        self.jugador = jugador
        for letra in range(25):
            self.listaLetras.append(QLabel(str(self.letras[letra]), self))
            self.listaLetras[letra].setGeometry(int(self.x[letra]), int(self.y[letra]), 35,35)
            self.listaLetras[letra].setFont(QFont('Noto Sans',16))
            self.estableceColorFondoLetra(letra)
            self.listaLetras[letra].setAlignment(QtCore.Qt.AlignCenter)
            self.listaLetras[letra].show()
        self.repaint()

    def estableceColorFondoLetra(self, letra):
        if self.jugadores[self.jugadorTurno].rosco[letra][0] == 0:
            # Fondo color verde
            self.listaLetras[letra].setStyleSheet(("background-color: rgb(27, 36, 224);"
                                        "color : rgb(255,255,255);"
                                        "border-radius: 17px;"
                                        "border : solid white;"
                                        "border-width : 2px 2px 2px 2px;"
                                        "font-weight: bold;"
                                        "border-color: rgb(255, 255, 255);"))
        else:
            # Fondo color azul
            if self.jugadores[self.jugadorTurno].rosco[letra][0] == 1:
                # Fondo color verde
                self.listaLetras[letra].setStyleSheet(("background-color: rgb(27, 224, 36);"
                                            "color : rgb(255,255,255);"
                                        "border-radius: 17px;"
                                        "border : solid white;"
                                        "border-width : 2px 2px 2px 2px;"
                                        "font-weight: bold;"
                                        "border-color: rgb(255, 255, 255);"))
            else:
                # Fondo color rojo
                self.listaLetras[letra].setStyleSheet(("background-color: rgb(224, 27, 36);"
                                            "color : rgb(255,255,255);"
                                            "border-radius: 17px;"
                                            "border : solid white;"
                                            "border-width : 2px 2px 2px 2px;"
                                            "font-weight: bold;"
                                            "border-color: rgb(255, 255, 255);"))
            
    def estableceRueda(self):
        num_segmentos = 25
        rad = 200
        cx = 800
        cy = 250

        angulo = np.linspace(0, 2*np.pi, num_segmentos+1)
        x = rad * np.cos(angulo) + cx
        y = rad * np.sin(angulo) + cy
        return x, y
        
    def poneJugadores(self):
        self.listaWNombresL=[]
        self.listaWTiempoL=[]
        for i in range(len(self.jugadores)):
            self.listaWNombresL.append(QLabel(self.jugadores[i].nombre, self))
            self.seteo_tablero_estetic(self.listaWNombresL[i], 50, (i * 50) + 150, 230, 35)
            
            self.listaWTiempoL.append(QLabel(str(self.jugadores[i].tiempoRestante), self))
            self.seteo_tablero_estetic(self.listaWTiempoL[i], 350, (i * 50) + 150, 120, 35)
            
    def seteo_tablero_estetic(self, widget, x,y,wx,wy):
        widget.setGeometry(x, y, wx, wy)
        widget.setFont(QFont('Noto Sans',18))
        widget.setStyleSheet("color : rgb(255,255,255);font-weight: bold;"
                            "padding: 2 px;"
                            "border-top-left-radius : 20px;"
                            "border-bottom-right-radius : 20px;")
        widget.setWordWrap(True);
        widget.setAlignment(QtCore.Qt.AlignCenter)
        widget.show()
                
    def cambiaJugadores(self):
        self.wjugadoresL.setText('Jugadores : ' + str(self.wjugadores.value()) )
        
    def cambiaTiempo(self):
        self.wtiempoL.setText('Tiempo : ' + str(self.wtiempo.value()) )
    
    def mensaje(self, mensaje, tiempo, color):
        self.wmensaje.setText( mensaje )
        if color == "azul":
            self.wmensaje.setStyleSheet(("background-color: rgb(27, 36, 224);"
                                            "color : rgb(255,255,255);"
                                            "border-top-left-radius : 15px;"
                                            "border-bottom-right-radius : 15px;"
                                            "border : solid white;"
                                            "border-width : 2px 2px 2px 2px;"
                                            "font-weight: bold;"
                                            "border-color: rgb(255, 255, 255);"))
        else:
            if color == "rojo":
                self.wmensaje.setStyleSheet(("background-color: rgb(224, 27, 36);"
                                                "color : rgb(255,255,255);"
                                                "border-top-left-radius : 15px;"
                                                "border-bottom-right-radius : 15px;"
                                                "border : solid white;"
                                                "border-width : 2px 2px 2px 2px;"
                                                
                                                
                                                "font-weight: bold;"
                                                "border-color: rgb(255, 255, 255);"))
            else:
                self.wmensaje.setStyleSheet(("background-color: rgb(27, 224, 36);"
                                                "color : rgb(255,255,255);"
                                                "border-top-left-radius : 15px;"
                                                "border-bottom-right-radius : 15px;"
                                                "border : solid white;"
                                                "border-width : 2px 2px 2px 2px;"
                                                "font-weight: bold;"
                                                "border-color: rgb(255, 255, 255);"))
        self.wmensaje.show()
        self.repaint()
        time.sleep(tiempo)
        self.wmensaje.hide()

    def finalDeJuego(self):
        self.mensaje("Fin del juego", 5, "rojo")
        sys.exit()
    

class Dialog(QDialog):
    listaWNombres = []
    listaWNombresL = []

    def __init__(self, totalJugadores, listaNombres):
        QDialog.__init__(self)
        self.setStyleSheet(("background-color: qlineargradient(spread:pad, x1:0.466, y1:0.483, x2:0.478, y2:0, stop:0 rgba(36, 59, 181, 255), stop:1 rgba(255, 255, 255, 255));"
                            "color : rgb(255,255,255);"
                            "border-top-left-radius : 20px;"
                            "border-bottom-right-radius : 20px;"
                            "border-width : 2px 2px 2px 2px;"
                            "font-weight: bold;"))
        

        self.totalJugadores = totalJugadores
        self.listaNombres = listaNombres
        
        self.setWindowTitle("Nombre de jugadores")
        self.setFixedSize(600, 600)
        self.setModal(True)
        boton = QPushButton('Grabar', self)
        boton.setGeometry(420,500,100,40)
        boton.setFont(QFont('Noto Sans',15))
        boton.setStyleSheet("font-weight: bold")
        
        
        boton.clicked.connect(self.grabaNombres)
        boton.show()
        
        for i in range(self.totalJugadores):
            self.listaWNombresL.append(QLabel('Jugador '+ str(i+1), self))
            self.listaWNombresL[i].setGeometry(50, (i * 50) + 200, 200, 35)
            self.listaWNombresL[i].setFont(QFont('Noto Sans',18))
            self.listaWNombresL[i].setStyleSheet("font-weight: bold")
            self.listaWNombresL[i].show()
            
            self.listaWNombres.append(QLineEdit(' ', self))                                                                                                                                      
            self.listaWNombres[i].setGeometry(300, (i * 50) + 200, 200, 35)
            self.listaWNombres[i].setFont(QFont('Noto Sans',18))
            self.listaWNombres[i].setStyleSheet("font-weight: bold")
            self.listaWNombres[i].show()
        self.listaWNombres[0].setFocus()
        self.exec_()

    def grabaNombres(self):
        for i in range(self.totalJugadores):
            MainWindow.listaNombres.append(self.listaWNombres[i].text().strip().capitalize())
        self.close()       

class Jugador():
    tiempoRestante = 0

    def __init__(self, tiempoRestante, nombre):
        self.tiempoRestante = tiempoRestante
        self.nombre = nombre
        self.rosco = {}
        self.proximaLetra = 0
        
        # rosco[{letra : [estado, pregunta, respuesta, contiene]}]
        # estado = 0 - Sin responder / 1 - Respondida correcta / 2 - Respondida incorrecta
        for letra in range(25):
            pregunta, respuesta , contiene = self.buscaPalabra(MainWindow.letras[letra], MainWindow.comienzaCon[letra])
            self.rosco[letra] = [0, pregunta, respuesta, contiene]
    
    def buscaPalabra(self, letra, comienzaCon):
        contiene = False
        if comienzaCon == '0':
            MainWindow.cur.execute("SELECT * FROM palabras WHERE substring(palabra,1,1) = ?", (letra.lower(),))
            resultado = MainWindow.cur.fetchall()
        else:
            MainWindow.cur.execute("SELECT * FROM palabras WHERE INSTR(palabra,?)", (letra.lower(),))
            resultado = MainWindow.cur.fetchall()
            contiene = True
            
        azar = random.randint(0,len(resultado)-1)
        resultadoAzar = resultado[azar]
        return resultadoAzar[0], resultadoAzar[1], contiene

if __name__ == "__main__": 
    app = QtWidgets.QApplication([]) 
    ventana = MainWindow()
    ventana.show() 
    app.exec_()