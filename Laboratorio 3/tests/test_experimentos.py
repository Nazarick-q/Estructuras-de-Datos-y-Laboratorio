"""Pruebas del script de experimentos (con tamaños diminutos para que sean rápidas).

Ejecutar desde la raíz del laboratorio:

    python -m unittest discover -s tests -t . -v
"""

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import experimentos as ex
from src.generador import generar_ids_busqueda


def silencio(*_args, **_kwargs):
    pass


def leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


class TestIdsBusqueda(unittest.TestCase):
    def test_proporciones_y_rangos(self):
        n, m = 100, 1000
        ids = generar_ids_busqueda(n, m, 0.2, semilla=1)
        self.assertEqual(len(ids), m)
        ausentes = [i for i in ids if i > n]
        presentes = [i for i in ids if i <= n]
        self.assertEqual(len(ausentes), 200)
        self.assertTrue(all(n + 1 <= i <= 2 * n for i in ausentes))
        self.assertTrue(all(1 <= i <= n for i in presentes))

    def test_reproducible_y_mezclado(self):
        a = generar_ids_busqueda(500, 300, 0.2, semilla=9)
        b = generar_ids_busqueda(500, 300, 0.2, semilla=9)
        c = generar_ids_busqueda(500, 300, 0.2, semilla=10)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        # Están mezclados: los ausentes no quedan todos al final.
        self.assertTrue(any(i <= 500 for i in a[-60:]))

    def test_argumentos_invalidos(self):
        with self.assertRaises(ValueError):
            generar_ids_busqueda(0, 10)
        with self.assertRaises(ValueError):
            generar_ids_busqueda(10, 10, 1.5)


class TestExtrapolar(unittest.TestCase):
    def test_ley_de_potencias_exacta(self):
        p, estimado = ex.extrapolar([(100, 1.0), (1000, 100.0)], 10_000)
        self.assertAlmostEqual(p, 2.0)
        self.assertAlmostEqual(estimado, 10_000.0)

    def test_tiempos_nulos_no_rompen(self):
        p, estimado = ex.extrapolar([(100, 0.0), (1000, 0.0)], 10_000)
        self.assertEqual(p, 1.0)
        self.assertEqual(estimado, 0.0)

    def test_formatear_duracion(self):
        self.assertEqual(ex.formatear_duracion(5), "5.0 s")
        self.assertEqual(ex.formatear_duracion(120), "2.0 min")
        self.assertEqual(ex.formatear_duracion(7200), "2.0 h")
        self.assertEqual(ex.formatear_duracion(172800), "2.0 días")


class TestCorrer(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ruta = Path(self._tmp.name) / "mediciones.csv"

    def correr(self, **kwargs):
        argumentos = dict(
            ruta_csv=self.ruta, estructuras=ex.ESTRUCTURAS,
            ordenes_insercion=ex.ORDENES_INSERCION, tamanos=(50, 100), m=20,
            repeticiones=lambda n: 2, ordenes_bmas=(4, 8), salida=silencio)
        argumentos.update(kwargs)
        return ex.correr(**argumentos)

    def test_filas_y_columnas(self):
        nuevas = self.correr()
        # 2 tamaños x 2 órdenes x 2 repeticiones x (3 estructuras + 2 B+) = 40
        self.assertEqual(nuevas, 40)
        filas = leer(self.ruta)
        self.assertEqual(len(filas), 120)
        with open(self.ruta, newline="", encoding="utf-8") as archivo:
            self.assertEqual(next(csv.reader(archivo)), ex.COLUMNAS)
        for operacion in ("insertar", "buscar", "listar"):
            self.assertEqual(sum(f["operacion"] == operacion for f in filas), 40)
        for f in filas:
            self.assertEqual(f["M"], "20")
            self.assertGreaterEqual(float(f["tiempo_total_s"]), 0.0)
            self.assertGreaterEqual(float(f["tiempo_por_operacion_s"]), 0.0)
            if f["estructura"] == "bmas":
                self.assertIn(f["orden_bmas"], ("4", "8"))
            else:
                self.assertEqual(f["orden_bmas"], "")
            if f["estructura"] in ("abb", "bmas"):
                self.assertNotEqual(f["altura"], "")
            else:
                self.assertEqual(f["altura"], "")

    def test_tiempo_por_operacion_es_total_entre_divisor(self):
        self.correr(estructuras=("abb",), ordenes_insercion=("aleatorio",),
                    tamanos=(100,), repeticiones=lambda n: 1)
        for f in leer(self.ruta):
            divisor = 20 if f["operacion"] == "buscar" else 100
            self.assertAlmostEqual(float(f["tiempo_por_operacion_s"]),
                                   float(f["tiempo_total_s"]) / divisor)

    def test_semillas_y_alturas_del_abb(self):
        self.correr(estructuras=("abb",), tamanos=(100,), repeticiones=lambda n: 2)
        filas = [f for f in leer(self.ruta) if f["operacion"] == "insertar"]
        self.assertEqual({f["semilla"] for f in filas},
                         {str(ex.SEMILLA_BASE + 1), str(ex.SEMILLA_BASE + 2)})
        ordenado = [f for f in filas if f["orden_insercion"] == "ordenado"]
        aleatorio = [f for f in filas if f["orden_insercion"] == "aleatorio"]
        self.assertTrue(all(f["altura"] == "100" for f in ordenado))  # cadena
        self.assertTrue(all(int(f["altura"]) < 40 for f in aleatorio))

    def test_reanudacion(self):
        self.assertEqual(self.correr(repeticiones=lambda n: 1), 20)
        self.assertEqual(len(leer(self.ruta)), 60)
        self.assertEqual(self.correr(repeticiones=lambda n: 2), 20)  # solo la rep. 2
        self.assertEqual(len(leer(self.ruta)), 120)
        self.assertEqual(self.correr(repeticiones=lambda n: 2), 0)   # nada pendiente
        self.assertEqual(len(leer(self.ruta)), 120)

    def test_limite_abb_ordenado(self):
        avisos = []
        self.correr(limite_abb_ordenado=50, salida=avisos.append)
        filas = leer(self.ruta)
        abb_ord = {f["N"] for f in filas
                   if f["estructura"] == "abb" and f["orden_insercion"] == "ordenado"}
        abb_ale = {f["N"] for f in filas
                   if f["estructura"] == "abb" and f["orden_insercion"] == "aleatorio"}
        self.assertEqual(abb_ord, {"50"})
        self.assertEqual(abb_ale, {"50", "100"})
        self.assertTrue(any("ABB con inserción ordenada omitido" in a for a in avisos))

    def test_m_reducida_solo_para_lista_desordenada(self):
        self.correr(tamanos=(100,), m_reducida_lista=5, n_minimo_m_reducida=100)
        for f in leer(self.ruta):
            esperado = "5" if f["estructura"] == "lista_desordenada" else "20"
            self.assertEqual(f["M"], esperado)

    def test_encabezado_incompatible(self):
        self.ruta.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.correr()

    def test_contar_ejecuciones(self):
        args = (ex.ESTRUCTURAS, ex.ORDENES_INSERCION, (50, 100),
                lambda n: 2, (4, 8))
        self.assertEqual(ex.contar_ejecuciones(*args, None), 40)
        self.assertEqual(ex.contar_ejecuciones(*args, 50), 38)


class TestPiloto(unittest.TestCase):
    def test_piloto_pequeno_guarda_csv_e_informa(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "piloto.csv"
            salida = []
            filas = ex.piloto(ruta, repeticiones=1, m=10, tamanos=(30, 60, 120),
                              tamanos_abb_ordenado=(30, 60, 120),
                              salida=salida.append)
            # 2 órdenes x 4 estructuras x 3 tamaños x 1 repetición x 3 operaciones
            self.assertEqual(len(filas), 72)
            self.assertEqual(len(leer(ruta)), 72)
            texto = "\n".join(salida)
            self.assertIn("Estimación del plan completo", texto)
            self.assertIn("Tiempo total estimado del plan completo", texto)


class TestCLI(unittest.TestCase):
    def ejecutar(self, argumentos):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = ex.main(argumentos)
        return codigo, salida.getvalue()

    def test_principal_escribe_csv_y_entorno(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "m.csv"
            codigo, texto = self.ejecutar([
                "principal", "--tamanos", "50", "--repeticiones-pequenas", "1",
                "--m", "10", "--orden-bmas", "4", "--salida", str(ruta)])
            self.assertEqual(codigo, 0)
            self.assertIn("El plan tiene 8 mediciones", texto)  # 2 órdenes x 4 estructuras
            self.assertEqual(len(leer(ruta)), 24)
            entorno = json.loads((Path(tmp) / "m.entorno.json").read_text(encoding="utf-8"))
            self.assertEqual(entorno["modo"], "principal")
            self.assertIn("python", entorno)
            self.assertEqual(entorno["parametros"]["m"], 10)

    def test_solo_plan_no_mide(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "m.csv"
            codigo, texto = self.ejecutar(["principal", "--tamanos", "50", "100",
                                           "--solo-plan", "--salida", str(ruta)])
            self.assertEqual(codigo, 0)
            self.assertIn("El plan tiene", texto)
            self.assertFalse(ruta.exists())

    def test_modo_orden_bmas(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "b.csv"
            codigo, _ = self.ejecutar(["orden-bmas", "--n", "50", "--ordenes", "4", "8",
                                       "--repeticiones", "1", "--m", "10",
                                       "--salida", str(ruta)])
            self.assertEqual(codigo, 0)
            filas = leer(ruta)
            # 2 órdenes de inserción x 2 órdenes de B+ x 3 operaciones
            self.assertEqual(len(filas), 12)
            self.assertEqual({f["estructura"] for f in filas}, {"bmas"})
            self.assertEqual({f["orden_bmas"] for f in filas}, {"4", "8"})

    def test_modo_piloto_llama_a_piloto_con_los_argumentos(self):
        # La lógica de piloto() se prueba en TestPiloto; aquí solo el cableado del CLI.
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "p.csv"
            with mock.patch.object(ex, "piloto") as falso:
                codigo, _ = self.ejecutar(["piloto", "--repeticiones", "2", "--m", "5",
                                           "--salida", str(ruta)])
            self.assertEqual(codigo, 0)
            falso.assert_called_once_with(ruta, 2, 5, ex.SEMILLA_BASE,
                                          ex.ORDEN_BMAS_DEFECTO)
            self.assertTrue((Path(tmp) / "p.entorno.json").exists())

    def test_interrupcion_con_ctrl_c(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "m.csv"
            with mock.patch.object(ex, "correr", side_effect=KeyboardInterrupt):
                codigo, texto = self.ejecutar(["principal", "--tamanos", "50",
                                               "--salida", str(ruta)])
            self.assertEqual(codigo, 130)
            self.assertIn("quedó guardado", texto)


if __name__ == "__main__":
    unittest.main()
