"""Pruebas de corrección. Ejecutar desde la raíz del repositorio:

    python -m unittest tests.test_estructuras -v
"""

import random
import unittest

from src.abb import ArbolBinarioBusqueda, _Nodo
from src.arbol_bmas import ArbolBMas, _Hoja
from src.estudiante import Estudiante
from src.listas import ListaDesordenada, ListaOrdenada


def crear(id_):
    return Estudiante(id_, f"Nombre{id_}", 20, 3.5)


def permutacion(n, semilla=0):
    ids = list(range(1, n + 1))
    random.Random(semilla).shuffle(ids)
    return ids


FABRICAS = {
    "lista_desordenada": ListaDesordenada,
    "lista_ordenada": ListaOrdenada,
    "abb": ArbolBinarioBusqueda,
    "bmas_3": lambda: ArbolBMas(3),
    "bmas_4": lambda: ArbolBMas(4),
    "bmas_5": lambda: ArbolBMas(5),
    "bmas_8": lambda: ArbolBMas(8),
    "bmas_32": lambda: ArbolBMas(32),
}

# Estructuras que detectan IDs duplicados sin costo adicional.
CON_DETECCION_DUPLICADOS = [
    "lista_ordenada", "abb", "bmas_3", "bmas_4", "bmas_5", "bmas_8", "bmas_32",
]


class TestComunes(unittest.TestCase):
    def test_estructura_vacia(self):
        for nombre, fabrica in FABRICAS.items():
            with self.subTest(nombre):
                e = fabrica()
                self.assertEqual(len(e), 0)
                self.assertIsNone(e.buscar(1))
                self.assertEqual(e.listar(), [])

    def test_insertar_buscar_listar(self):
        for nombre, fabrica in FABRICAS.items():
            for n in (1, 2, 10, 500):
                with self.subTest(estructura=nombre, n=n):
                    e = fabrica()
                    ids = permutacion(n)
                    for i in ids:
                        e.insertar(crear(i))
                    self.assertEqual(len(e), n)
                    for i in ids:
                        self.assertEqual(e.buscar(i).id, i)
                    for ausente in (0, -5, n + 1, 2 * n):
                        self.assertIsNone(e.buscar(ausente))
                    self.assertEqual([x.id for x in e.listar()],
                                     list(range(1, n + 1)))

    def test_insercion_ascendente_y_descendente(self):
        for nombre, fabrica in FABRICAS.items():
            for orden_ids in (range(1, 301), range(300, 0, -1)):
                with self.subTest(estructura=nombre, primero=orden_ids[0]):
                    e = fabrica()
                    for i in orden_ids:
                        e.insertar(crear(i))
                    self.assertEqual([x.id for x in e.listar()],
                                     list(range(1, 301)))
                    self.assertEqual(e.buscar(150).id, 150)

    def test_duplicados(self):
        for nombre in CON_DETECCION_DUPLICADOS:
            with self.subTest(nombre):
                e = FABRICAS[nombre]()
                for i in permutacion(50):
                    e.insertar(crear(i))
                with self.assertRaises(ValueError):
                    e.insertar(crear(25))
                self.assertEqual(len(e), 50)

    def test_mismos_resultados_entre_estructuras(self):
        ids = random.Random(7).sample(range(1, 10_000), 1_000)
        consultas = random.Random(8).sample(range(1, 10_000), 500)
        estructuras = {n: f() for n, f in FABRICAS.items()}
        for e in estructuras.values():
            for i in ids:
                e.insertar(crear(i))
        referencia = sorted(ids)
        conjunto = set(ids)
        for nombre, e in estructuras.items():
            with self.subTest(nombre):
                self.assertEqual([x.id for x in e.listar()], referencia)
                for q in consultas:
                    r = e.buscar(q)
                    if q in conjunto:
                        self.assertEqual(r.id, q)
                    else:
                        self.assertIsNone(r)


class TestABB(unittest.TestCase):
    def test_altura_ordenado_vs_aleatorio(self):
        n = 2000
        ordenado = ArbolBinarioBusqueda()
        for i in range(1, n + 1):
            ordenado.insertar(crear(i))
        self.assertEqual(ordenado.altura(), n)  # degenera en una cadena

        aleatorio = ArbolBinarioBusqueda()
        for i in permutacion(n):
            aleatorio.insertar(crear(i))
        self.assertLess(aleatorio.altura(), 60)  # del orden de log N

    def test_altura_casos_pequenos(self):
        arbol = ArbolBinarioBusqueda()
        self.assertEqual(arbol.altura(), 0)
        arbol.insertar(crear(5))
        self.assertEqual(arbol.altura(), 1)

    def test_cadena_profunda_sin_recursion(self):
        # Se construye la cadena a mano (insertar 200.000 ordenados costaría
        # ~2*10^10 pasos) para comprobar que altura, listar y buscar no
        # dependen de la recursión y que liberar el árbol no falla.
        n = 200_000
        arbol = ArbolBinarioBusqueda()
        arbol._raiz = actual = _Nodo(crear(1))
        for i in range(2, n + 1):
            nuevo = _Nodo(crear(i))
            actual.der = nuevo
            actual = nuevo
        arbol._n = n
        self.assertEqual(arbol.altura(), n)
        self.assertEqual(len(arbol.listar()), n)
        self.assertEqual(arbol.buscar(n).id, n)
        del arbol, actual, nuevo


def verificar_bmas(caso, arbol):
    """Comprueba los invariantes estructurales del árbol B+."""
    m = arbol.orden
    hojas = []  # (hoja, profundidad) en orden de izquierda a derecha

    def rec(nodo, prof, es_raiz, inf, sup):
        llaves = nodo.llaves
        caso.assertEqual(llaves, sorted(llaves))
        caso.assertLessEqual(len(llaves), m - 1)
        for k in llaves:
            if inf is not None:
                caso.assertGreaterEqual(k, inf)
            if sup is not None:
                caso.assertLess(k, sup)
        if isinstance(nodo, _Hoja):
            if not es_raiz:
                caso.assertGreaterEqual(len(llaves), m // 2)
            hojas.append((nodo, prof))
            return
        caso.assertEqual(len(nodo.hijos), len(llaves) + 1)
        minimo = 1 if es_raiz else (m + 1) // 2 - 1
        caso.assertGreaterEqual(len(llaves), minimo)
        limites = [inf] + llaves + [sup]
        for i, hijo in enumerate(nodo.hijos):
            rec(hijo, prof + 1, False, limites[i], limites[i + 1])

    rec(arbol._raiz, 1, True, None, None)
    caso.assertEqual({p for _, p in hojas}, {arbol.altura()})
    for (a, _), (b, _) in zip(hojas, hojas[1:]):
        caso.assertIs(a.siguiente, b)
    caso.assertIsNone(hojas[-1][0].siguiente)


class TestBMas(unittest.TestCase):
    def test_invariantes_varios_ordenes_y_secuencias(self):
        secuencias = {
            "aleatoria": permutacion(1500, semilla=3),
            "ascendente": list(range(1, 1501)),
            "descendente": list(range(1500, 0, -1)),
        }
        for orden in (3, 4, 5, 6, 7, 8, 16, 32, 64):
            for nombre, ids in secuencias.items():
                with self.subTest(orden=orden, secuencia=nombre):
                    arbol = ArbolBMas(orden)
                    for i in ids:
                        arbol.insertar(crear(i))
                        if len(arbol) % 100 == 0:
                            verificar_bmas(self, arbol)
                    verificar_bmas(self, arbol)

    def test_orden_invalido(self):
        with self.assertRaises(ValueError):
            ArbolBMas(2)

    def test_altura_crece_poco(self):
        arbol = ArbolBMas(32)
        for i in permutacion(20_000):
            arbol.insertar(crear(i))
        self.assertLessEqual(arbol.altura(), 4)


if __name__ == "__main__":
    unittest.main()
