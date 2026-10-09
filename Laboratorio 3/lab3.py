import time
import random
import statistics
import matplotlib.pyplot as plt
import sys
import bisect
import csv

sys.setrecursionlimit(50000)

class Estudiante:
    def __init__(self, id_estudiante, nombre, edad, promedio):
        self.id = id_estudiante
        self.nombre = nombre
        self.edad = edad
        self.promedio = promedio

# ==========================================
# ESTRUCTURAS DE DATOS
# ==========================================

class SistemaLista:
    def __init__(self):
        self.ids = []
        self.estudiantes = []

    def insertar(self, estudiante):
        idx = bisect.bisect_left(self.ids, estudiante.id)
        self.ids.insert(idx, estudiante.id)
        self.estudiantes.insert(idx, estudiante)

    def buscar(self, id_estudiante):
        idx = bisect.bisect_left(self.ids, id_estudiante)
        if idx < len(self.ids) and self.ids[idx] == id_estudiante:
            return self.estudiantes[idx]
        return None

    def listar(self):
        return list(self.estudiantes)

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

class NodoBPlus:
    def __init__(self, hoja=False):
        self.hoja = hoja
        self.claves = []
        self.valores = []
        self.hijos = []
        self.siguiente = None

class SistemaBPlus:
    def __init__(self, grado=32):
        self.raiz = NodoBPlus(hoja=True)
        self.grado = grado

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
                if estudiante.id >= nodo.claves[i]:
                    i += 1
            self._insertar_no_lleno(nodo.hijos[i], estudiante)

    def _dividir_hijo(self, nodo, i):
        grado = self.grado
        y = nodo.hijos[i]
        z = NodoBPlus(hoja=y.hoja)
        nodo.hijos.insert(i + 1, z)
        
        if y.hoja:
            nodo.claves.insert(i, y.claves[grado - 1])
            z.claves = y.claves[grado - 1:]
            y.claves = y.claves[:grado - 1]
            z.valores = y.valores[grado - 1:]
            y.valores = y.valores[:grado - 1]
            z.siguiente = y.siguiente
            y.siguiente = z
        else:
            nodo.claves.insert(i, y.claves[grado - 1])
            z.claves = y.claves[grado:]
            y.claves = y.claves[:grado - 1]
            z.hijos = y.hijos[grado:]
            y.hijos = y.hijos[:grado]

    def buscar(self, id_estudiante):
        nodo = self.raiz
        while not nodo.hoja:
            i = bisect.bisect_right(nodo.claves, id_estudiante)
            nodo = nodo.hijos[i]
        i = bisect.bisect_left(nodo.claves, id_estudiante)
        if i < len(nodo.claves) and nodo.claves[i] == id_estudiante:
            return nodo.valores[i]
        return None

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
# MOTORES DE MEDICIÓN ESTADÍSTICA
# ==========================================

def medir_insercion(clase_estructura, estudiantes):
    repeticiones = 1
    while True:
        tiempos = []
        for _ in range(5):  # 5 bloques independientes
            tiempo_acumulado = 0
            for _ in range(repeticiones):
                sistema = clase_estructura()
                
                # Excluir la creación/destrucción del tiempo medido
                t0 = time.perf_counter()
                for est in estudiantes:
                    sistema.insertar(est)
                tiempo_acumulado += (time.perf_counter() - t0)
                
            tiempos.append(tiempo_acumulado)
        
        promedio_ciclo = sum(tiempos) / 5
        if promedio_ciclo >= 1.0:
            t_ops = [t / repeticiones for t in tiempos]
            return statistics.mean(t_ops), statistics.median(t_ops), statistics.stdev(t_ops)
        repeticiones *= 2

def medir_busqueda(sistema, ids_busqueda):
    repeticiones = 1
    while True:
        tiempos = []
        for _ in range(5):
            tiempo_acumulado = 0
            for _ in range(repeticiones):
                t0 = time.perf_counter()
                for id_b in ids_busqueda:
                    sistema.buscar(id_b)
                tiempo_acumulado += (time.perf_counter() - t0)
            tiempos.append(tiempo_acumulado)
        
        promedio_ciclo = sum(tiempos) / 5
        if promedio_ciclo >= 1.0:
            t_ops = [t / (repeticiones * len(ids_busqueda)) for t in tiempos]
            return statistics.mean(t_ops), statistics.median(t_ops), statistics.stdev(t_ops)
        repeticiones *= 2

def medir_listar(sistema):
    repeticiones = 1
    while True:
        tiempos = []
        for _ in range(5):
            tiempo_acumulado = 0
            for _ in range(repeticiones):
                t0 = time.perf_counter()
                sistema.listar()
                tiempo_acumulado += (time.perf_counter() - t0)
            tiempos.append(tiempo_acumulado)
        
        promedio_ciclo = sum(tiempos) / 5
        if promedio_ciclo >= 1.0:
            t_ops = [t / repeticiones for t in tiempos]
            return statistics.mean(t_ops), statistics.median(t_ops), statistics.stdev(t_ops)
        repeticiones *= 2

# ==========================================
# EJECUCIÓN DEL EXPERIMENTO
# ==========================================

def guardar_csv(datos_crudos, archivo="resultados_laboratorio.csv"):
    with open(archivo, mode='w', newline='') as f:
        escritor = csv.writer(f)
        escritor.writerow(["Estructura", "Ordenamiento", "N", "Metrica", "Promedio", "Mediana", "StdDev"])
        for fila in datos_crudos:
            escritor.writerow(fila)
    print(f"Datos guardados en {archivo}")

def ejecutar_experimentos():
    random.seed(42) # Garantizar reproducibilidad
    tamanos_N = [1000, 5000, 10000, 20000]
    M_busquedas = 1000
    
    # Inyección de dependencias (B+ ajustado a grado 32)
    estructuras = {
        "Lista": SistemaLista, 
        "ABB": SistemaABB, 
        "BPlus": lambda: SistemaBPlus(grado=32)
    }
    
    resultados_dict = {
        "insercion": {"Lista": {"aleatorio": [], "ordenado": []}, "ABB": {"aleatorio": [], "ordenado": []}, "BPlus": {"aleatorio": [], "ordenado": []}},
        "busqueda":  {"Lista": {"aleatorio": [], "ordenado": []}, "ABB": {"aleatorio": [], "ordenado": []}, "BPlus": {"aleatorio": [], "ordenado": []}},
        "listar":    {"Lista": {"aleatorio": [], "ordenado": []}, "ABB": {"aleatorio": [], "ordenado": []}, "BPlus": {"aleatorio": [], "ordenado": []}}
    }
    datos_crudos_csv = []

    for N in tamanos_N:
        print(f"\n[{N}] Iniciando pruebas...")
        
        for tipo_orden in ["aleatorio", "ordenado"]:
            es_ordenado = (tipo_orden == "ordenado")
            
            ids = list(range(1, N + 1))
            if not es_ordenado: random.shuffle(ids)
            estudiantes = [Estudiante(i, f"Est_{i}", 20, 4.0) for i in ids]
            
            # Generar variedad de búsquedas (50% aciertos, 50% fallos)
            mitad = min(M_busquedas // 2, N)
            ids_acierto = random.sample(ids, mitad)
            ids_fallo = random.sample(range(N * 2, N * 3), M_busquedas - mitad)
            ids_busqueda = ids_acierto + ids_fallo
            random.shuffle(ids_busqueda)

            for nombre, clase in estructuras.items():
                if nombre == "ABB" and es_ordenado and N > 5000:
                    continue 

                # 1. Medir Inserción
                p_ins, m_ins, s_ins = medir_insercion(clase, estudiantes)
                resultados_dict["insercion"][nombre][tipo_orden].append((N, p_ins, s_ins))
                datos_crudos_csv.append([nombre, tipo_orden, N, "insercion", p_ins, m_ins, s_ins])

                # Preparar estructura estática
                sistema = clase()
                for est in estudiantes: sistema.insertar(est)

                # 2. Medir Búsqueda
                p_busq, m_busq, s_busq = medir_busqueda(sistema, ids_busqueda)
                resultados_dict["busqueda"][nombre][tipo_orden].append((N, p_busq, s_busq))
                datos_crudos_csv.append([nombre, tipo_orden, N, "busqueda", p_busq, m_busq, s_busq])

                # 3. Medir Listar
                p_list, m_list, s_list = medir_listar(sistema)
                resultados_dict["listar"][nombre][tipo_orden].append((N, p_list, s_list))
                datos_crudos_csv.append([nombre, tipo_orden, N, "listar", p_list, m_list, s_list])
                
                print(f"  -> {nombre} ({tipo_orden}) procesado.")

    guardar_csv(datos_crudos_csv)
    generar_graficas(resultados_dict)

def generar_graficas(resultados):
    marcadores = {'Lista': 'o-', 'ABB': 's-', 'BPlus': '^-'}
    configs = [
        ("insercion", "Tiempo Total de Construcción", 'linear', "grafica_1_insercion.png", True),
        ("busqueda", "Tiempo Promedio por Búsqueda", 'log', "grafica_2_busqueda.png", False),
        ("listar", "Tiempo Total de Listar O(N)", 'linear', "grafica_3_listar.png", False)
    ]

    for metrica, ylabel, escala, archivo, omitir_abb_ord in configs:
        plt.figure(figsize=(10, 6))
        for nombre, datos_estructura in resultados[metrica].items():
            for tipo_orden, datos in datos_estructura.items():
                if not datos: continue
                if omitir_abb_ord and nombre == "ABB" and tipo_orden == "ordenado": continue
                
                N_vals, tiempos, errores = zip(*datos)
                plt.errorbar(N_vals, tiempos, yerr=errores, fmt=marcadores[nombre], 
                            label=f"{nombre} ({tipo_orden})", capsize=4)

        plt.title(f"Rendimiento de {metrica.capitalize()} vs Tamaño de Entrada (N)")
        plt.xlabel("Número de Estudiantes (N)")
        plt.ylabel(f"{ylabel} (segundos)")
        plt.yscale(escala)
        plt.grid(True, which="both", ls="--")
        plt.legend()
        plt.tight_layout()
        plt.savefig(archivo)

if __name__ == "__main__":
    ejecutar_experimentos()