import heapq
from ia.nodo import Nodo

class BuscadorAEstrella:
    def __init__(self, mapa):
        self.mapa = mapa #Recibe el mapa que ya creamos para saber por dónde moverse

    def distancia_manhattan(self, celda_a, celda_b):
        """
        Heurística exigida por el taller. 
        Calcula la distancia en 'L' (cuadras) ignorando obstáculos.
        """
        return abs(celda_a.fila - celda_b.fila) + abs(celda_a.columna - celda_b.columna) #|x1-x2| + |y1-y2|

    def buscar_ruta_entre_dos_puntos(self, inicio_celda, meta_celda):
        """
        Implementación del pseudocódigo de BÚSQUEDA EN GRAFOS para A*.
        Encuentra la ruta óptima entre un punto A y un punto B.
        """
        nodo_inicio = Nodo(inicio_celda) #Punto A
        nodo_meta = Nodo(meta_celda) #Punto B

        #La "Frontera" (Lista Abierta). Se usa la libreria heapq para que siempre el de menor 'f' salga primero.
        #Básicamente esta libreria lo que hace es crear una lista autosorteable (se organiza sola en cada llamada)
        lista_abierta = []
        heapq.heappush(lista_abierta, nodo_inicio)

        #El "Conjunto de Explorados" (Lista Cerrada) para evitar bucles infinitos (Búsqueda en Grafos).
        #Se guardan tuplas (fila, columna) porque son más rápidas de buscar.
        lista_cerrada = set()

        historial_exploracion = [] #Funciona como una lista de visitados para el paso a paso, útil para animar en la GUI
        paso = 1 #Pasos dados

        print(f"\n--- EXPLORANDO RUTA DE ({inicio_celda.fila},{inicio_celda.columna}) A ({meta_celda.fila},{meta_celda.columna}) ---")
        print(f"{'PASO':<5} | {'NODO':<8} | {'PADRE':<8} | {'ACCION':<10} | {'COSTO':<5} | FRONTERA")
        print("-" * 80) #Este print y el que se muestra más adelante solamente muestran como está pensando la IA con propositos de realizar el informe

        while lista_abierta: #Siempre que existan nodos a explorar...
            #1. Extraer el nodo con menor f(n)
            nodo_actual = heapq.heappop(lista_abierta)

            str_nodo = f"({nodo_actual.celda.fila},{nodo_actual.celda.columna})"
            str_padre = f"({nodo_actual.padre.celda.fila},{nodo_actual.padre.celda.columna})" if nodo_actual.padre else "None" #Información para los print de más adelante

            #Calcular la acción tomada comparando con el padre
            accion = "Inicio"
            if nodo_actual.padre:
                df = nodo_actual.celda.fila - nodo_actual.padre.celda.fila
                dc = nodo_actual.celda.columna - nodo_actual.padre.celda.columna
                if df == -1: accion = "Arriba"
                elif df == 1: accion = "Abajo"
                elif dc == -1: accion = "Izquierda"
                elif dc == 1: accion = "Derecha" #Principalmente para mostrar en el print mas adelante, no tiene efecto real sobre el algoritmo
                
            frontera_visual = [f"({n.celda.fila},{n.celda.columna})" for n in lista_abierta]
            str_frontera = str(frontera_visual)[:30] + "..." if len(frontera_visual) > 3 else str(frontera_visual)
            
            # Imprimir el estado mental del dron con el nuevo formato
            print(f"{paso:<5} | {str_nodo:<8} | {str_padre:<8} | {accion:<10} | {nodo_actual.f:<5} | {str_frontera}")
            
            #Se guarda la celda para que Pygame la anime paso a paso
            historial_exploracion.append(nodo_actual.celda)
            paso += 1

            #2. Prueba de Meta
            if nodo_actual.celda.fila == nodo_meta.celda.fila and nodo_actual.celda.columna == nodo_meta.celda.columna:
                #Reconstruir la ruta yendo hacia atrás a través de los padres
                ruta = []
                actual = nodo_actual
                while actual is not None:
                    ruta.append(actual.celda)
                    actual = actual.padre
                return ruta[::-1], historial_exploracion #Se invierte la lista para que vaya de Inicio a Fin, no de fin a meta como está inicialmente

            #3. Marcar nodo como explorado
            lista_cerrada.add((nodo_actual.celda.fila, nodo_actual.celda.columna))

            #4. Expandir a nodos vecinos
            vecinos = self.mapa.obtener_vecinos(nodo_actual.celda)
            for vecino in vecinos:
                #Si el vecino ya fue explorado, se ignora
                if (vecino.fila, vecino.columna) in lista_cerrada:
                    continue

                #Crear el nuevo nodo hijo
                nodo_vecino = Nodo(vecino, nodo_actual)
                
                #Calcular costos
                #g = costo g del padre + costo de moverse a esa celda
                nodo_vecino.g = nodo_actual.g + vecino.obtener_costo_total() 
                #h = Distancia Manhattan a la meta
                nodo_vecino.h = self.distancia_manhattan(vecino, meta_celda)
                #f = g + h
                nodo_vecino.f = nodo_vecino.g + nodo_vecino.h

                #Verificar si el vecino ya está en la lista abierta con un g MENOR
                #Si es así, no vale la pena volver a agregarlo
                en_abierta_con_menor_costo = False
                for n in lista_abierta:
                    if n == nodo_vecino and n.g <= nodo_vecino.g:
                        en_abierta_con_menor_costo = True
                        break
                
                if not en_abierta_con_menor_costo:
                    heapq.heappush(lista_abierta, nodo_vecino)

        #Si la lista abierta se vacía y no se llega, no hay ruta posible
        return None, historial_exploracion

    #Tomar en cuenta que por naturaleza a* calcula la ruta de un punto a otro sin puntos intermedios, eso quiere decir que si se quieren añadir
    #Paradas o puntos intermedios entre el inicio y la meta, es mucho más sencillo y rentable, partir la ruta completa en pedazos o subrutas
    #Que vayan del punto a al b, creando inicios y metas temporales para cada tramo, y luego pegar todas esas subrutas en una macroruta (o la ruta completa)
    #Que el algoritmo recorrerá, que intentar alterar la matemática del algoritmo para que considere puntos a, b, c, ..., z, solamente por desear 
    #Poner paradas o puntos intermedios, para que Sergio no me borre todooooooooooo D': XD

    def calcular_ruta_completa(self, coordenadas_ruta): #Es el A* general, itera intercambiando los destinos para completar la ruta completa
        """
        Resuelve el requerimiento del taller: "única ruta pasando por intermedios y metas".
        Ejemplo coordenadas_ruta: [Inicio, Rest1, Rest2, Meta1, Meta2]
        """
        ruta_completa = []
        historial_completo = []
        
        for i in range(len(coordenadas_ruta) - 1):
            origen = coordenadas_ruta[i]
            destino = coordenadas_ruta[i+1] #La meta es el destino siguiente dentro de la lista de objetivos a visitar, así hasta llegar a la meta
            
            celda_origen = self.mapa.obtener_celda(origen[0], origen[1])
            celda_destino = self.mapa.obtener_celda(destino[0], destino[1])
            
            #Buscar sub-ruta
            sub_ruta, sub_historial = self.buscar_ruta_entre_dos_puntos(celda_origen, celda_destino)
            
            if sub_ruta is None:
                print(f"ALERTA: Camino bloqueado entre {origen} y {destino}.")
                return None 
            
            #Para evitar que el punto de llegada se duplique como punto de partida en la lista final
            historial_completo.extend(sub_historial)
            if i > 0:
                sub_ruta = sub_ruta[1:] # Evitar duplicar el punto de conexión
            ruta_completa.extend(sub_ruta)
            
        return ruta_completa, historial_completo