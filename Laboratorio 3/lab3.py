import time
import random
import statistics
import matplotlib.pyplot as plt
import sys
import bisect

# Aumentar el límite de recursión para el ABB en el caso de datos ordenados
sys.setrecursionlimit(50000)

# ==========================================
# 1. MODELO DE DATOS
# ==========================================
class Estudiante:
    def __init__(self, id_estudiante, nombre, edad, promedio):
        self.id = id_estudiante
        self.nombre = nombre
        self.edad = edad
        self.promedio = promedio

# ==========================================
# 2. ESTRUCTURAS DE DATOS
# ==========================================

# Estrategia 1: Lista (Mantenida ordenada usando bisect para simular un sistema real)
class SistemaLista:
    def __init__(self):
        self.ids = []
        self.estudiantes = []

    def insertar(self, estudiante):
        # Inserción manteniendo el orden O(N)
        idx = bisect.bisect_left(self.ids, estudiante.id)
        self.ids.insert(idx, estudiante.id)
        self.estudiantes.insert(idx, estudiante)

    def buscar(self, id_estudiante):
        # Búsqueda binaria O(log N)
        idx = bisect.bisect_left(self.ids, id_estudiante)
        if idx < len(self.ids) and self.ids[idx] == id_estudiante:
            return self.estudiantes[idx]
        return None

    def listar(self):
        return self.estudiantes

# Estrategia 2: Árbol Binario de Búsqueda (ABB)
class NodoABB:
    def __init__(self, estudiante):
        self.estudiante = estudiante
        self.izq = None
        self.der = None

class SistemaABB:
    def __init__(self):
        self.raiz = None

    def insertar(self, estudiante):
        if self.raiz is None:
            self.raiz = NodoABB(estudiante)
        else:
            self._insertar_recursivo(self.raiz, estudiante)

    def _insertar_recursivo(self, nodo, estudiante):
        if estudiante.id < nodo.estudiante.id:
            if nodo.izq is None:
                nodo.izq = NodoABB(estudiante)
            else:
                self._insertar_recursivo(nodo.izq, estudiante)
        elif estudiante.id > nodo.estudiante.id:
            if nodo.der is None:
                nodo.der = NodoABB(estudiante)
            else:
                self._insertar_recursivo(nodo.der, estudiante)

    def buscar(self, id_estudiante):
        return self._buscar_recursivo(self.raiz, id_estudiante)

    def _buscar_recursivo(self, nodo, id_estudiante):
        if nodo is None or nodo.estudiante.id == id_estudiante:
            return nodo.estudiante if nodo else None
        if id_estudiante < nodo.estudiante.id:
            return self._buscar_recursivo(nodo.izq, id_estudiante)
        return self._buscar_recursivo(nodo.der, id_estudiante)

    def listar(self):
        resultado = []
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo, resultado):
        if nodo:
            self._inorden(nodo.izq, resultado)
            resultado.append(nodo.estudiante)
            self._inorden(nodo.der, resultado)

# Estrategia 3: Árbol B+ (Implementación simplificada para el laboratorio)
class NodoBPlus:
    def __init__(self, hoja=False):
        self.hoja = hoja
        self.claves = []
        self.valores = []
        self.hijos = []
        self.siguiente = None

class SistemaBPlus:
    def __init__(self, grado=3):
        self.raiz = NodoBPlus(hoja=True)
        self.grado = grado

    def buscar(self, id_estudiante):
        nodo = self.raiz
        while not nodo.hoja:
            i = bisect.bisect_right(nodo.claves, id_estudiante)
            nodo = nodo.hijos[i]
        i = bisect.bisect_left(nodo.claves, id_estudiante)
        if i < len(nodo.claves) and nodo.claves[i] == id_estudiante:
            return nodo.valores[i]
        return None

    def insertar(self, estudiante):
        raiz = self.raiz
        if len(raiz.claves) == (2 * self.grado) - 1:
            nueva_raiz = NodoBPlus()
            self.raiz = nueva_raiz
            nueva_raiz.hijos.append(raiz)
            self._dividir_hijo(nueva_raiz, 0)
            self._insertar_no_lleno(nueva_raiz, estudiante)
        else:
            self._insertar_no_lleno(raiz, estudiante)

    def _insertar_no_lleno(self, nodo, estudiante):
        i = len(nodo.claves) - 1
        if nodo.hoja:
            nodo.claves.append(0)
            nodo.valores.append(None)
            while i >= 0 and estudiante.id < nodo.claves[i]:
                nodo.claves[i + 1] = nodo.claves[i]
                nodo.valores[i + 1] = nodo.valores[i]
                i -= 1
            nodo.claves[i + 1] = estudiante.id
            nodo.valores[i + 1] = estudiante
        else:
            while i >= 0 and estudiante.id < nodo.claves[i]:
                i -= 1
            i += 1
            if len(nodo.hijos[i].claves) == (2 * self.grado) - 1:
                self._dividir_hijo(nodo, i)
                if estudiante.id > nodo.claves[i]:
                    i += 1
            self._insertar_no_lleno(nodo.hijos[i], estudiante)

    def _dividir_hijo(self, nodo, i):
        grado = self.grado
        y = nodo.hijos[i]
        z = NodoBPlus(hoja=y.hoja)
        nodo.hijos.insert(i + 1, z)
        nodo.claves.insert(i, y.claves[grado - 1])
        z.claves = y.claves[grado:(2 * grado - 1)]
        y.claves = y.claves[0:(grado - 1)]
        if y.hoja:
            z.valores = y.valores[grado:(2 * grado - 1)]
            y.valores = y.valores[0:(grado - 1)]
            z.siguiente = y.siguiente
            y.siguiente = z
        else:
            z.hijos = y.hijos[grado:(2 * grado)]
            y.hijos = y.hijos[0:grado]

    def listar(self):
        resultado = []
        nodo = self.raiz
        while not nodo.hoja:
            nodo = nodo.hijos[0]
        while nodo:
            resultado.extend(nodo.valores)
            nodo = nodo.siguiente
        return resultado

# ==========================================
# 3. MARCO DE PRUEBAS ESTADÍSTICAS Y GRÁFICOS
# ==========================================

def generar_datos(N, ordenados=False):
    ids = list(range(1, N + 1))
    if not ordenados:
        random.shuffle(ids)
    estudiantes = [Estudiante(id_est, f"Estudiante_{id_est}", 20, 4.0) for id_est in ids]
    return estudiantes, ids

def medir_tiempo_operacion(funcion, datos_prueba, min_tiempo=1.0):
    """
    Escala dinámicamente el número de repeticiones hasta que la ejecución total 
    dure más del tiempo mínimo (1 segundo), asegurando mediciones correctas.
    """
    repeticiones = 1
    while True:
        tiempos = []
        # Realizamos 3 bloques de medición para calcular desviación estándar
        for _ in range(3):
            inicio = time.perf_counter()
            for _ in range(repeticiones):
                for dato in datos_prueba:
                    funcion(dato)
            fin = time.perf_counter()
            tiempos.append(fin - inicio)
        
        tiempo_total_promedio = sum(tiempos) / 3
        if tiempo_total_promedio >= min_tiempo:
            # Calcular tiempo promedio por operación unitaria
            tiempo_por_operacion = [(t / (repeticiones * len(datos_prueba))) for t in tiempos]
            promedio = statistics.mean(tiempo_por_operacion)
            desviacion = statistics.stdev(tiempo_por_operacion) if len(tiempo_por_operacion) > 1 else 0
            return promedio, desviacion, repeticiones
        
        repeticiones *= 2

def ejecutar_experimentos():
    tamanos_N = [1000, 5000, 10000, 20000]
    M = 1000 # Base de búsquedas
    
    resultados = {
        "Lista": {"aleatorio": [], "ordenado": []},
        "ABB": {"aleatorio": [], "ordenado": []},
        "BPlus": {"aleatorio": [], "ordenado": []}
    }

    estructuras = {
        "Lista": SistemaLista,
        "ABB": SistemaABB,
        "BPlus": SistemaBPlus
    }

    for N in tamanos_N:
        print(f"\n--- Evaluando para N = {N} ---")
        
        for tipo_orden in ["aleatorio", "ordenado"]:
            es_ordenado = (tipo_orden == "ordenado")
            estudiantes, ids_insertados = generar_datos(N, ordenados=es_ordenado)
            
            # Generar M IDs aleatorios para buscar (garantizando que existan)
            ids_busqueda = random.sample(ids_insertados, min(M, N))

            for nombre, clase_estructura in estructuras.items():
                if nombre == "ABB" and es_ordenado and N > 5000:
                    print(f"Omitiendo ABB ordenado para N={N} (Evitar StackOverflow por O(N))")
                    continue

                sistema = clase_estructura()
                
                # Pre-cargar datos
                for est in estudiantes:
                    sistema.insertar(est)

                # Medir Búsqueda (Asegurando > 1 segundo)
                promedio, std_dev, reps = medir_tiempo_operacion(sistema.buscar, ids_busqueda, min_tiempo=1.0)
                resultados[nombre][tipo_orden].append((N, promedio, std_dev))
                
                print(f"[{nombre} - {tipo_orden}] N={N} | Promedio: {promedio:.2e}s | StdDev: {std_dev:.2e} | Reps por bloque: {reps}")

    graficar_resultados(resultados)

def graficar_resultados(resultados):
    plt.figure(figsize=(12, 6))
    
    marcadores = {'Lista': 'o-', 'ABB': 's-', 'BPlus': '^-'}
    colores = {'aleatorio': 'blue', 'ordenado': 'red'}

    for nombre, datos_estructura in resultados.items():
        for tipo_orden, datos in datos_estructura.items():
            if not datos: continue
            N_vals = [d[0] for d in datos]
            tiempos = [d[1] for d in datos]
            errores = [d[2] for d in datos]
            
            etiqueta = f"{nombre} ({tipo_orden})"
            plt.errorbar(N_vals, tiempos, yerr=errores, fmt=marcadores[nombre], 
                         label=etiqueta, capsize=5)

    plt.title("Comparación de Tiempo de Búsqueda vs Tamaño de Entrada (N)")
    plt.xlabel("Número de Estudiantes (N)")
    plt.ylabel("Tiempo Promedio por Búsqueda (segundos)")
    plt.yscale('log')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig("grafica_tiempos_busqueda.png")
    print("\nGráfica guardada como 'grafica_tiempos_busqueda.png'.")
    plt.show()

if __name__ == "__main__":
    ejecutar_experimentos()