import pygame
import sys
import config

class MotorGrafico:
    def __init__(self, mapa):
        pygame.init()
        self.mapa = mapa
        self.ancho = config.COLUMNAS * config.TAMANO_CELDA
        self.alto = config.FILAS * config.TAMANO_CELDA
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("IA Córdoba - Dron de Rescate")
        self.reloj = pygame.time.Clock()

    def _obtener_color_celda(self, celda):
        if celda.tipo == config.TIPO_INICIO: return config.COLOR_INICIO
        if celda.tipo == config.TIPO_RESTAURANTE: return config.COLOR_RESTAURANTE
        if celda.tipo == config.TIPO_META: return config.COLOR_META
        if celda.tipo == config.TIPO_MONTANA: return config.COLOR_MONTANA
        if celda.tipo == config.TIPO_RIO: return config.COLOR_RIO
        return config.COLOR_NORMAL

    def dibujar_cuadricula(self):
        for fila in self.mapa.cuadricula:
            for celda in fila:
                color = self._obtener_color_celda(celda)
                rect = pygame.Rect(celda.columna * config.TAMANO_CELDA, 
                                   celda.fila * config.TAMANO_CELDA, 
                                   config.TAMANO_CELDA, config.TAMANO_CELDA)
                pygame.draw.rect(self.pantalla, color, rect)
                pygame.draw.rect(self.pantalla, config.COLOR_LINEA, rect, 1)

    def dibujar_ruta(self, ruta):
        if not ruta: return
        puntos_centro = []
        for celda in ruta:
            x = (celda.columna * config.TAMANO_CELDA) + (config.TAMANO_CELDA // 2)
            y = (celda.fila * config.TAMANO_CELDA) + (config.TAMANO_CELDA // 2)
            puntos_centro.append((x, y))
            pygame.draw.circle(self.pantalla, (255, 255, 255), (x, y), 5)
            
        if len(puntos_centro) > 1:
            pygame.draw.lines(self.pantalla, (255, 255, 255), False, puntos_centro, 4)

    def iniciar_bucle(self, ruta_optima, historial):
        """Mantiene la ventana abierta y anima el paso a paso."""
        corriendo = True
        
        #Variables para la animación
        pasos_dibujados = 0
        tiempo_ultimo_paso = pygame.time.get_ticks()
        velocidad_ms = 50 #Milisegundos entre cada cuadro explorado
        exploracion_terminada = False

        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                    
            self.pantalla.fill(config.COLOR_FONDO)
            self.dibujar_cuadricula()
            
            # --- LÓGICA DE ANIMACIÓN PASO A PASO ---
            if not exploracion_terminada and historial:
                tiempo_actual = pygame.time.get_ticks()
                if tiempo_actual - tiempo_ultimo_paso > velocidad_ms:
                    pasos_dibujados += 1
                    tiempo_ultimo_paso = tiempo_actual
                    if pasos_dibujados >= len(historial):
                        exploracion_terminada = True
                
                #Dibujar las celdas exploradas hasta el paso actual
                for i in range(pasos_dibujados):
                    celda = historial[i]
                    #Solo repintar de "explorado" si no es un punto de interés clave
                    if celda.tipo in [config.TIPO_NORMAL, config.TIPO_RIO]:
                        rect = pygame.Rect(celda.columna * config.TAMANO_CELDA, 
                                           celda.fila * config.TAMANO_CELDA, 
                                           config.TAMANO_CELDA, config.TAMANO_CELDA)
                        pygame.draw.rect(self.pantalla, (70, 130, 180), rect) #Color azul acero brillante (Explorado)
                        pygame.draw.rect(self.pantalla, config.COLOR_LINEA, rect, 1)
            else:
                #Una vez termina de animar cómo piensa, dibuja todos los cuadros explorados...
                for celda in (historial if historial else []):
                    if celda.tipo in [config.TIPO_NORMAL, config.TIPO_RIO]:
                        rect = pygame.Rect(celda.columna * config.TAMANO_CELDA, celda.fila * config.TAMANO_CELDA, config.TAMANO_CELDA, config.TAMANO_CELDA)
                        pygame.draw.rect(self.pantalla, (70, 130, 180), rect)
                        pygame.draw.rect(self.pantalla, config.COLOR_LINEA, rect, 1)
                
                #Y traza la ruta final ganadora encima.
                self.dibujar_ruta(ruta_optima)
            
            pygame.display.flip()
            self.reloj.tick(60)
            
        pygame.quit()
        sys.exit()

    def iniciar_bucle_adversario(self, dron_inicio, objetivos, cerebro):
        """Mantiene la ventana abierta para el juego por turnos Dron vs Clima."""
        corriendo = True
        pos_dron = dron_inicio
        inundaciones = set(config.RIOS) #Inicia con los ríos base
        objetivos_pendientes = list(objetivos) #Copia de la lista de metas
        
        tiempo_ultimo_turno = pygame.time.get_ticks()
        velocidad_turno = 800 #Milisegundos entre cada jugada (0.8 segundos)
        
        turno_dron = True
        juego_terminado = False

        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False

            tiempo_actual = pygame.time.get_ticks()
            if not juego_terminado and tiempo_actual - tiempo_ultimo_turno > velocidad_turno:
                tiempo_ultimo_turno = tiempo_actual
                
                if turno_dron:
                    # --- TURNO DEL DRON (MAX) ---
                    nuevo_paso = cerebro.calcular_siguiente_paso(pos_dron, inundaciones, objetivos_pendientes)
                    if nuevo_paso:
                        pos_dron = nuevo_paso
                        print(f"[*] Dron avanza a: {pos_dron}")
                        
                        #Si pisa el objetivo actual, lo removemos de la lista
                        if objetivos_pendientes and pos_dron == objetivos_pendientes[0]:
                            print(f"[+] ¡Objetivo alcanzado: {pos_dron}!")
                            objetivos_pendientes.pop(0)
                            
                    turno_dron = False
                else:
                    # --- TURNO DEL CLIMA (MIN) ---
                    nuevo_agua = cerebro.calcular_paso_clima(pos_dron, inundaciones, objetivos_pendientes)
                    if nuevo_agua:
                        inundaciones.add(nuevo_agua)
                        print(f"[!] Clima inunda: {nuevo_agua}")
                    turno_dron = True

                #Validar condiciones de fin de juego
                if not objetivos_pendientes:
                    print("\n¡VICTORIA! El dron ha completado toda la ruta a salvo.")
                    juego_terminado = True
                elif pos_dron in inundaciones:
                    print("\n¡DERROTA! El dron fue atrapado por el desbordamiento.")
                    juego_terminado = True

            #DIBUJAR TODO
            self.pantalla.fill(config.COLOR_FONDO)
            self.dibujar_cuadricula()

            #Dibujar inundaciones dinámicas (agua nueva)
            for agua in inundaciones:
                if agua not in config.RIOS: #Se pintan solo las nuevas
                    rect = pygame.Rect(agua[1] * config.TAMANO_CELDA, agua[0] * config.TAMANO_CELDA, 
                                       config.TAMANO_CELDA, config.TAMANO_CELDA)
                    pygame.draw.rect(self.pantalla, (20, 80, 120), rect) #Un azul marino oscuro y amenazante
                    pygame.draw.rect(self.pantalla, config.COLOR_LINEA, rect, 1)

            #Dibujar todas las metas pendientes
            for obj in objetivos_pendientes:
                m_rect = pygame.Rect(obj[1] * config.TAMANO_CELDA, obj[0] * config.TAMANO_CELDA, 
                                     config.TAMANO_CELDA, config.TAMANO_CELDA)
                pygame.draw.rect(self.pantalla, config.COLOR_META, m_rect)

            #Dibujar el Dron
            d_rect = pygame.Rect(pos_dron[1] * config.TAMANO_CELDA, pos_dron[0] * config.TAMANO_CELDA, 
                                 config.TAMANO_CELDA, config.TAMANO_CELDA)
            pygame.draw.rect(self.pantalla, (255, 200, 0), d_rect) #Dron de color amarillo/dorado
            pygame.draw.circle(self.pantalla, (0, 0, 0), d_rect.center, 6) #Detalle visual del dron

            pygame.display.flip()
            self.reloj.tick(60)

        pygame.quit()
        sys.exit()