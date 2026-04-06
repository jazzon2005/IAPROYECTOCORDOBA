# --- DIMENSIONES DEL TABLERO ---
FILAS = 10
COLUMNAS = 10
TAMANO_CELDA = 60

# --- COLORES (RGB) ---
COLOR_FONDO = (40, 40, 40)
COLOR_LINEA = (200, 200, 200)
COLOR_INICIO = (50, 205, 50)     #Verde (Fundación)
COLOR_RESTAURANTE = (255, 165, 0) #Naranja (Puntos intermedios)
COLOR_META = (255, 20, 147)       #Rosa (Comunidades aisladas)
COLOR_MONTANA = (139, 69, 19)     #Café oscuro (Obstáculos)
COLOR_RIO = (65, 105, 225)        #Azul (Zonas de riesgo/inundación)
COLOR_NORMAL = (255, 255, 255)    #Blanco (Camino libre)

# --- TIPOS DE CELDA (Para lógica interna) ---
TIPO_NORMAL = 0
TIPO_INICIO = 1
TIPO_RESTAURANTE = 2
TIPO_META = 3
TIPO_MONTANA = 4
TIPO_RIO = 5

#1. El Dron inicia en el Norte (Montería) lejos del peligro inicial
INICIO_FUNDACION = (0, 1)

#2. Debe recoger suministros en el centro del mapa
RESTAURANTES = [(4, 4), (5, 5)]

#3. La meta final es una comunidad al Sur-Este
COMUNIDADES = [(9, 8)]

#4. Las montañas (Nudo del Paramillo) están al Sur-Oeste. 
#Son la fuente desde donde el clima empezará a expandir el agua.
MONTANAS = [(8, 0), (9, 0), (9, 1), (7, 0), (8, 1)]

#5. El Río cruza como una cicatriz. El clima desbordará estas casillas
#amenazando con aislar la esquina inferior derecha.
RIOS = [(7, 1), (7, 2), (7, 3), (7, 4), (8, 5), (8, 6), (9, 7)]

#Posiblemente luego los cambie por sprites xd

PROFUNDIDAD = 3 #Profundidad para el algoritmo de alfa poda beta