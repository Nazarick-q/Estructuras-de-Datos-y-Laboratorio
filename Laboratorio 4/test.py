import os
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from hyper_octree import Punto, HiperCubo, HyperOctree

CARPETA_SALIDA = os.path.dirname(os.path.abspath(__file__))
SEMILLA = 31102025 # Reproductibilidad de las pruebas

def guardar_figura(fig, nombre):
    """Guarda la figura en la misma carpeta donde está el script test.py."""
    ruta = os.path.join(CARPETA_SALIDA, nombre)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    print(f"Figura guardada en: {ruta}")
    return ruta

def crear_arbol(k=2, n=10000, capacidad=16): # Dimension, cantidad de puntos, capacidad del bucket
    limite = HiperCubo([0] * k, [10000] * k)  # Centro y mitades del hipercubo, se peden modificar para cambiar tamaño y centro del mapa
    arbol = HyperOctree(limite, capacidad) 
    puntos = [Punto([random.uniform(-10000, 10000) for _ in range(k)]) for _ in range(n)] # Cambia distribucion de los puntos
    for p in puntos:
        arbol.insertar(p)
    return arbol, puntos

def test_visual_vecino_mas_cercano():
    if SEMILLA is not None:
        random.seed(SEMILLA)
    arbol, puntos = crear_arbol()
    ubicacion_dada = Punto([0, 0]) # Cambia punto de referencia
    mejor_punto, mejor_distancia = arbol.vecino_mas_cercano(ubicacion_dada)

    esperado = min(puntos, key=lambda p: p.distancia(ubicacion_dada)) # Validación
    assert mejor_punto is esperado, "El vecino más cercano no coincide con fuerza bruta" # Solo se muestra si hay error

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter([p.coordenadas[0] for p in puntos], [p.coordenadas[1] for p in puntos], c='lightgray', s=15, label='Entregas')
    ax.scatter(*ubicacion_dada.coordenadas, c='blue', marker='x', s=100, label='Ubicación de referencia')
    if mejor_punto:
        ax.scatter(*mejor_punto.coordenadas, c='green', s=50, label='Más Cercano')
        ax.plot([ubicacion_dada.coordenadas[0], mejor_punto.coordenadas[0]], [ubicacion_dada.coordenadas[1], mejor_punto.coordenadas[1]], 'g--')
    ax.set_xlim(-10000 , 10000) # Cambia tamaño del mapa
    ax.set_ylim(-10000, 10000) # Cambia tamaño del mapa
    ax.set_xlabel("Distancia en el Eje X (metros)")
    ax.set_ylabel("Distancia en el Eje Y (metros)")
    ax.set_aspect('equal')
    ax.set_title(f"Vecino más cercano (Distancia: {mejor_distancia:.2f}m)")
    ax.legend()
    
    guardar_figura(fig, "vecino_mas_cercano.png")
    plt.show()

def test_visual_busqueda_radio():
    if SEMILLA is not None:
        random.seed(SEMILLA)
    arbol, puntos = crear_arbol()
    ubicacion_dada = Punto([0, 0]) # Cambia punto de referencia
    radio = 500
    encontrados = arbol.busqueda_radio(ubicacion_dada, radio)

    esperados = [p for p in puntos if p.distancia(ubicacion_dada) <= radio] # Validación
    assert set(map(id, encontrados)) == set(map(id, esperados)), "La búsqueda por radio no coincide con fuerza bruta" # Solo se muestra si hay error

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter([p.coordenadas[0] for p in puntos], [p.coordenadas[1] for p in puntos], c='lightgray', s=15, label='Entregas')
    ax.scatter([p.coordenadas[0] for p in encontrados], [p.coordenadas[1] for p in encontrados], c='green', s=30, label=f'Dentro del radio ({len(encontrados)})')
    ax.scatter(*ubicacion_dada.coordenadas, c='blue', marker='x', s=100, label='Ubicación dada de referencia')
    ax.add_patch(Circle(ubicacion_dada.coordenadas, radio, fill=False, color='red', linestyle='--'))
    ax.set_xlim(-10000, 10000) # Cambia tamaño del mapa
    ax.set_ylim(-10000, 10000) # Cambia tamaño del mapa
    ax.set_xlabel("Distancia en el Eje X (metros)")
    ax.set_ylabel("Distancia en el Eje Y (metros)")
    ax.set_aspect('equal')
    ax.set_title(f"Búsqueda por radio (r = {radio}m): {len(encontrados)} puntos")
    ax.legend()
    
    guardar_figura(fig, "busqueda_radio.png")
    plt.show()

if __name__ == "__main__":
    test_visual_vecino_mas_cercano()
    test_visual_busqueda_radio()