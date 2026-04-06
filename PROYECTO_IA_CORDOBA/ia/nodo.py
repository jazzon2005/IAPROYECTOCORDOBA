class Nodo:
    """
    Representa un estado en el espacio de búsqueda del algoritmo A*.
    A diferencia de la 'Celda' (que es física), el 'Nodo' es la mente de la IA.
    """
    def __init__(self, celda, padre=None):
        self.celda = celda    #Objeto Celda (física) al que corresponde este nodo
        self.padre = padre    #Nodo del que venimos (crucial para reconstruir la ruta)
        
        #Valores matemáticos para A*
        self.g = 0            #Costo acumulado desde el inicio hasta aquí
        self.h = 0            #Heurística (distancia estimada hasta la meta)
        self.f = 0            #Costo total (g + h)

    def __lt__(self, otro):
        """
        Método mágico (Less Than) para que la cola de prioridad (heapq) 
        pueda ordenar los nodos automáticamente según su valor 'f'.
        """
        return self.f < otro.f
        
    def __eq__(self, otro):
        """Compara si dos nodos apuntan a la misma coordenada física."""
        return self.celda.fila == otro.celda.fila and self.celda.columna == otro.celda.columna