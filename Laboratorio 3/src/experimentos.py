"""Experimentos de medición del Laboratorio 3.

Ejecutar desde la carpeta del laboratorio. Hay tres modos:

    python -m src.experimentos piloto       # mide poco y estima cuánto tardaría el plan
    python -m src.experimentos orden-bmas   # experimento secundario: variar el orden del B+
    python -m src.experimentos principal    # experimento principal (el que alimenta las gráficas)

Cada modo escribe un CSV en formato largo (una fila por repetición, estructura y
operación) en la carpeta data/, más un JSON con el entorno de ejecución. El modo
principal puede interrumpirse con Ctrl+C y reanudarse: al volver a ejecutar el
mismo comando se saltan las repeticiones ya guardadas.

Metodología (resumen; se detalla en el README y la wiki)
- Datos: IDs = permutación de 1 a N (caso "aleatorio") o 1, 2, ..., N (caso
  "ordenado"). Ambos casos contienen exactamente los mismos registros.
- Búsquedas: M IDs, 80 % existentes y 20 % ausentes (de N+1 a 2N), mezclados.
- Dentro de cada repetición, las cuatro estructuras se miden una tras otra
  con los mismos datos y las mismas búsquedas (comparación pareada), de modo
  que cualquier deriva del equipo (calentamiento, carga) les afecta por igual.
- Medición: time.perf_counter, sin desactivar el recolector de basura. Solo se
  cronometran las tres operaciones; la generación de datos, la altura y las
  comprobaciones quedan fuera. Entre estructuras se llama a gc.collect() para
  liberar memoria (no se cronometra).
- Semilla de cada repetición = semilla base + número de repetición.

Columnas del CSV
    tiempo_total_s          tiempo de la operación completa.
    tiempo_por_operacion_s  insertar: total / N;  buscar: total / M;
                            listar: total / N (por elemento listado).
    M                       número de búsquedas de esa repetición (se repite
                            en las tres filas, aunque solo afecta a buscar).
    altura                  niveles del árbol (ABB y B+); vacío en las listas.
    orden_bmas              orden del B+; vacío en las demás estructuras.
"""

import argparse
import csv
import gc
import json
import math
import os
import platform
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .abb import ArbolBinarioBusqueda
from .arbol_bmas import ArbolBMas
from .generador import generar_estudiantes, generar_ids_busqueda
from .listas import ListaDesordenada, ListaOrdenada

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"

COLUMNAS = [
    "estructura", "operacion", "orden_insercion", "N", "M", "repeticion",
    "semilla", "tiempo_total_s", "tiempo_por_operacion_s", "altura",
    "orden_bmas",
]

ESTRUCTURAS = ("lista_desordenada", "lista_ordenada", "abb", "bmas")
ORDENES_INSERCION = ("aleatorio", "ordenado")

# Parámetros acordados para el experimento principal.
TAMANOS = (100, 1_000, 10_000, 100_000, 1_000_000)
UMBRAL_REPETICIONES = 100_000      # N <= umbral: repeticiones "pequeñas"
REPS_PEQUENAS, REPS_GRANDES = 30, 10
M_DEFECTO = 1_000
PROPORCION_AUSENTES = 0.2
SEMILLA_BASE = 42
ORDEN_BMAS_DEFECTO = 32            # provisional: se elige con el experimento secundario
ORDENES_BMAS_SECUNDARIO = (4, 8, 16, 32, 64, 128)
N_SECUNDARIO = 100_000
N_MINIMO_M_REDUCIDA = 1_000_000

# Conservador hasta que la piloto indique hasta dónde llega el ABB ordenado.
LIMITE_ABB_ORDENADO_DEFECTO = 10_000

# Tamaños de la piloto (el ABB ordenado es cuadrático: se limita).
TAMANOS_PILOTO = (1_000, 10_000, 100_000)
TAMANOS_PILOTO_ABB_ORDENADO = (1_000, 5_000, 20_000)


def repeticiones_plan(n):
    return REPS_PEQUENAS if n <= UMBRAL_REPETICIONES else REPS_GRANDES


# ------------------------------------------------------------------ medición

def crear(estructura, orden_bmas=None):
    if estructura == "lista_desordenada":
        return ListaDesordenada()
    if estructura == "lista_ordenada":
        return ListaOrdenada()
    if estructura == "abb":
        return ArbolBinarioBusqueda()
    if estructura == "bmas":
        return ArbolBMas(ORDEN_BMAS_DEFECTO if orden_bmas is None else orden_bmas)
    raise ValueError(f"Estructura desconocida: {estructura}")


def medir_repeticion(estructura, orden_bmas, orden_insercion, n, repeticion,
                     semilla, registros, ids_busqueda):
    """Mide insertar, buscar y listar para una estructura. Devuelve 3 filas."""
    est = crear(estructura, orden_bmas)
    reloj = time.perf_counter
    m = len(ids_busqueda)

    insertar = est.insertar
    inicio = reloj()
    for registro in registros:
        insertar(registro)
    t_insertar = reloj() - inicio

    buscar = est.buscar
    inicio = reloj()
    for id_ in ids_busqueda:
        buscar(id_)
    t_buscar = reloj() - inicio

    inicio = reloj()
    listado = est.listar()
    t_listar = reloj() - inicio

    # Comprobaciones de cordura (fuera de las mediciones).
    if len(est) != n or len(listado) != n:
        raise RuntimeError(f"{estructura}: tamaño inesperado tras insertar")
    if est.buscar(1) is None or est.buscar(n) is None or est.buscar(n + 1) is not None:
        raise RuntimeError(f"{estructura}: búsqueda incorrecta en las comprobaciones")
    altura = est.altura() if hasattr(est, "altura") else ""

    def fila(operacion, total, divisor):
        return {
            "estructura": estructura,
            "operacion": operacion,
            "orden_insercion": orden_insercion,
            "N": n,
            "M": m,
            "repeticion": repeticion,
            "semilla": semilla,
            "tiempo_total_s": total,
            "tiempo_por_operacion_s": total / divisor if divisor else 0.0,
            "altura": altura,
            "orden_bmas": "" if orden_bmas is None else orden_bmas,
        }

    return [fila("insertar", t_insertar, n),
            fila("buscar", t_buscar, m),
            fila("listar", t_listar, n)]


# ----------------------------------------------------------------------- CSV

def _clave(estructura, orden_insercion, n, repeticion, orden_bmas):
    return (estructura, orden_insercion, int(n), int(repeticion),
            "" if orden_bmas is None else str(orden_bmas))


def leer_completadas(ruta):
    """Claves de las repeticiones ya guardadas (las que tienen la fila 'listar')."""
    completadas = set()
    if not ruta.exists() or ruta.stat().st_size == 0:
        return completadas
    with open(ruta, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != COLUMNAS:
            raise ValueError(
                f"{ruta} existe pero sus columnas no coinciden con las esperadas; "
                "usa otro nombre de archivo o muévelo antes de continuar.")
        for fila in lector:
            if fila["operacion"] == "listar":
                completadas.add(_clave(fila["estructura"], fila["orden_insercion"],
                                       fila["N"], fila["repeticion"],
                                       fila["orden_bmas"]))
    return completadas


def _variantes(estructuras, ordenes_bmas):
    for estructura in estructuras:
        if estructura == "bmas":
            for orden in ordenes_bmas:
                yield estructura, orden
        else:
            yield estructura, None


def _omitida(estructura, orden_insercion, n, limite_abb_ordenado):
    return (estructura == "abb" and orden_insercion == "ordenado"
            and limite_abb_ordenado is not None and n > limite_abb_ordenado)


def contar_ejecuciones(estructuras, ordenes_insercion, tamanos, repeticiones,
                       ordenes_bmas, limite_abb_ordenado):
    """Cuántas mediciones (estructura x repetición) tiene el plan."""
    total = 0
    for n in tamanos:
        for orden in ordenes_insercion:
            for estructura, _ in _variantes(estructuras, ordenes_bmas):
                if not _omitida(estructura, orden, n, limite_abb_ordenado):
                    total += repeticiones(n)
    return total


def correr(ruta_csv, estructuras, ordenes_insercion, tamanos, m, repeticiones,
           semilla_base=SEMILLA_BASE, ordenes_bmas=(ORDEN_BMAS_DEFECTO,),
           limite_abb_ordenado=None, m_reducida_lista=None,
           n_minimo_m_reducida=N_MINIMO_M_REDUCIDA, salida=print):
    """Ejecuta el plan y agrega cada medición al CSV apenas termina.

    repeticiones: función n -> número de repeticiones para ese tamaño.
    Devuelve cuántas mediciones nuevas se hicieron.
    """
    ruta_csv = Path(ruta_csv)
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    completadas = leer_completadas(ruta_csv)
    es_nuevo = not ruta_csv.exists() or ruta_csv.stat().st_size == 0

    if limite_abb_ordenado is not None and "abb" in estructuras \
            and "ordenado" in ordenes_insercion:
        omitidos = [n for n in tamanos if n > limite_abb_ordenado]
        if omitidos:
            salida(f"Aviso: ABB con inserción ordenada omitido para N = "
                   f"{', '.join(f'{n:,}' for n in omitidos)} "
                   f"(límite: {limite_abb_ordenado:,}).")

    nuevas = 0
    with open(ruta_csv, "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, lineterminator="\n")
        if es_nuevo:
            escritor.writeheader()
        for n in tamanos:
            reps = repeticiones(n)
            for orden in ordenes_insercion:
                for rep in range(1, reps + 1):
                    pendientes = [
                        (est, ob) for est, ob in _variantes(estructuras, ordenes_bmas)
                        if not _omitida(est, orden, n, limite_abb_ordenado)
                        and _clave(est, orden, n, rep, ob) not in completadas
                    ]
                    if not pendientes:
                        continue
                    inicio = time.perf_counter()
                    semilla = semilla_base + rep
                    registros = generar_estudiantes(n, orden, semilla)
                    ids = generar_ids_busqueda(n, m, PROPORCION_AUSENTES, semilla)
                    for est, ob in pendientes:
                        ids_est = ids
                        if (est == "lista_desordenada" and m_reducida_lista
                                and n >= n_minimo_m_reducida):
                            ids_est = ids[:m_reducida_lista]
                        filas = medir_repeticion(est, ob, orden, n, rep, semilla,
                                                 registros, ids_est)
                        escritor.writerows(filas)
                        archivo.flush()
                        nuevas += 1
                        gc.collect()
                    salida(f"N={n:>9,}  {orden:<9}  repetición {rep:>2}/{reps}  "
                           f"({time.perf_counter() - inicio:.1f} s)")
    return nuevas


# ------------------------------------------------------------------- piloto

def extrapolar(puntos, n_objetivo):
    """Ley de potencias t = c * N^p ajustada con los dos mayores tamaños.

    puntos: lista de (N, tiempo) ordenada por N. Devuelve (p, tiempo estimado).
    Es una estimación de orden de magnitud, no una medición.
    """
    (n1, t1), (n2, t2) = puntos[-2], puntos[-1]
    if t1 <= 0 or t2 <= 0 or n1 == n2:
        p = 1.0
    else:
        p = math.log(t2 / t1) / math.log(n2 / n1)
    return p, t2 * (n_objetivo / n2) ** p


def formatear_duracion(segundos):
    if segundos < 60:
        return f"{segundos:.1f} s"
    if segundos < 3600:
        return f"{segundos / 60:.1f} min"
    if segundos < 86400:
        return f"{segundos / 3600:.1f} h"
    return f"{segundos / 86400:.1f} días"


def reporte_piloto(filas, salida=print):
    agrupado = defaultdict(list)
    for f in filas:
        agrupado[(f["estructura"], f["orden_insercion"], f["operacion"],
                  f["N"])].append(f["tiempo_total_s"])
    series = defaultdict(dict)
    for (est, orden, op, n), tiempos in agrupado.items():
        series[(est, orden, op)][n] = statistics.median(tiempos)

    salida("\nEstimación del plan completo (por repetición, mediana de la piloto;")
    salida("extrapolación con ley de potencias desde los dos mayores N medidos:")
    salida("son órdenes de magnitud, no mediciones)\n")
    salida(f"{'estructura':<18}{'orden':<10}{'operación':<10}{'pend.':>6}"
           f"{'N=100.000':>12}{'N=1.000.000':>13}{'plan (30/10 rep)':>18}")
    gran_total = 0.0
    por_combinacion = defaultdict(float)
    for clave in sorted(series):
        est, orden, op = clave
        puntos = sorted(series[clave].items())
        p, _ = extrapolar(puntos, TAMANOS[-1])

        def estimado(n, puntos=puntos):
            medidos = dict(puntos)
            return medidos[n] if n in medidos else extrapolar(puntos, n)[1]

        total_plan = sum(repeticiones_plan(n) * estimado(n) for n in TAMANOS)
        gran_total += total_plan
        por_combinacion[(est, orden)] += total_plan
        salida(f"{est:<18}{orden:<10}{op:<10}{p:>6.2f}"
               f"{formatear_duracion(estimado(100_000)):>12}"
               f"{formatear_duracion(estimado(1_000_000)):>13}"
               f"{formatear_duracion(total_plan):>18}")
    salida(f"\nTiempo total estimado del plan completo: {formatear_duracion(gran_total)}")
    caras = [(c, t) for c, t in por_combinacion.items() if t > 3600]
    if caras:
        salida("Combinaciones que por sí solas superan 1 hora en el plan:")
        for (est, orden), t in sorted(caras, key=lambda x: -x[1]):
            salida(f"  - {est}, orden de inserción {orden}: {formatear_duracion(t)}")
    salida("")


def piloto(ruta_csv, repeticiones=3, m=M_DEFECTO, semilla_base=SEMILLA_BASE,
           orden_bmas=ORDEN_BMAS_DEFECTO, tamanos=TAMANOS_PILOTO,
           tamanos_abb_ordenado=TAMANOS_PILOTO_ABB_ORDENADO, salida=print):
    """Mide poco (pocas repeticiones, tamaños moderados) y estima el plan."""
    filas = []
    for orden in ORDENES_INSERCION:
        for est in ESTRUCTURAS:
            tams = (tamanos_abb_ordenado if est == "abb" and orden == "ordenado"
                    else tamanos)
            for n in tams:
                inicio = time.perf_counter()
                for rep in range(1, repeticiones + 1):
                    semilla = semilla_base + rep
                    registros = generar_estudiantes(n, orden, semilla)
                    ids = generar_ids_busqueda(n, m, PROPORCION_AUSENTES, semilla)
                    ob = orden_bmas if est == "bmas" else None
                    filas += medir_repeticion(est, ob, orden, n, rep, semilla,
                                              registros, ids)
                    gc.collect()
                salida(f"  {est:<18}{orden:<10}N={n:>9,}  "
                       f"{repeticiones} rep. en {time.perf_counter() - inicio:.1f} s")
    ruta_csv = Path(ruta_csv)
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_csv, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    reporte_piloto(filas, salida)
    return filas


# ------------------------------------------------------------------- entorno

def fijar_nucleos(texto):
    """Opcional: fija el proceso a ciertos núcleos lógicos (requiere psutil)."""
    nucleos = [int(x) for x in texto.split(",") if x.strip() != ""]
    try:
        import psutil
    except ImportError:
        raise SystemExit("--nucleos requiere psutil: pip install psutil")
    psutil.Process().cpu_affinity(nucleos)
    return nucleos


def escribir_entorno(ruta_csv, modo, parametros):
    ruta = Path(ruta_csv).with_suffix(".entorno.json")
    info = {
        "modo": modo,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "python": sys.version,
        "implementacion": platform.python_implementation(),
        "sistema": platform.platform(),
        "procesador": platform.processor(),
        "nucleos_logicos": os.cpu_count(),
        "parametros": parametros,
    }
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta


# ----------------------------------------------------------------------- CLI

def crear_parser():
    comun = argparse.ArgumentParser(add_help=False)
    comun.add_argument("--semilla", type=int, default=SEMILLA_BASE,
                       help="semilla base (la de cada repetición es base + n.º de repetición)")
    comun.add_argument("--nucleos", default=None,
                       help="núcleos lógicos a los que fijar el proceso, p. ej. 0,2,4,6 "
                            "(opcional, requiere psutil)")

    parser = argparse.ArgumentParser(
        prog="python -m src.experimentos",
        description="Experimentos de medición del Laboratorio 3.")
    sub = parser.add_subparsers(dest="modo", required=True)

    p = sub.add_parser("piloto", parents=[comun],
                       help="mide poco y estima cuánto tardaría el plan completo")
    p.add_argument("--repeticiones", type=int, default=3)
    p.add_argument("--m", type=int, default=M_DEFECTO)
    p.add_argument("--orden-bmas", type=int, default=ORDEN_BMAS_DEFECTO)
    p.add_argument("--salida", type=Path, default=DATOS / "piloto.csv")

    p = sub.add_parser("orden-bmas", parents=[comun],
                       help="experimento secundario: variar el orden del B+ con N fijo")
    p.add_argument("--n", type=int, default=N_SECUNDARIO)
    p.add_argument("--ordenes", type=int, nargs="+", default=list(ORDENES_BMAS_SECUNDARIO))
    p.add_argument("--repeticiones", type=int, default=10)
    p.add_argument("--m", type=int, default=M_DEFECTO)
    p.add_argument("--salida", type=Path, default=DATOS / "orden_bmas.csv")

    p = sub.add_parser("principal", parents=[comun],
                       help="experimento principal (reanudable con Ctrl+C)")
    p.add_argument("--tamanos", type=int, nargs="+", default=list(TAMANOS))
    p.add_argument("--estructuras", nargs="+", choices=ESTRUCTURAS,
                   default=list(ESTRUCTURAS))
    p.add_argument("--orden-insercion", nargs="+", choices=ORDENES_INSERCION,
                   default=list(ORDENES_INSERCION), dest="ordenes_insercion")
    p.add_argument("--m", type=int, default=M_DEFECTO)
    p.add_argument("--repeticiones-pequenas", type=int, default=REPS_PEQUENAS,
                   help=f"repeticiones para N <= {UMBRAL_REPETICIONES:,}")
    p.add_argument("--repeticiones-grandes", type=int, default=REPS_GRANDES,
                   help=f"repeticiones para N > {UMBRAL_REPETICIONES:,}")
    p.add_argument("--orden-bmas", type=int, default=ORDEN_BMAS_DEFECTO)
    p.add_argument("--limite-abb-ordenado", type=int, default=LIMITE_ABB_ORDENADO_DEFECTO,
                   help="mayor N con el que se mide el ABB con inserción ordenada "
                        "(0 = sin límite); fíjalo con los resultados de la piloto")
    p.add_argument("--m-reducida-lista-desordenada", type=int, default=None,
                   help=f"M menor solo para la lista desordenada con N >= "
                        f"{N_MINIMO_M_REDUCIDA:,} (documentar si se usa)")
    p.add_argument("--salida", type=Path, default=DATOS / "mediciones.csv")
    p.add_argument("--solo-plan", action="store_true",
                   help="muestra cuántas mediciones tiene el plan y termina")
    return parser


def main(argv=None):
    args = crear_parser().parse_args(argv)
    parametros = {k: (str(v) if isinstance(v, Path) else v)
                  for k, v in vars(args).items()}
    try:
        if args.nucleos:
            parametros["nucleos_fijados"] = fijar_nucleos(args.nucleos)

        if args.modo == "piloto":
            escribir_entorno(args.salida, "piloto", parametros)
            print("Piloto: mide poco y extrapola; no sustituye al experimento principal.\n")
            piloto(args.salida, args.repeticiones, args.m, args.semilla,
                   args.orden_bmas)
            print(f"Mediciones de la piloto guardadas en {args.salida}")

        elif args.modo == "orden-bmas":
            escribir_entorno(args.salida, "orden-bmas", parametros)
            nuevas = correr(args.salida, ("bmas",), ORDENES_INSERCION, (args.n,),
                            args.m, lambda n: args.repeticiones, args.semilla,
                            ordenes_bmas=tuple(args.ordenes))
            print(f"Listo: {nuevas} mediciones nuevas en {args.salida}")

        else:
            limite = args.limite_abb_ordenado or None
            plan = contar_ejecuciones(
                args.estructuras, args.ordenes_insercion, args.tamanos,
                lambda n: (args.repeticiones_pequenas if n <= UMBRAL_REPETICIONES
                           else args.repeticiones_grandes),
                (args.orden_bmas,), limite)
            print(f"El plan tiene {plan} mediciones (estructura x repetición); "
                  f"cada una incluye insertar, buscar y listar.")
            if args.solo_plan:
                return 0
            escribir_entorno(args.salida, "principal", parametros)
            nuevas = correr(
                args.salida, tuple(args.estructuras), tuple(args.ordenes_insercion),
                tuple(args.tamanos), args.m,
                lambda n: (args.repeticiones_pequenas if n <= UMBRAL_REPETICIONES
                           else args.repeticiones_grandes),
                args.semilla, ordenes_bmas=(args.orden_bmas,),
                limite_abb_ordenado=limite,
                m_reducida_lista=args.m_reducida_lista_desordenada)
            print(f"Listo: {nuevas} mediciones nuevas en {args.salida}")
    except KeyboardInterrupt:
        print("\nInterrumpido. Lo medido hasta ahora quedó guardado; "
              "vuelve a ejecutar el mismo comando para continuar.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
