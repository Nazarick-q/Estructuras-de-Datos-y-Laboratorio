"""Interfaz de terminal del sistema de estudiantes (Laboratorio 3).

Permite elegir la estructura de almacenamiento y usar las tres operaciones
del enunciado: buscar por ID, insertar y listar en orden ascendente de ID.

Ejecutar desde la carpeta del laboratorio:

    python main.py        (también sirve el botón de ejecutar de VS Code)
    python -m src.app
"""

import re
import time

from .abb import ArbolBinarioBusqueda
from .arbol_bmas import ArbolBMas
from .estudiante import Estudiante
from .generador import generar_estudiantes
from .listas import ListaDesordenada, ListaOrdenada

# clave -> (nombre, fabrica, complejidad esperada)
ESTRUCTURAS = {
    "1": ("Lista desordenada", ListaDesordenada,
          "buscar O(N), insertar O(1), listar O(N log N)"),
    "2": ("Lista ordenada", ListaOrdenada,
          "buscar O(log N), insertar O(N), listar O(N)"),
    "3": ("Árbol binario de búsqueda (ABB)", ArbolBinarioBusqueda,
          "buscar e insertar O(h): ~O(log N) con IDs aleatorios, "
          "O(N) con IDs ordenados; listar O(N)"),
    "4": ("Árbol B+", None,
          "buscar e insertar O(log N), listar O(N)"),
}

# Umbral a partir del cual cargar un ABB con IDs ordenados se vuelve muy lento.
UMBRAL_ABB_ORDENADO = 20_000

_MILES = re.compile(r"^\d{1,3}([.,_]\d{3})+$")


# ---------------------------------------------------------------- entrada

def leer_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  El valor no puede estar vacío.")


def leer_entero(mensaje, minimo=None, maximo=None, defecto=None):
    """Lee un entero. Acepta separadores de miles (1.000.000 o 1,000,000)."""
    while True:
        texto = input(mensaje).strip()
        if texto == "" and defecto is not None:
            return defecto
        if _MILES.match(texto):
            texto = re.sub(r"[.,_]", "", texto)
        try:
            valor = int(texto)
        except ValueError:
            print("  Escribe un número entero.")
            continue
        if minimo is not None and valor < minimo:
            print(f"  El valor debe ser al menos {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"  El valor debe ser como máximo {maximo}.")
            continue
        return valor


def leer_flotante(mensaje, minimo, maximo):
    """Lee un decimal; acepta punto o coma como separador decimal."""
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            print("  Escribe un número (puedes usar punto o coma decimal).")
            continue
        if not (minimo <= valor <= maximo):
            print(f"  El valor debe estar entre {minimo} y {maximo}.")
            continue
        return valor


def leer_opcion(mensaje, validas, defecto=None):
    validas = tuple(validas)
    while True:
        texto = input(mensaje).strip().lower()
        if texto == "" and defecto is not None:
            return defecto
        if texto in validas:
            return texto
        print(f"  Opción no válida. Elige una de: {', '.join(validas)}.")


# ----------------------------------------------------------------- sesión

class Sesion:
    """Estructura elegida, cómo crear una vacía y su complejidad esperada."""

    def __init__(self, clave, nombre, fabrica, complejidad):
        self.clave = clave
        self.nombre = nombre
        self.fabrica = fabrica
        self.complejidad = complejidad
        self.estructura = fabrica()


def elegir_estructura():
    print("\nElige la estructura de almacenamiento:")
    for clave, (nombre, _, _) in ESTRUCTURAS.items():
        print(f"  {clave}. {nombre}")
    clave = leer_opcion("Opción: ", ESTRUCTURAS.keys())
    nombre, fabrica, complejidad = ESTRUCTURAS[clave]
    if clave == "4":
        orden = leer_entero(
            "Orden del B+ (máximo de hijos por nodo, mínimo 3, Enter = 32): ",
            minimo=3, defecto=32)
        nombre = f"{nombre} (orden {orden})"

        def fabrica(orden=orden):
            return ArbolBMas(orden)
    return Sesion(clave, nombre, fabrica, complejidad)


def formatear_tiempo(segundos):
    if segundos < 1e-3:
        return f"{segundos * 1e6:.1f} µs"
    if segundos < 1:
        return f"{segundos * 1e3:.2f} ms"
    return f"{segundos:.2f} s"


def imprimir_fila(est):
    print(f"{est.id:>10}  {est.nombre:<30}  {est.edad:>4}  {est.promedio:>8.2f}")


# ---------------------------------------------------------------- acciones

def accion_insertar(sesion):
    id_ = leer_entero("  ID (entero positivo): ", minimo=1)
    # En la terminal se evitan los IDs repetidos para todas las estructuras
    # (en la lista desordenada esta comprobación cuesta O(N), pero aquí no se mide).
    if sesion.estructura.buscar(id_) is not None:
        print(f"  Ya existe un estudiante con el ID {id_}. No se insertó.")
        return
    nombre = leer_texto("  Nombre: ")
    edad = leer_entero("  Edad: ", minimo=1, maximo=120)
    promedio = leer_flotante("  Promedio (0.0 a 5.0): ", 0.0, 5.0)
    sesion.estructura.insertar(Estudiante(id_, nombre, edad, promedio))
    print(f"  Estudiante {id_} insertado.")


def accion_buscar(sesion):
    id_ = leer_entero("  ID a buscar: ")
    inicio = time.perf_counter()
    est = sesion.estructura.buscar(id_)
    duracion = time.perf_counter() - inicio
    if est is None:
        print(f"  No se encontró ningún estudiante con el ID {id_}.")
    else:
        print(f"  {'ID':>10}  {'Nombre':<30}  {'Edad':>4}  {'Promedio':>8}")
        imprimir_fila(est)
    print(f"  (búsqueda: {formatear_tiempo(duracion)})")


def accion_listar(sesion):
    total = len(sesion.estructura)
    if total == 0:
        print("  La estructura está vacía.")
        return
    limite = leer_entero("  ¿Cuántos mostrar? (Enter = 20, 0 = todos): ",
                         minimo=0, defecto=20)
    inicio = time.perf_counter()
    todos = sesion.estructura.listar()
    duracion = time.perf_counter() - inicio
    mostrados = todos if limite == 0 else todos[:limite]
    print(f"  {'ID':>10}  {'Nombre':<30}  {'Edad':>4}  {'Promedio':>8}")
    for est in mostrados:
        imprimir_fila(est)
    print(f"  (mostrando {len(mostrados)} de {total}; "
          f"listado completo en {formatear_tiempo(duracion)})")


def accion_cargar(sesion):
    if len(sesion.estructura) > 0:
        print("  La carga de ejemplo solo funciona con la estructura vacía "
              "(usa la opción 6 para empezar de nuevo).")
        return
    n = leer_entero("  ¿Cuántos estudiantes? (Enter = 1000): ",
                    minimo=1, defecto=1000)
    letra = leer_opcion(
        "  Orden de inserción: [a]leatorio u [o]rdenado (Enter = a): ",
        ("a", "o"), "a")
    orden = "aleatorio" if letra == "a" else "ordenado"
    semilla = leer_entero("  Semilla (Enter = 42): ", defecto=42)

    if sesion.clave == "3" and orden == "ordenado" and n > UMBRAL_ABB_ORDENADO:
        pasos = n * (n - 1) // 2
        print(f"  Aviso: con IDs ordenados el ABB se convierte en una cadena y "
              f"insertar {n} estudiantes requiere unos {pasos:,} pasos; "
              f"puede tardar mucho.")
        if leer_opcion("  ¿Continuar? (s/n, Enter = n): ", ("s", "n"), "n") == "n":
            print("  Carga cancelada.")
            return

    estudiantes = generar_estudiantes(n, orden, semilla)
    # Se carga en una estructura nueva: si se interrumpe con Ctrl+C no queda a medias.
    nueva = sesion.fabrica()
    inicio = time.perf_counter()
    for est in estudiantes:
        nueva.insertar(est)
    duracion = time.perf_counter() - inicio
    sesion.estructura = nueva
    print(f"  Se insertaron {n} estudiantes ({orden}, semilla {semilla}) en "
          f"{formatear_tiempo(duracion)}  "
          f"(~{formatear_tiempo(duracion / n)} por inserción).")


def accion_info(sesion):
    estructura = sesion.estructura
    print(f"  Estructura: {sesion.nombre}")
    print(f"  Estudiantes almacenados: {len(estructura)}")
    if hasattr(estructura, "altura"):
        print(f"  Altura (niveles): {estructura.altura()}")
    print(f"  Complejidad esperada: {sesion.complejidad}")


ACCIONES = {
    "1": accion_insertar,
    "2": accion_buscar,
    "3": accion_listar,
    "4": accion_cargar,
    "5": accion_info,
}


def mostrar_menu(sesion):
    print("\n" + "=" * 56)
    print(f" Estructura: {sesion.nombre}   |   Estudiantes: "
          f"{len(sesion.estructura)}")
    print("=" * 56)
    print(" 1. Insertar estudiante")
    print(" 2. Buscar estudiante por ID")
    print(" 3. Listar estudiantes (orden ascendente de ID)")
    print(" 4. Cargar datos de ejemplo")
    print(" 5. Información de la estructura")
    print(" 6. Cambiar de estructura (empieza vacía)")
    print(" 0. Salir")


def main():
    print("=" * 56)
    print(" Sistema de estudiantes - Laboratorio 3")
    print(" (Ctrl+C cancela la operación en curso)")
    print("=" * 56)
    try:
        sesion = elegir_estructura()
        while True:
            mostrar_menu(sesion)
            opcion = leer_opcion("Opción: ", ("0", "1", "2", "3", "4", "5", "6"))
            if opcion == "0":
                break
            if opcion == "6":
                if len(sesion.estructura) > 0 and leer_opcion(
                        "  Se perderán los datos actuales. "
                        "¿Continuar? (s/n, Enter = n): ",
                        ("s", "n"), "n") == "n":
                    continue
                sesion = elegir_estructura()
                continue
            try:
                ACCIONES[opcion](sesion)
            except KeyboardInterrupt:
                print("\n  Operación cancelada.")
    except (EOFError, KeyboardInterrupt):
        print()
    print("Hasta luego.")


if __name__ == "__main__":
    main()
