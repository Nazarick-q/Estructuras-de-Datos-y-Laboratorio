import os
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from hyper_octree import Punto, HiperCubo, HyperOctree

CARPETA_SALIDA = os.path.dirname(os.path.abspath(__file__))
SEMILLA = None

def guardar_figura(fig, nombre):
    """Guarda la figura en la misma carpeta donde está el script test.py."""
    ruta = os.path.join(CARPETA_SALIDA, nombre)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    print(f"Figura guardada en: {ruta}")
    return ruta

def crear_arbol(k=2, n=500, capacidad=8):
    limite = HiperCubo([5000] * k, [5000] * k)  # Centro y mitades del hipercubo
    arbol = HyperOctree(limite, capacidad)       # capacidad = tamaño del bucket
    puntos = [Punto([random.uniform(0, 10000) for _ in range(k)]) for _ in range(n)]
    for p in puntos:
        arbol.insertar(p)
    return arbol, puntos

def test_visual_vecino_mas_cercano():
    if SEMILLA is not None:
        random.seed(SEMILLA)
    arbol, puntos = crear_arbol()
    cliente = Punto([5000, 5000])
    mejor_punto, mejor_distancia = arbol.vecino_mas_cercano(cliente)

    # Validación
    esperado = min(puntos, key=lambda p: p.distancia(cliente))
    assert mejor_punto is esperado, "El vecino más cercano no coincide con fuerza bruta"

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter([p.coordenadas[0] for p in puntos], [p.coordenadas[1] for p in puntos], c='lightgray', s=15, label='Entregas')
    ax.scatter(*cliente.coordenadas, c='blue', marker='x', s=100, label='Ubicación Cliente')
    if mejor_punto:
        ax.scatter(*mejor_punto.coordenadas, c='green', s=50, label='Más Cercano')
        ax.plot([cliente.coordenadas[0], mejor_punto.coordenadas[0]], [cliente.coordenadas[1], mejor_punto.coordenadas[1]], 'g--')
    ax.set_title(f"Vecino más cercano (Distancia: {mejor_distancia:.2f}m)")
    ax.legend()
    
    guardar_figura(fig, "vecino_mas_cercano.png")
    plt.show()

def test_visual_busqueda_radio():
    if SEMILLA is not None:
        random.seed(SEMILLA)
    arbol, puntos = crear_arbol()
    cliente = Punto([5000, 5000])
    radio = 1500
    encontrados = arbol.busqueda_radio(cliente, radio)

    esperados = [p for p in puntos if p.distancia(cliente) <= radio]
    assert set(map(id, encontrados)) == set(map(id, esperados)), \
        "La búsqueda por radio no coincide con fuerza bruta"

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter([p.coordenadas[0] for p in puntos], [p.coordenadas[1] for p in puntos], c='lightgray', s=15, label='Entregas')
    ax.scatter([p.coordenadas[0] for p in encontrados], [p.coordenadas[1] for p in encontrados], c='green', s=30, label=f'Dentro del radio ({len(encontrados)})')
    ax.scatter(*cliente.coordenadas, c='blue', marker='x', s=100, label='Ubicación Cliente')
    ax.add_patch(Circle(cliente.coordenadas, radio, fill=False, color='red', linestyle='--'))
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 10000)
    ax.set_aspect('equal')
    ax.set_title(f"Búsqueda por radio (r = {radio}m): {len(encontrados)} puntos")
    ax.legend()
    
    guardar_figura(fig, "busqueda_radio.png")
    plt.show()

if __name__ == "__main__":
    test_visual_vecino_mas_cercano()
    test_visual_busqueda_radio()