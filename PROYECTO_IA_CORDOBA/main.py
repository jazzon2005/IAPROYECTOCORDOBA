import sys
import pygame
import config
from modelo.mapa import Mapa
from ia.a_estrella import BuscadorAEstrella
from ia.adversario import BuscadorAdversario
from graficos.motor_pygame import MotorGrafico

def mostrar_menu():
    """Crea una UI básica con botones usando Pygame para elegir el Punto a ejecutar."""
    pygame.init()
    #Tamaño de ventana pequeño para el menú
    pantalla = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Menú Principal - IA Córdoba")
    fuente = pygame.font.SysFont(None, 30)

    #Definir los rectángulos de los botones
    boton_p1 = pygame.Rect(50, 80, 300, 50)
    boton_p2 = pygame.Rect(50, 160, 300, 50)

    while True:
        pantalla.fill(config.COLOR_FONDO)
        
        #Dibujar los botones
        pygame.draw.rect(pantalla, config.COLOR_INICIO, boton_p1)
        pygame.draw.rect(pantalla, config.COLOR_RIO, boton_p2) #Azul para el botón de agua/adversarios
        
        #Crear los textos
        texto_p1 = fuente.render("Punto 1: Ruta A*", True, (255, 255, 255))
        texto_p2 = fuente.render("Punto 2: Adversarios", True, (255, 255, 255))
        
        #Centrar el texto en los botones
        pantalla.blit(texto_p1, (boton_p1.x + 60, boton_p1.y + 15))
        pantalla.blit(texto_p2, (boton_p2.x + 40, boton_p2.y + 15))
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_p1.collidepoint(evento.pos):
                    return 1
                if boton_p2.collidepoint(evento.pos):
                    return 2
                    
        pygame.display.flip()

def ejecutar_punto_1():
    print("--- INICIANDO IA DE RESCATE - CÓRDOBA ---")
    print("Fase 1: Búsqueda de ruta óptima con A*")
    
    #1. Generar el mundo
    mapa_cordoba = Mapa()
    
    #2. Iniciar el "cerebro"
    cerebro_dron = BuscadorAEstrella(mapa_cordoba)
    
    #3. Ordenar las paradas: Inicio -> Rest 1 -> Rest 2 -> Meta
    secuencia_puntos = [
        config.INICIO_FUNDACION,
        config.RESTAURANTES[0],
        config.RESTAURANTES[1],
        config.COMUNIDADES[0]
    ]
    
    print("Calculando ruta...")
    #Ahora se capturan la ruta final Y el historial de los pasos que pensó
    ruta, historial = cerebro_dron.calcular_ruta_completa(secuencia_puntos)
    
    if ruta:
        print(f"\n¡Éxito! Ruta encontrada con un total de {len(ruta)} pasos.")
        print("Abriendo visualizador paso a paso...")
        visualizador = MotorGrafico(mapa_cordoba)
        #Se pasa el historial al motor gráfico para que anime la expansión
        visualizador.iniciar_bucle(ruta, historial)
    else:
        print("Error: No se encontró un camino válido. Revisa los obstáculos.")

def ejecutar_punto_2():    
    print("\n--- INICIANDO FASE 2: BÚSQUEDA ENTRE ADVERSARIOS ---")
    print("Dron (MAX) vs Clima/Inundaciones (MIN)")
    
    mapa_cordoba = Mapa()
    cerebro_adversario = BuscadorAdversario(mapa_cordoba)
    
    #Posiciones iniciales para el duelo
    inicio = config.INICIO_FUNDACION
    secuencia_puntos = [
        config.RESTAURANTES[0],
        config.RESTAURANTES[1],
        config.COMUNIDADES[0]
    ]
    
    print("Abriendo campo de batalla...")
    visualizador = MotorGrafico(mapa_cordoba)
    #Se inicia el bucle especial por turnos (Algoritmo MINIMAX)
    visualizador.iniciar_bucle_adversario(inicio, secuencia_puntos, cerebro_adversario)

if __name__ == "__main__":
    opcion = mostrar_menu()
    if opcion == 1:
        ejecutar_punto_1()
    elif opcion == 2:
        ejecutar_punto_2()