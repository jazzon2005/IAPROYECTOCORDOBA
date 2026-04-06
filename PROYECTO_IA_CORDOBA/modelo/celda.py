import config #Trae la configuración inicial para que sea super sencillo cambiar las cosas, y no quede hardcodeado como en el proyecto anterior
#Tomar en cuenta que esto no es la clase Nodo, alimentará a la clase Nodo, pero no lo es, es solamente para modularidad y escalabilidad
#Este código solo representa la información de una casilla en el mapa, más no las características del nodo como su padre, frontera, etc.

class Celda:
    def __init__(self, fila, columna):
        self.fila = fila
        self.columna = columna
        self.tipo = config.TIPO_NORMAL #Tipo inicial, se cambiará en runtime
        
        #Costo base exigido por el taller
        self.costo_base = 1
        
        #Variable para el algoritmo MINIMAX (el clima alterará esto)
        self.riesgo_inundacion = 0 

    def es_transitable(self):
        """Devuelve False si es una montaña, True para el resto."""
        return self.tipo != config.TIPO_MONTANA

    def obtener_costo_total(self):
        """Para el punto 2: El costo aumenta según el riesgo climático."""
        return self.costo_base + self.riesgo_inundacion