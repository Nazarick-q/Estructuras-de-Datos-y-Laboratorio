import os
import time
import random
import matplotlib.pyplot as plt

from hyper_octree import Punto, HiperCubo, HyperOctree

CARPETA_SALIDA = os.path.dirname(os.path.abspath(__file__))
SEMILLA = 31102025        # Semilla para reproducibilidad
NUM_CONSULTAS = 50        # Bloque de consultas para acumular tiempos en segundos

def guardar_figura(fig, nombre):
    ruta = os.path.join(CARPETA_SALIDA, nombre)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    print(f"[OK] Grafica guardada en: {ruta}")
    return ruta

def fuerza_bruta_radio(puntos, cliente, radio):
    return [p for p in puntos if p.distancia(cliente) <= radio]

def fuerza_bruta_vecino(puntos, cliente):
    return min(puntos, key=lambda p: p.distancia(cliente))


def ejecutar_analisis_completo():
    if SEMILLA is not None:
        random.seed(SEMILLA)

    tamanos_n = [100, 300, 500, 1000, 5000, 10000, 25000, 50000, 100000, 150000, 200000, 250000, 300000] # Se puede aumentar o disminuir para cambiar los tiempos de ejecución
    
    tiempos_arbol_radio = []
    tiempos_fb_radio = []
    
    tiempos_arbol_vecino = []
    tiempos_fb_vecino = []

    cliente = Punto([0, 0]) # Punto de referencia
    radio = 1500 # Radio de busqueda
    capacidad_bucket = 16 # Capacidad del bucket

    print("=" * 50)
    print("HYPEROCTREE (K=2) VS FUERZA BRUTA (ESCALA LOG-LOG)")
    print("=" * 50)

    for n in tamanos_n:
        limite = HiperCubo([0, 0], [10000, 10000])
        arbol = HyperOctree(limite, capacidad=capacidad_bucket, profundidad_max=14)
        puntos = [Punto([random.uniform(-10000, 10000) for _ in range(2)]) for _ in range(n)]

        for p in puntos:
            arbol.insertar(p)

        #Busqueda por radio
        t0 = time.perf_counter()
        for _ in range(NUM_CONSULTAS):
            _ = fuerza_bruta_radio(puntos, cliente, radio)
        t_fb_radio = time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(NUM_CONSULTAS):
            _ = arbol.busqueda_radio(cliente, radio)
        t_arbol_radio = time.perf_counter() - t0

        tiempos_fb_radio.append(t_fb_radio)
        tiempos_arbol_radio.append(t_arbol_radio)

        #Vecino mas cercano
        t0 = time.perf_counter()
        for _ in range(NUM_CONSULTAS):
            _ = fuerza_bruta_vecino(puntos, cliente)
        t_fb_vecino = time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(NUM_CONSULTAS):
            _ = arbol.vecino_mas_cercano(cliente)
        t_arbol_vecino = time.perf_counter() - t0

        tiempos_fb_vecino.append(t_fb_vecino)
        tiempos_arbol_vecino.append(t_arbol_vecino)

        print(f"N = {n:6d} | Radio: Arbol {t_arbol_radio:6.3f} s, FB {t_fb_radio:6.3f} s | Vecino: Arbol {t_arbol_vecino:6.3f} s, FB {t_fb_vecino:6.3f} s")

    # Grafica Busqueda por radio (ESCALA LOG-LOG)
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(tamanos_n, tiempos_fb_radio, label='Fuerza Bruta O(N)', marker='o', color='red', linewidth=2)
    ax1.plot(tamanos_n, tiempos_arbol_radio, label='HyperOctree', marker='s', color='green', linewidth=2)
    
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    ax1.set_title("Rendimiento Busqueda por radio - Escala Log-Log (Radio = 1500m)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Numero de Puntos N (Escala Logaritmica)", fontsize=10)
    ax1.set_ylabel("Tiempo Acumulado en Segundos (Escala Logaritmica)", fontsize=10)
    ax1.grid(True, which="both", linestyle='--', alpha=0.6)
    ax1.legend(fontsize=10)

    guardar_figura(fig1, "rendimiento_busqueda_por_radio.png")
    plt.show()

    # Grafica Vecino mas cercano (ESCALA LOG-LOG)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.plot(tamanos_n, tiempos_fb_vecino, label='Fuerza Bruta O(N)', marker='o', color='red', linewidth=2)
    ax2.plot(tamanos_n, tiempos_arbol_vecino, label='HyperOctree', marker='s', color='green', linewidth=2)
    
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    
    ax2.set_title("Rendimiento Vecino mas cercano - Escala Log-Log", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Numero de Puntos N (Escala Logaritmica)", fontsize=10)
    ax2.set_ylabel("Tiempo Acumulado en Segundos (Escala Logaritmica)", fontsize=10)
    ax2.grid(True, which="both", linestyle='--', alpha=0.6)
    ax2.legend(fontsize=10)

    guardar_figura(fig2, "rendimiento_vecino_mas_cercano.png")
    plt.show()

if __name__ == "__main__":
    ejecutar_analisis_completo()