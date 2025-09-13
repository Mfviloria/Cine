from datetime import datetime, timedelta #para validar lo de la hora

# Variables globales para la ventana principal
info_peliculas = []
resultados = []
sillas = []
input_texto = ""
mostrar_input = False
seleccionadas = []
opcion = ""
botones = []
pago_mensaje = ""
boton_pagar = None
categoria_actual = "todos"  
x = 50
y = 175
w = 200
h = 250
current_image= None
imagen_fondo = None
borde = False
mostrar_pago = False
segunda_ventana = None 
sala_ventana = False
escogida = ""
transa = False
neq = False
efectivo = False
tarjeta = False
num = None
comprar = False
dulceria = False
mostrar_ganancias = False
boton_ganancias_area = {
    'x': 570.5, 
    'y': 170.3, 
    'w': 192.5, 
    'h': 258.5
}
ultima_actualizacion = 0
intervalo_actualizacion = 5000  

# Clase para la segunda ventana
class ManejoArchivo:
    def __init__(self, name):
        self.name = name
    
    def leer(self):
        archivo = open(self.name, "r")  # leer y escribir
        contenido = archivo.read()
        print("Contenido original:", contenido)
        
    def editar(self, posicion):
        archivo = open (self.name, "r")
        matriz = []
        for linea in archivo:
            matriz.append(linea.strip().split(","))
            
        for i in range(len(matriz)):
            for j in range(len(matriz[i])):
                if matriz[i][j] == posicion:
                    matriz[i][j] = "X"
                    
        archivo = open(self.name, "w")
        for fila in matriz:
            archivo.write(",".join(fila) + "\n")
        archivo.close()
        
    def recorrer(self):
        archivo = open(self.name, "r")
        matriz = []
        for linea in archivo:
            matriz.append(linea.strip().split(","))
            
        return matriz
 #----GANANCIAS----   
def calcular_ganancias():
    try:
        ganancias = {
            "Avengers: Endgame": 0,
            "Joker": 0,
            "Parasite": 0
        }
        total_sillas_ocupadas = 0  # Contador global de sillas ocupadas
        
        archivos_peliculas = [
            ("AvengersEndgame1530-1.txt", "Avengers: Endgame"),
            ("AvengersEndgame1800-2.txt", "Avengers: Endgame"),
            ("Joker1645-3.txt", "Joker"),
            ("Joker1915-1.txt", "Joker"),
            ("Parasite1730-2.txt", "Parasite"),
            ("Parasite2000-3.txt", "Parasite")
        ]
        
        for archivo, pelicula in archivos_peliculas:
            try:
                manejo = ManejoArchivo(archivo)
                matriz = manejo.recorrer()
                sillas_ocupadas = sum(fila.count("X") for fila in matriz)
                ganancias[pelicula] += sillas_ocupadas * 9500
                total_sillas_ocupadas += sillas_ocupadas
                
            except Exception as e:
                print("Error procesando {archivo}: {str(e)}")
                continue
        
        ganancia_total = sum(ganancias.values())
        total = [total_sillas_ocupadas, ganancia_total]
        return total
    except Exception as e:
        print("Error general en cálculo: {str(e)}")
        return 0, 0

#----DIBUJAR----
from time import strftime  # Asegúrate de tener esto al principio del archivo

def dibujar_ventana_ganancias():
    
    global ultima_actualizacion
    
    # Actualizar solo si ha pasado el intervalo
    if millis() - ultima_actualizacion > intervalo_actualizacion:
        ultima_actualizacion = millis()
    
    # Obtener datos actualizados
    ganancias, total = calcular_ganancias()
    
    fill(240, 240, 250)
    stroke(100)
    strokeWeight(2)
    rect(200, 100, 400, 250, 15)
    
    fill(50, 70, 150)
    textSize(24)
    textAlign(CENTER)
    text("REPORTE DE GANANCIAS", 400, 140)
    
    fill(100)
    textSize(12)
    text("Actualizado: ", 400, 170)
    
    stroke(200)
    line(220, 190, 580, 190)
    
    # Datos de películas
    textSize(16)
    textAlign(LEFT)
    fill(0)
    y_pos = 220
    
    total = calcular_ganancias()
    fill(50, 150, 50)
    textSize(20)
    text("NÚMERO DE PERSONAS: ", 220, 178 + 40)
    text(str(total[0]), 480, 178+40)
    stroke(150)
    line(220, y_pos + 10, 580, y_pos + 10)
    fill(50, 150, 50)
    textSize(20)
    text("GANANCIA TOTAL: ", 220, y_pos + 40)
    text(str(total[1]), 420, y_pos+40)
    
    
    fill(200, 80, 80)
    rect(350, y_pos + 70, 100, 40, 10)
    fill(255)
    textSize(16)
    textAlign(CENTER, CENTER)
    text("CERRAR", 400, y_pos + 90)
   
        
class SegundaVentana:
    def __init__(self):
        self.ventana = createGraphics(600, 600)
        self.info_peliculas = ["Avengers: Endgame, 15:30, Sala 1", 
                      "Avengers: Endgame, 18:00, Sala 2",
                      "Joker, 13:45, Sala 3",
                      "Joker, 19:15, Sala 1",
                      "Parasite, 17:30, Sala 2",
                      "Parasite, 20:00, Sala 3"]
        self.escogida = ""
        self.botones = []
        self.boton_pagar = None
        self.pago_mensaje = ""
        self.mostrar_input = False
        self.input_texto = ""
        self.categoria_actual = "todos"
        self.opcion = ""
        self.activa = True
        self.escogida = ""
        # Inicializar botones
        self.cargarTodosLosDatos()
    
    def cargarTodosLosDatos(self):
        self.botones = []
        for linea in self.info_peliculas:
            self.botones.append(BotonResultado(linea, 30, 0))
    
    def es_horario_valido(self, horario):
        try:            
            if len(horario) != 5 or horario[2] != ":":
                return False
            horas = int(horario[:2])
            minutos = int(horario[3:])
            return 0 <= horas < 24 and 0 <= minutos < 60
        except:
            return False 
    
    def aplicarFiltro(self, dato):
        self.botones = []  # Limpiar botones anteriores
        # Validar que el dato de filtro no esté vacío
        if not dato.strip():
            print("Debe ingresar un criterio de búsqueda")
            self.pago_mensaje = "Debe ingresar un criterio de búsqueda"
            return
        
        if self.categoria_actual == "pelicula" and dato.strip().isdigit():
            self.pago_mensaje = ""
            return 
        
        # Validar filtro de horario
        if self.categoria_actual == "horario":
            # Verificar si es un formato de hora válido (ej: "14:30")
            if not self.es_horario_valido(dato.strip()):
                self.pago_mensaje = "Error: Ingrese un horario válido (ej: 14:30)."
                return 
            
        indice = 0
        if self.categoria_actual == "pelicula":
            indice = 0
        elif self.categoria_actual == "horario":
            indice = 1
        elif self.categoria_actual == "sala":
            indice = 2
        
        for linea in self.info_peliculas:
            partes = linea.strip().split(",")
            if len(partes) > indice:
                valor = partes[indice].strip().lower()
                if dato.strip().lower() in valor:
                    self.botones.append(BotonResultado(linea, 30, 0))
    
    def dibujar(self):
        
        if not self.activa:
            return
            
        self.ventana.beginDraw()
        self.ventana.background(232, 218, 239)
        
        # Título
        self.ventana.fill(0)
        self.ventana.textSize(18)
        self.ventana.textAlign(CENTER, TOP)
        self.ventana.text("Sistema de Información de Cine", self.ventana.width/2, 10)
        self.ventana.textSize(14)
        
        # Botones de filtro con mejor diseño
        self.ventana.fill(144, 107, 231)
        if self.categoria_actual == "pelicula":
            self.ventana.fill(170, 148, 223)  # Resaltar botón activo
        self.ventana.rect(30, 50, 100, 30, 5)
        
        self.ventana.fill(144, 107, 231)
        if self.categoria_actual == "horario":
            self.ventana.fill(170, 148, 223)  # Resaltar botón activo
        self.ventana.rect(140, 50, 100, 30, 5)
        
        self.ventana.fill(144, 107, 231)
        if self.categoria_actual == "sala":
            self.ventana.fill(170, 148, 223)  # Resaltar botón activo
        self.ventana.rect(250, 50, 100, 30, 5)
        
        self.ventana.fill(144, 107, 231)
        if self.categoria_actual == "todos":
            self.ventana.fill(170, 148, 223)  # Resaltar botón activo
        self.ventana.rect(360, 50, 100, 30, 5)
        
        self.ventana.fill(255)
        self.ventana.textAlign(CENTER, CENTER)
        self.ventana.text("Película", 80, 65)
        self.ventana.text("Horario", 190, 65)
        self.ventana.text("Sala", 300, 65)
        self.ventana.text("Todos", 410, 65)
        
        
        # Cuadro de texto para filtrar
        if self.mostrar_input:
            self.ventana.fill(255)
            self.ventana.rect(30, 90, 300, 30)
            self.ventana.fill(0)
            self.ventana.textAlign(LEFT, CENTER)
            self.ventana.text(self.input_texto, 35, 105)
            
            # Instrucción
            self.ventana.fill(100)
            self.ventana.textAlign(LEFT, CENTER)
            self.ventana.text("Presiona ENTER para filtrar", 340, 105)
        
        # Encabezados de columnas
        self.ventana.fill(50)
        self.ventana.textAlign(LEFT, CENTER)
        self.ventana.text("PELÍCULA", 40, 130)
        self.ventana.text("HORARIO", 210, 130)
        self.ventana.text("SALA", 330, 130)
        
        # Línea separadora
        self.ventana.stroke(100)
        self.ventana.line(30, 145, 430, 145)
        self.ventana.noStroke()
        
        # Dibujar resultados como botones
        y_offset = 160
        for boton in self.botones:
            boton.y = y_offset
            self.dibujarBoton(boton)
            y_offset += 40
        
        # Botón pagar
        if self.boton_pagar != None:
            self.dibujarBotonPagar(self.boton_pagar)
        
        # Mensaje de pago
        if self.pago_mensaje != "":
            self.ventana.fill(0, 150, 0)
            self.ventana.textAlign(CENTER, CENTER)
            self.ventana.text(self.pago_mensaje, self.ventana.width/2, self.ventana.height - 30)
        
        self.ventana.endDraw()
        image(self.ventana, 0, 0)
    
    def dibujarBoton(self, boton):
        # Fondo del botón
        if boton.seleccionado:
            self.ventana.fill(200, 230, 255)
        else:
            self.ventana.fill(255)
        self.ventana.rect(boton.x, boton.y, boton.w, boton.h)
        
        # Texto con información estructurada
        self.ventana.fill(0)
        self.ventana.textAlign(LEFT, CENTER)
        
        # Mostrar información según el formato: Película | Horario | Sala
        self.ventana.text(boton.pelicula, boton.x + 10, boton.y + boton.h / 2)
        self.ventana.text(boton.horario, boton.x + 180, boton.y + boton.h / 2)
        self.ventana.text(boton.sala, boton.x + 300, boton.y + boton.h / 2)
    
    def dibujarBotonPagar(self, boton):
        self.ventana.fill(82, 137, 201)
        self.ventana.rect(boton.x, boton.y, boton.w, boton.h)
        self.ventana.fill(255)
        self.ventana.textAlign(CENTER, CENTER)
        self.ventana.text("Pagar", boton.x + boton.w / 2, boton.y + boton.h / 2)
    
    
    
        
    def manejarClick(self, mx, my):
        global sala_ventana, escogida
        if not self.activa:
            return
        
        # Verifica si se presiona un filtro
        if 30 <= mx <= 130 and 50 <= my <= 80:
            self.opcion = "pelicula"
            self.categoria_actual = "pelicula"
            self.mostrar_input = True
            self.input_texto = ""
        elif 140 <= mx <= 240 and 50 <= my <= 80:
            self.opcion = "horario"
            self.categoria_actual = "horario"
            self.mostrar_input = True
            self.input_texto = ""
        elif 250 <= mx <= 350 and 50 <= my <= 80:
            self.opcion = "sala"
            self.categoria_actual = "sala"
            self.mostrar_input = True
            self.input_texto = ""
        elif 360 <= mx <= 460 and 50 <= my <= 80:
            self.categoria_actual = "todos"
            self.mostrar_input = False
            self.cargarTodosLosDatos()
            self.boton_pagar = None
        
        # Verifica si se clickeó un resultado
        for i, boton in enumerate(self.botones):
            if boton.fueClickeado(mx, my):
                # Deseleccionar todos los botones
                for b in self.botones:
                    b.seleccionado = False
                
                # Seleccionar el botón clickeado
                boton.seleccionado = True
                print("Seleccionado: " + boton.texto)
                escogida = boton.texto.strip().split(",")
                
                # Validar el tiempo antes de permitir la selección
                try:
                    hora_pelicula_str = escogida[1].strip()
                    hora_pelicula = datetime.strptime(hora_pelicula_str, "%H:%M")
                    hora_actual = datetime.now()
                    
                    # Combinar con fecha actual para comparación correcta
                    hora_pelicula = hora_pelicula.replace(
                        year=hora_actual.year,
                        month=hora_actual.month,
                        day=hora_actual.day
                    )
                    
                    # Calcular diferencia en minutos
                    diferencia = (hora_actual - hora_pelicula).total_seconds() / 60
                    
                    if diferencia > 30:  # Más de 30 minutos después del inicio
                        print("No se pueden comprar entradas. La película comenzó a las " + hora_pelicula_str + 
                              " (hace " + str(int(diferencia)) + " minutos).")
                        self.pago_mensaje = "La función comenzó hace " + str(int(diferencia)) + " minutos. No se pueden comprar entradas."
                        self.boton_pagar = None 
                        return
                    elif diferencia < 0:  # Película es en el futuro
                        print("La película comenzará a las " + hora_pelicula_str + 
                              " (en " + str(-int(diferencia)) + " minutos).")
                    else:
                        print("Película en curso. Comenzó a las " + hora_pelicula_str + 
                              " (hace " + str(int(diferencia)) + " minutos).")
                except Exception as e:
                    print("Error al validar horario: " + str(e))
                    self.pago_mensaje = "Error al validar el horario de la función"
                    return
                
                # Si pasa la validación, mostrar botón de pagar
                self.boton_pagar = BotonPagar(boton.x + 420, boton.y)
                self.pago_mensaje = ""  # Limpiar mensaje anterior
                crearSillas(boton.texto.strip().split(","))
                return
        
        # Verifica si se presionó pagar
        if self.boton_pagar != None and self.boton_pagar.fueClickeado(mx, my):
            try:
                hora_pelicula_str = escogida[1].strip()
                hora_pelicula = datetime.strptime(hora_pelicula_str, "%H:%M")
                hora_actual = datetime.now()
                
                hora_pelicula = hora_pelicula.replace(
                    year=hora_actual.year,
                    month=hora_actual.month,
                    day=hora_actual.day
                )
                
                diferencia = (hora_actual - hora_pelicula).total_seconds() / 60
                
                if diferencia > 30:
                    self.pago_mensaje = "No se puede acceder: La película ya comenzó hace más de 30 minutos"
                    print(self.pago_mensaje)
                    return
                    
            except Exception as e:
                self.pago_mensaje = "Error al validar horario: " + str(e)
                print(self.pago_mensaje)
                return
            
            sala_ventana = True
            print(self.pago_mensaje)
    
    def manejarTecla(self, k):
        if not self.activa:
            return
            
        if self.mostrar_input:
            if k == BACKSPACE and len(self.input_texto) > 0:
                self.input_texto = self.input_texto[:-1]
            elif k == ENTER:
                self.mostrar_input = False
                self.aplicarFiltro(self.input_texto)
                self.boton_pagar = None
            elif k != CODED and len(str(k)) == 1:  # Solo caracteres imprimibles
                self.input_texto += str(k)
                
# Clase para representar los botones de resultados
class BotonResultado:
    def __init__(self, texto, x, y):
        self.texto = texto
        self.x = x
        self.y = y
        self.w = 400
        self.h = 30
        self.seleccionado = False
        
        # Separar la información para mostrarla mejor
        partes = texto.strip().split(",")
        if len(partes) >= 3:
            self.pelicula = partes[0].strip()
            self.horario = partes[1].strip()
            self.sala = partes[2].strip()
        else:
            self.pelicula = texto
            self.horario = ""
            self.sala = ""

    def fueClickeado(self, mx, my):
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

# Clase para el botón de pagar
class BotonPagar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 100
        self.h = 30

    def fueClickeado(self, mx, my):
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h


def setup():
    global imagen_fondo, Sala, Silla, esc, ocu, sillas, pagos, efect, card, nequi, num, dulces
    size(800, 600)
    textSize(14)
    imagen_fondo = loadImage("Cinema.png")
    imagen_fondo.resize(800, 600)
    Sala = loadImage("Sala.png")
    Sala.resize(800,600)
    Silla= loadImage("silla.png")
    Silla.resize(100,100)
    ocu= loadImage("ocupada.png")
    ocu.resize(100,100)
    esc = loadImage("escogido.png")
    esc.resize(45,45)
    global fuente
    fuente = createFont("Segoe UI Semibold", 16)
    textFont(fuente)
    dulces = loadImage("Dulces.png")
    dulces.resize(800,600)
    
def crearSillas(esc):
    global escogida
    """
peliculas = ["Avengers: Endgame, 15:30, Sala 1", 
                      "Avengers: Endgame, 18:00, Sala 2",
                      "Joker, 16:45, Sala 3",
                      "Joker, 19:15, Sala 1",
                      "Parasite, 17:30, Sala 2",
                      "Parasite, 20:00, Sala 3"]
    """
    global sillas, segunda_ventana
    print("Escogido: "+ str(escogida[2]))
    sillas = []
    
    chairs = None
    
    if esc[0] == "Avengers: Endgame" and esc[1] == " 15:30" and esc[2] == " Sala 1":
        chairs = ManejoArchivo("AvengersEndgame1530-1.txt")
    elif esc[0] == "Avengers: Endgame" and esc[1] == " 18:00" and esc[2] == " Sala 2":
        chairs = ManejoArchivo("AvengersEndgame1800-2.txt")
    elif esc[0] == "Joker" and esc[1] == " 13:45" and esc[2] == " Sala 3":
        chairs = ManejoArchivo("Joker1645-3.txt")
    elif esc[0] == "Joker" and esc[1] == " 19:15" and esc[2] == " Sala 1":
        chairs = ManejoArchivo("Joker1915-1.txt")
    elif esc[0] == "Parasite" and esc[1] == " 17:30" and esc[2] == " Sala 2":
        chairs = ManejoArchivo("Parasite1730-2.txt")
    elif esc[0] == "Parasite" and esc[1] == " 20:00" and esc[2] == " Sala 3":
        chairs = ManejoArchivo("Parasite2000-3.txt")
        
        
    #chairs = ManejoArchivo("AvengersEndgame1800-2.txt")    
    matriz = chairs.recorrer() 
    
    for j in range(400, 14, -58):  
        for i in range(255, 758, 58):  
            if i != 487:  
                fila = (j - 14) // 58  
                columna = (i - 255) // 58  
                if fila < len(matriz) and columna < len(matriz[fila]):
                    tipo = matriz[fila][columna]  
                    sillas.append(SillaCine(i, j, tipo)) 


def draw():
    global borde, segunda_ventana, sala_ventana, current_image,sillas,Sala, dulceria, dulces, seleccionadas, pagos, transa, efect, neq, card, efectivo, tarjeta, dulces
    global mostrar_ganancias
    if sala_ventana:
        pago= False
        image(Sala, 0, 0)
        
    
    elif segunda_ventana and segunda_ventana.activa:
        segunda_ventana.dibujar()
   
    else:
        image(imagen_fondo, 0, 0)
        
    
    # Si la segunda ventana está activa, mostrarla
    if segunda_ventana is not None and segunda_ventana.activa:
        segunda_ventana.dibujar()
        if sala_ventana:
            #Ventana para reservar asientos
            salaVentana()
            
    else:
        # Dibujar la ventana principal
        background(240)
        
        # Dibujar imagen de fondo
        image(imagen_fondo, 0, 0)
        noFill()
        rect(550, 175,200,250)
        # Detectar si el mouse está sobre el botón invisible
        borde = x < mouseX < x + w and y < mouseY < y + h
        
        # Opcional: dibujar un borde cuando el mouse está encima (solo para pruebas)
        if borde:
            noFill()
            stroke(255, 0, 0)
            rect(x, y, w, h)
            noStroke()
            
    if mostrar_ganancias:
        dibujar_ventana_ganancias()
        
    if dulceria: 
        image(dulces,0,0)
        
    """
    if False:
        noFill()
        stroke(255, 0, 0, 150)
        strokeWeight(1)
        rect(boton_ganancias_area['x'], boton_ganancias_area['y'], 
             boton_ganancias_area['w'], boton_ganancias_area['h'])
    """

"""
    image(esc, 280,422)
    image(esc,340,422)
    image(esc, 745,422)
    image(esc, 280, 72)
    image(esc, 745,72)
"""

class SillaCine():
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.seleccionado = False
        self.ancho = 50
        self.alto = 58
    
    def mostrar(self):
        global esc, ocu, Silla
        if self.tipo == "X":  # Si está ocupada, muestra la imagen ocupada
            image(ocu, self.x, self.y)
        elif self.seleccionado:  # Si está seleccionada, muestra la imagen seleccionada
            image(esc, self.x + 28, self.y + 24)
        else:  # Si no está seleccionada, muestra la imagen normal
            image(Silla, self.x, self.y)
        
    def fueClickeada(self, mx, my):
        if self.tipo != "X":  # Solo se puede seleccionar si no es "X"
            return (self.x + 25 <= mx <= self.x + self.ancho + 10 and
                    self.y <= my <= self.y + self.alto)
        return False
    
    def estado(self):
        if self.tipo != "X":  
            self.seleccionado = not self.seleccionado
    
    def getestado(self):
        return self.seleccionado
    
    def type(self):
        self.tipo = "X"
        
        

def pago():
    global seleccionadas
    
    fill(255)
    stroke(0)
    rect(200, 150, 320, 200, 20)  # Rectángulo del cuadro de pago
    
    # Mensaje principal
    fill(0)
    textSize(14)
    textAlign(CENTER, CENTER)
    
    if seleccionadas:
        mensaje = "Número de sillas escogidas: " + str(len(seleccionadas)) + "."
        mensaje2 = "Valor a cancelar: " + str(len(seleccionadas)*9000) + " pesos colombianos."
        text(mensaje, 360, 200)
        text(mensaje2, 360, 230)
        
        fill(180)
        rect(310, 280, 100, 30, 10)  # Botón "Pagar"
        fill(0)
        text("Pagar", 360, 295)
    else:
        mensaje = "No hay sillas seleccionadas."
        text(mensaje, 360, 200) 
    
    fill(180)
    rect(210, 160, 50, 30, 10)  # Botón "Volver"
    fill(0)
    text("Volver", 235, 175)

            
def salaVentana():
    
    global Sala, Silla, sillas, seleccionadas, esc
    image(Sala,0,0)
    
    noFill()
    if sala_ventana and mouseX>=12 and mouseX<=148 and mouseY>=11 and mouseY<=43:
        stroke(0)
        strokeWeight(2)
        rect(12,10,136,32,20)
    if sala_ventana and mouseX>=12 and mouseX<=197+12 and mouseY>=555 and mouseY<=555+32:
        stroke(0)
        strokeWeight(2)
        rect(12,555,197,32,20)
        
    
    """
    image(Silla, 270,400)
    image(Silla, 700,400)
    image(Silla, 270,50)
    image(Silla, 700,50)
    """
    
    stroke(0)
    #rect(279,421,50,58)
    for silla in sillas:
        silla.mostrar()
        
    columnas = 5
    filas = 3
    ancho_col = 70
    alto_fila = 20
    inicio_x = 40
    inicio_y = 410
        
    fill(0)          
    noStroke()
    textSize(14)
    for idx, etiqueta in enumerate(seleccionadas[:columnas * filas]):
        col = idx % columnas
        fila = idx // columnas
        x = inicio_x + col *ancho_col*0.5 
        y = inicio_y + 40 + fila * alto_fila
        text(etiqueta, x, y)
    
    if mostrar_pago:
        pago()
        
    
def mousePressed():
    global segunda_ventana, sala_ventana, current_image, esc, Silla, seleccionadas, sillas, mostrar_pago, comprar, mostrar_ganancias, dulceria, ultima_actualizacion
    """
    if 560 <= mouseX <= 580 and 160 <= mouseY <= 180:
        mostrar_ganancias = not mostrar_ganancias
        return
    """
    #boton = boton_ganancias_area
    #550, 175,200,250)
    
    
    # Si la ventana está abierta, verificar clic en "CERRAR"
    if sala_ventana != True and mostrar_ganancias != True and segunda_ventana == None and mouseX >= 300 and mouseX <= 500 and mouseY >= 175 and mouseY<= 175+250:
        dulceria = True
        
    if dulceria and sala_ventana != True  and mouseX >= 10 and mouseX <= 10+135 and mouseY >= 12 and mouseY<= 12+30:
        dulceria = False
    
    if mostrar_ganancias and dulceria != True and sala_ventana != True and mouseX >= 350 and mouseX <= 350+70 and mouseY >= 220 and mouseY<= 220+40:
        mostrar_ganancias = False
        seleccionadas = []
        for silla in sillas:
            if silla.getestado():
                silla.estado()
        
        image(imagen_fondo, 0, 0)
        segunda_ventana.activa = False
    
        
            
    if sala_ventana != True  and mouseX >= 550 and mouseX <= 550+200 and mouseY >= 175 and mouseY<= 175+200:
        mostrar_ganancias = True
        #300-500, 175-175+250

    elif sala_ventana:
        if 12 <= mouseX <= 148 and 10 <= mouseY <= 43:
            sala_ventana = False
            mostrar_pago = False
            
            for silla in sillas:
                if silla.getestado():
                    silla.estado()
                    
            seleccionadas = []
            background(240)
            image(imagen_fondo, 0, 0)
    
            borde = x < mouseX < x + w and y < mouseY < y + h
            if borde:
                
                noFill()
                stroke(255, 0, 0)
                rect(x, y, w, h)
                noStroke()
    
            segunda_ventana.activa = True
            return
        
        elif mouseX>=12 and mouseX<=197+12 and mouseY>=555 and mouseY<=555+32:
            mostrar_pago = True
            #310, 280, 100, 30, 10
            
        elif mostrar_pago and mouseX>=310 and mouseX<= 310+100 and mouseY<= 280+30 and mouseY >= 280:
            global escogida
        
            mostrar_pago = False
            
            if escogida[0] == "Avengers: Endgame" and escogida[1] == " 15:30" and escogida[2] == " Sala 1":
                archivo = ManejoArchivo("AvengersEndgame1530-1.txt")
            elif escogida[0] == "Avengers: Endgame" and escogida[1] == " 18:00" and escogida[2] == " Sala 2":
                archivo = ManejoArchivo("AvengersEndgame1800-2.txt")
            elif escogida[0] == "Joker" and escogida[1] == " 16:45" and escogida[2] == " Sala 3":
                archivo = ManejoArchivo("Joker1645-3.txt")
            elif escogida[0] == "Joker" and escogida[1] == " 19:15" and escogida[2] == " Sala 1":
                archivo = ManejoArchivo("Joker1915-1.txt")
            elif escogida[0] == "Parasite" and escogida[1] == " 17:30" and escogida[2] == " Sala 2":
                archivo = ManejoArchivo("Parasite1730-2.txt")
            elif escogida[0] == "Parasite" and escogida[1] == " 20:00" and escogida[2] == " Sala 3":
                archivo = ManejoArchivo("Parasite2000-3.txt")
                
            letras_filas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            fila_index = 0
        
            for silla in sillas:
                if silla.getestado(): 
                    fila = (421 - silla.y) // 58
                
                    if silla.x < 511:
                        col = (silla.x - 279) // 58 + 2
                    else:
                        col = (silla.x - 279 - 58) // 58 + 2
                            
                    seleccion = letras_filas[fila] + str(col)
                    archivo.editar(seleccion)
                    silla.type()
                    #(210, 160, 50, 30, 10)
            
            for silla in sillas:
                if silla.getestado():
                    silla.estado()
            
            delay(2000)
            sala_ventana = False
            mostrar_pago = False
            seleccionadas = []
            for silla in sillas:
                if silla.getestado():
                    silla.estado()
        
            image(imagen_fondo, 0, 0)
            segunda_ventana.activa = False
            
        elif mostrar_pago and mouseX>=210 and mouseX<= 310+50 and mouseY<= 160+30 and mouseY >= 160:
            mostrar_pago = False
    
        # Si se hace clic en la matriz de sillas
        elif mouseX >= 279 and mouseX <= 801 and mouseY >= 15 and mouseY <= 479:
            letras_filas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            
            for silla in sillas:
                if silla.fueClickeada(mouseX, mouseY):
                    # Calculamos la fila
                    fila = (421 - silla.y) // 58 
            
                    # Calculamos la columna
                    if silla.x < 511:
                        col = (silla.x - 279) // 58 + 2
                    else:
                        col = (silla.x - 279 - 58) // 58 + 2
            
                    seleccion = letras_filas[fila] + str(col)
            
                    if silla.getestado():  
                        silla.estado()
                        if seleccion in seleccionadas:
                            seleccionadas.remove(seleccion)
                    else:  
                        if len(seleccionadas) < 15:
                            silla.estado()
                            seleccionadas.append(seleccion)
                        else:
                            print("¡Límite de 15 sillas alcanzado!")
                    
                    print("Fila:", letras_filas[fila], ", Columna:", col)
            
        
            
    elif segunda_ventana is not None and segunda_ventana.activa:
        segunda_ventana.manejarClick(mouseX, mouseY)
            
    
    else:
        if x < mouseX < x + w and y < mouseY < y + h:
            print("¡Botón invisible presionado!")
            segunda_ventana = SegundaVentana()
    
def keyPressed():
    global segunda_ventana

    # Si la segunda ventana está activa, manejar teclas en ella
    if segunda_ventana is not None and segunda_ventana.activa:
        segunda_ventana.manejarTecla(key)

# Función para cerrar la segunda ventana (puedes agregar un botón para esto)
def cerrarSegundaVentana():
    global segunda_ventana
    if segunda_ventana is not None:
        segunda_ventana.activa = False
        segunda_ventana = None
        
def dibujarBotonSalir(self, boton):
        self.ventana.fill(0, 200, 100)
        self.ventana.rect(450, 550, boton.w, boton.h)
        self.ventana.fill(255)
        self.ventana.textAlign(CENTER, CENTER)
        self.ventana.text("Salir", 450 + boton.w / 2, 550 + boton.h / 2)

# Verifica si se presiona Salir
        if 450 <=mx<= 450+boton.w/2 and 550 <= my <= 550+boton.h/2:
            cerrarSegundaVentana()
