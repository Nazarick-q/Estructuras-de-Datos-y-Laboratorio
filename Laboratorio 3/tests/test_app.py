"""Pruebas del generador de datos y de la interfaz de terminal.

Ejecutar desde la raíz del laboratorio:

    python -m unittest discover -s tests -t . -v
"""

import contextlib
import io
import os
import subprocess
import sys
import unittest
from unittest import mock

from src import app
from src.generador import (EDAD_MAX, EDAD_MIN, PROMEDIO_MAX, PROMEDIO_MIN,
                           generar_estudiantes)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ejecutar_app(entradas):
    """Corre app.main() con las entradas dadas y devuelve lo que imprimió."""
    salida = io.StringIO()
    with mock.patch("builtins.input", side_effect=entradas), \
            contextlib.redirect_stdout(salida):
        app.main()
    return salida.getvalue()


class TestGenerador(unittest.TestCase):
    def test_ids_son_permutacion_de_1_a_n(self):
        for orden in ("aleatorio", "ordenado"):
            ids = [e.id for e in generar_estudiantes(300, orden)]
            self.assertEqual(sorted(ids), list(range(1, 301)))

    def test_ordenado_es_ascendente_y_aleatorio_no(self):
        ordenado = [e.id for e in generar_estudiantes(100, "ordenado")]
        aleatorio = [e.id for e in generar_estudiantes(100, "aleatorio")]
        self.assertEqual(ordenado, list(range(1, 101)))
        self.assertNotEqual(aleatorio, ordenado)

    def test_mismos_registros_en_ambos_ordenes(self):
        def firma(lista):
            return sorted((e.id, e.nombre, e.edad, e.promedio) for e in lista)
        self.assertEqual(firma(generar_estudiantes(200, "aleatorio", 7)),
                         firma(generar_estudiantes(200, "ordenado", 7)))

    def test_reproducible_con_semilla(self):
        a = [(e.id, e.nombre, e.edad, e.promedio)
             for e in generar_estudiantes(150, "aleatorio", 5)]
        b = [(e.id, e.nombre, e.edad, e.promedio)
             for e in generar_estudiantes(150, "aleatorio", 5)]
        c = [(e.id, e.nombre, e.edad, e.promedio)
             for e in generar_estudiantes(150, "aleatorio", 6)]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_rangos_de_edad_y_promedio(self):
        for e in generar_estudiantes(2000):
            self.assertTrue(EDAD_MIN <= e.edad <= EDAD_MAX)
            self.assertTrue(PROMEDIO_MIN <= e.promedio <= PROMEDIO_MAX)
            self.assertEqual(e.promedio, round(e.promedio, 2))

    def test_argumentos_invalidos(self):
        with self.assertRaises(ValueError):
            generar_estudiantes(10, "otro")
        with self.assertRaises(ValueError):
            generar_estudiantes(-1)


class TestApp(unittest.TestCase):
    def test_sesion_manual_con_abb(self):
        salida = ejecutar_app([
            "3",                                    # estructura: ABB
            "1", "2", "Ana Torres", "20", "4.5",    # insertar ID 2
            "1", "1", "Luis Mora", "21", "3,5",     # insertar ID 1 (coma decimal)
            "1", "2",                               # ID repetido
            "2", "1",                               # buscar existente
            "2", "99",                              # buscar ausente
            "3", "",                                # listar (Enter = 20)
            "0",
        ])
        self.assertIn("Ya existe un estudiante con el ID 2", salida)
        self.assertIn("No se encontró ningún estudiante con el ID 99", salida)
        # En el listado final, el ID 1 (Luis) aparece antes que el ID 2 (Ana).
        self.assertLess(salida.rfind("Luis Mora"), salida.rfind("Ana Torres"))
        self.assertIn("mostrando 2 de 2", salida)
        self.assertIn("Hasta luego", salida)

    def test_carga_de_ejemplo_con_bmas(self):
        salida = ejecutar_app([
            "4", "4",                  # B+ de orden 4
            "4", "500", "o", "",       # cargar 500 ordenados, semilla por defecto
            "5",                       # información
            "3", "5",                  # listar 5
            "0",
        ])
        self.assertIn("Se insertaron 500 estudiantes (ordenado, semilla 42)", salida)
        self.assertIn("Árbol B+ (orden 4)", salida)
        self.assertIn("Altura (niveles):", salida)
        self.assertIn("mostrando 5 de 500", salida)

    def test_validacion_de_entradas(self):
        salida = ejecutar_app([
            "9", "1",                  # opción inválida, luego lista desordenada
            "1", "abc", "-3", "7",     # ID: texto, negativo, válido
            "", "Eva Ruiz",           # nombre vacío, válido
            "200", "19",               # edad fuera de rango, válida
            "7", "3.2",                # promedio fuera de rango, válido
            "2", "7",                  # buscarlo
            "0",
        ])
        self.assertIn("Opción no válida", salida)
        self.assertIn("Escribe un número entero", salida)
        self.assertIn("El valor debe ser al menos 1", salida)
        self.assertIn("El valor no puede estar vacío", salida)
        self.assertIn("El valor debe ser como máximo 120", salida)
        self.assertIn("El valor debe estar entre 0.0 y 5.0", salida)
        self.assertIn("Eva Ruiz", salida)

    def test_aviso_abb_ordenado_grande_y_cancelacion(self):
        salida = ejecutar_app([
            "3",
            "4", "30000", "o", "", "n",   # el aviso se responde 'n'
            "0",
        ])
        self.assertIn("puede tardar mucho", salida)
        self.assertIn("Carga cancelada", salida)
        self.assertIn("Estudiantes: 0", salida)

    def test_separador_de_miles_y_cambio_de_estructura(self):
        salida = ejecutar_app([
            "2",
            "4", "1.500", "a", "",        # 1.500 -> 1500 estudiantes
            "6", "s",                      # cambiar de estructura, confirmando
            "1",                           # ahora lista desordenada
            "0",
        ])
        self.assertIn("Se insertaron 1500 estudiantes", salida)
        self.assertIn("Estructura: Lista desordenada   |   Estudiantes: 0", salida)

    def test_cargar_con_datos_existentes_no_hace_nada(self):
        salida = ejecutar_app([
            "1",
            "4", "10", "a", "",
            "4",                           # segunda carga: rechazada
            "0",
        ])
        self.assertIn("solo funciona con la estructura vacía", salida)
        self.assertIn("Estudiantes: 10", salida)

    def test_fin_de_entrada_no_rompe(self):
        with mock.patch("builtins.input", side_effect=EOFError), \
                contextlib.redirect_stdout(io.StringIO()) as salida:
            app.main()
        self.assertIn("Hasta luego", salida.getvalue())

    def test_main_py_se_ejecuta_como_script_desde_cualquier_carpeta(self):
        # Equivale al botón ▶ de VS Code sobre main.py.
        entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
        resultado = subprocess.run(
            [sys.executable, os.path.join(RAIZ, "main.py")],
            input="3\n0\n", capture_output=True, text=True,
            encoding="utf-8", env=entorno, cwd=os.path.dirname(RAIZ))
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Hasta luego", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
