# ia/adversario.py
import math
import config

class EstadoJuego:
    """
    Representa una 'fotografía' del tablero en un momento específico.
    Usamos esta clase ligera para no clonar todo el mapa pesado en cada paso del árbol.
    """
    def __init__(self, pos_dron, inundaciones, objetivos):
        self.pos_dron = pos_dron             #Tupla (fila, col)
        self.inundaciones = set(inundaciones)#Set de tuplas (fila, col) con agua
        self.objetivos = tuple(objetivos)    #Tupla de (fila, col) a visitar en orden

class BuscadorAdversario:
    def __init__(self, mapa):
        self.mapa = mapa
        #Las montañas y ríos originales son las fuentes desde donde el clima puede expandir el agua según la investigación
        self.fuentes_agua_base = set(config.RIOS + config.MONTANAS)
        self.paso_global = 1 #Para el rastreo en la consola

    def distancia_manhattan(self, p1, p2): #Heuristica, se reutiliza la implementada en A*
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    
    def _obtener_nombre_accion(self, origen, destino): #Esto estaba en A* en la función de buscar ruta entre 2 puntos (A* local)
        """Helper para imprimir en consola hacia dónde se mueve."""
        if origen[0] > destino[0]: return "Arriba"
        if origen[0] < destino[0]: return "Abajo"
        if origen[1] > destino[1]: return "Izquierda"
        if origen[1] < destino[1]: return "Derecha"
        return "Llegada"

    def evaluar_estado(self, estado):
        """
        Función de Evaluación Estática (Heurística para MAX).
        Entre más alto el puntaje, mejor para el dron.
        """
        #1. Si el dron llegó a la meta, es la victoria máxima
        if not estado.objetivos:
            return 1000

        #2. Si el dron se ahogó (pisó una inundación), es la peor derrota
        if estado.pos_dron in estado.inundaciones:
            return -1000

        #3. Puntaje base basado en la distancia (queremos minimizar la distancia, 
        #por lo que la restamos para que una menor distancia dé un puntaje mayor)
        meta_actual = estado.objetivos[0]
        puntaje = -self.distancia_manhattan(estado.pos_dron, meta_actual)

        #Se castiga al dron por cada objetivo que le falte.
        #Al restarle 100 puntos por cada objetivo en la lista, el Dron preferirá 
        #"comerse" el objetivo actual lo más rápido posible para quitarse ese peso de -100 de encima.
        #Esto soluciona un bug anterior que tenía antes de que se quedaba dando vueltas cerca del objetivo en vez de tomarlo
        #Porque tomarlo implicaba un puntaje peor. Lo pueden comprobar borrando esta línea
        puntaje -= len(estado.objetivos) * 100

        #4. Penalización por estar cerca del agua (El dron prefiere rutas secas)
        vecinos_dron = self._obtener_vecinos_coordenada(estado.pos_dron[0], estado.pos_dron[1])
        for v in vecinos_dron:
            if v in estado.inundaciones or v in config.RIOS:
                puntaje -= 5 #Penalidad por volar junto al peligro, según la investigación, volar junto a estas casillas podría provocar perdida del dron

        return puntaje

    def obtener_movimientos_max(self, estado):
        """Devuelve las coordenadas a las que el dron puede moverse. Es un helper"""
        movimientos_validos = []
        vecinos = self._obtener_vecinos_coordenada(estado.pos_dron[0], estado.pos_dron[1])
        
        for v in vecinos:
            #El dron no puede atravesar montañas
            if v not in config.MONTANAS:
                movimientos_validos.append(v)
        return movimientos_validos

    def obtener_movimientos_min(self, estado):
        """
        Devuelve las celdas que el clima puede inundar.
        LÓGICA GEOGRÁFICA: El agua solo se expande desde las montañas o zonas ya inundadas. Es un helper
        """
        posibles_inundaciones = set()
        agua_actual = self.fuentes_agua_base.union(estado.inundaciones)
        
        for agua in agua_actual:
            vecinos = self._obtener_vecinos_coordenada(agua[0], agua[1])
            for v in vecinos:
                #El clima no inunda montañas, ni celdas que ya tienen agua, ni la fundación inicial
                if v not in config.MONTANAS and v not in estado.inundaciones and v != config.INICIO_FUNDACION:
                    posibles_inundaciones.add(v)
                    
        #Para evitar que MIN tenga demasiadas opciones (lo que haría lento el algoritmo),
        #se filtran para que solo intente inundar celdas que estén relativamente cerca del dron. Esto es opcional y se puede eliminar sin ningún problema
        movimientos_optimizados = [
            celda for celda in posibles_inundaciones 
            if self.distancia_manhattan(celda, estado.pos_dron) <= 5
        ]
        
        return movimientos_optimizados if movimientos_optimizados else list(posibles_inundaciones)[:5]

    def _obtener_vecinos_coordenada(self, fila, col):
        """Helper rápido para no usar el mapa pesado durante el árbol lógico."""
        vecinos = []
        for df, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nf, nc = fila + df, col + dc
            if 0 <= nf < config.FILAS and 0 <= nc < config.COLUMNAS:
                vecinos.append((nf, nc))
        return vecinos

    def poda_alfa_beta(self, estado, profundidad, alfa, beta, es_maximizador): #MINIMAX
        """Núcleo matemático Minimax con Poda Alfa-Beta."""
        if profundidad == 0 or not estado.objetivos or estado.pos_dron in estado.inundaciones:
            return self.evaluar_estado(estado), None #Manejo de errores en caso de que falten atributos

        mejor_movimiento = None

        if es_maximizador:
            max_eval = -math.inf #Peor opción que podría dar el contrincante
            movimientos = self.obtener_movimientos_max(estado) #Movimientos posibles
            
            for mov in movimientos: #Esto lo esta realizando en todo el árbol
                #Transición de estado: Si pisa un objetivo, se saca de la lista
                nuevos_objetivos = estado.objetivos
                if mov == estado.objetivos[0]:
                    nuevos_objetivos = estado.objetivos[1:] #Elimina el objetivo actual porque ya se alcanzó

                nuevo_estado = EstadoJuego(mov, estado.inundaciones, nuevos_objetivos) #Instancia al agente contrario
                evaluacion, _ = self.poda_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, False) #Explora el siguiente nivel del árbol asumiendo que el adversario jugará de manera óptima contra el
                
                if evaluacion > max_eval: #Ajusta su evaluación de acuerdo al resultado que dio el agente contrario
                    max_eval = evaluacion
                    mejor_movimiento = mov
                    
                alfa = max(alfa, evaluacion) #Realiza la poda
                if beta <= alfa:
                    break
            return max_eval, mejor_movimiento

        else: #Turno del Clima, funciona exactamente igual que el agente contrario, pero buscando su propio beneficio
            min_eval = math.inf
            movimientos = self.obtener_movimientos_min(estado)
            
            for mov in movimientos:
                nuevas_inundaciones = estado.inundaciones.copy()
                nuevas_inundaciones.add(mov)
                nuevo_estado = EstadoJuego(estado.pos_dron, nuevas_inundaciones, estado.objetivos)
                
                evaluacion, _ = self.poda_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, True)
                
                if evaluacion < min_eval:
                    min_eval = evaluacion
                    mejor_movimiento = mov
                    
                beta = min(beta, evaluacion)
                if beta <= alfa: #Poda
                    break
            return min_eval, mejor_movimiento

    def calcular_siguiente_paso(self, pos_actual_dron, inundaciones_actuales, objetivos_pendientes): #MAX
        """
        Calcula el paso del DRON y muestra el árbol de decisión en consola 
        para el reporte académico.
        """
        estado_inicial = EstadoJuego(pos_actual_dron, inundaciones_actuales, objetivos_pendientes)
        
        #Imprimir Cabecera una sola vez
        if self.paso_global == 1:
            print(f"\n--- PENSAMIENTO ADVERSARIO (ALFA-BETA) A PROFUNDIDAD {config.PROFUNDIDAD} ---")
            print(f"{'PASO':<5} | {'POSICION':<10} | {'OBJETIVO':<10} | {'ELEGIDO':<10} | {'EVAL':<5} | {'OPCIONES EVALUADAS (Acción:Puntaje)'}")
            print("-" * 90)

        max_eval = -math.inf
        mejor_movimiento = None
        alfa = -math.inf
        beta = math.inf
        
        movimientos = self.obtener_movimientos_max(estado_inicial)
        detalles_opciones = []

        for mov in movimientos: #Lo está haciendo por rama
            accion_txt = self._obtener_nombre_accion(pos_actual_dron, mov)
            
            nuevos_objetivos = estado_inicial.objetivos
            if mov == estado_inicial.objetivos[0]:
                nuevos_objetivos = estado_inicial.objetivos[1:] #Lo mismo de antes, si ya toco un objetivo pasa al siguiente

            nuevo_estado = EstadoJuego(mov, estado_inicial.inundaciones, nuevos_objetivos) #Llama al contrincante y luego lo hace jugar para ver que hará, con eso trabajar
            evaluacion, _ = self.poda_alfa_beta(nuevo_estado, config.PROFUNDIDAD - 1, alfa, beta, False)
            
            #Se guarda el detalle para la consola
            detalles_opciones.append(f"{accion_txt}:{evaluacion}")

            if evaluacion > max_eval: #Elige su mejor movimiento de acuerdo a como jugo el adversario
                max_eval = evaluacion
                mejor_movimiento = mov

            alfa = max(alfa, evaluacion)

        #Formateo para la consola
        str_pos = f"({pos_actual_dron[0]},{pos_actual_dron[1]})"
        str_obj = f"({estado_inicial.objetivos[0][0]},{estado_inicial.objetivos[0][1]})" if estado_inicial.objetivos else "None"
        str_accion = self._obtener_nombre_accion(pos_actual_dron, mejor_movimiento) if mejor_movimiento else "Ahogado"
        str_opciones = " | ".join(detalles_opciones)

        print(f"{self.paso_global:<5} | {str_pos:<10} | {str_obj:<10} | {str_accion:<10} | {max_eval:<5} | [{str_opciones}]")
        self.paso_global += 1

        return mejor_movimiento
        
    def calcular_paso_clima(self, pos_actual_dron, inundaciones_actuales, objetivos_pendientes): #MIN, funciona exactamente igual que el MAX pero buscando su propio beneficio
        """
        Calcula el paso del CLIMA (MIN) y muestra sus opciones evaluadas
        en consola con el mismo formato de tabla que el DRON.
        """
        estado_inicial = EstadoJuego(pos_actual_dron, inundaciones_actuales, objetivos_pendientes)
        
        #Se intercepta el primer nivel (MIN) para imprimir qué está evaluando
        min_eval = math.inf
        mejor_movimiento = None
        alfa = -math.inf
        beta = math.inf
        
        movimientos = self.obtener_movimientos_min(estado_inicial)
        detalles_opciones = []

        for mov in movimientos:
            #Simular estado futuro si el clima inunda 'mov'
            nuevas_inundaciones = estado_inicial.inundaciones.copy()
            nuevas_inundaciones.add(mov)
            nuevo_estado = EstadoJuego(estado_inicial.pos_dron, nuevas_inundaciones, estado_inicial.objetivos)
            
            #Evaluar esta rama (llamando al turno de MAX)
            evaluacion, _ = self.poda_alfa_beta(nuevo_estado, config.PROFUNDIDAD - 1, alfa, beta, True)
            
            #Guarda el detalle
            detalles_opciones.append(f"({mov[0]},{mov[1]}):{evaluacion}")

            if evaluacion < min_eval:
                min_eval = evaluacion
                mejor_movimiento = mov
                
            beta = min(beta, evaluacion)

        #Formateo para alinear con la tabla de consola del DRON
        #Usa self.paso_global - 1 porque el Dron ya aumentó el contador global
        str_paso = f"{self.paso_global - 1}-C" 
        str_pos = f"({pos_actual_dron[0]},{pos_actual_dron[1]})"
        str_obj = f"({estado_inicial.objetivos[0][0]},{estado_inicial.objetivos[0][1]})" if estado_inicial.objetivos else "None"
        str_accion = f"{mejor_movimiento}" if mejor_movimiento else "Nada"
        str_opciones = " | ".join(detalles_opciones)

        #Imprimir fila de la tabla alineada
        print(f"{str_paso:<5} | {str_pos:<10} | {str_obj:<10} | {str_accion:<10} | {min_eval:<5} | [{str_opciones}]")
        
        return mejor_movimiento