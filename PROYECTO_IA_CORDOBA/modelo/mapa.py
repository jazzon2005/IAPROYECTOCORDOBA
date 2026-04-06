import config
from modelo.celda import Celda #Aquí ya empieza a brillar la modularidad xd

class Mapa:
    """Genera y gestiona la matriz 10x10 del terreno de Córdoba."""
    def __init__(self):
        self.filas = config.FILAS
        self.columnas = config.COLUMNAS
        self.cuadricula = []
        self._generar_mapa()

    def _generar_mapa(self):
        """Construye la matriz y asigna los tipos de terreno basados en config.py."""
        #1. Llenar la matriz con Celdas normales
        for f in range(self.filas):
            fila_actual = []
            for c in range(self.columnas):
                fila_actual.append(Celda(f, c))
            self.cuadricula.append(fila_actual)
        
        #2. Asignar los puntos de interés
        #Fundación (Inicio)
        f_ini, c_ini = config.INICIO_FUNDACION
        self.cuadricula[f_ini][c_ini].tipo = config.TIPO_INICIO

        #Restaurantes
        for r_f, r_c in config.RESTAURANTES:
            self.cuadricula[r_f][r_c].tipo = config.TIPO_RESTAURANTE

        #Comunidades (Metas)
        for m_f, m_c in config.COMUNIDADES:
            self.cuadricula[m_f][m_c].tipo = config.TIPO_META

        #Montañas (Obstáculos)
        for mt_f, mt_c in config.MONTANAS:
            self.cuadricula[mt_f][mt_c].tipo = config.TIPO_MONTANA

        #Ríos (Zonas de riesgo)
        for ri_f, ri_c in config.RIOS:
            self.cuadricula[ri_f][ri_c].tipo = config.TIPO_RIO

    def obtener_vecinos(self, celda): #Función de expansión
        """
        Retorna una lista de Celdas adyacentes a las que el dron puede moverse.
        Movimientos legales según el PDF: arriba, abajo, izquierda, derecha.
        """
        vecinos = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)] #Arriba, Abajo, Izquierda, Derecha

        for df, dc in direcciones:
            nf = celda.fila + df
            nc = celda.columna + dc

            #Verificar que no se salga de los límites del tablero
            if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                vecino = self.cuadricula[nf][nc]
                #Solo se agregan vecinos a los que físicamente se puede ir
                if vecino.es_transitable():
                    vecinos.append(vecino)
        
        return vecinos

    def obtener_celda(self, fila, columna):
        """Helper para obtener una celda de manera segura."""
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            return self.cuadricula[fila][columna]
        return None #Literalmente, se está diciendo que solo se puede mover dentro de los límites del mapa