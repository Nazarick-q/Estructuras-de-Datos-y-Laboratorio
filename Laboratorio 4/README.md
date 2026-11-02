# Laboratorio 4: HyperOctree

## Descripción
Este laboratorio implementa un **HyperOctree**, una generalización del quadtree (2D) y del octree (3D) a `k` dimensiones, donde cada nodo se subdivide en `2^k` ortantes. La estructura se usa para resolver consultas espaciales sobre un conjunto de puntos (por ejemplo, entregas en un mapa de 10000 m × 10000 m):

1. **Búsqueda por radio:** todos los puntos a distancia menor o igual a `r` de una ubicación dada.
2. **Vecino más cercano:** el punto más próximo a una ubicación dada.

Además, se contrasta su eficiencia empírica frente a la **fuerza bruta** (recorrido lineal de todos los puntos), midiendo tiempos de consulta y de construcción al variar el número de puntos `N` y la dimensión `k`. Todas las consultas del árbol se validan contra la fuerza bruta para garantizar que devuelven el mismo resultado.

## Requisitos
* Python 3.8 o superior.
* Librerías estándar de Python: `math`, `heapq`, `itertools`, `os`, `random`, `time`, `statistics`, `collections`.
* Librería externa: `matplotlib`.

```bash
pip install matplotlib
```

## Escenario de prueba del laboratorio
Las pruebas generales usan datos fijos:

| Parámetro | Valor |
|---|---|
| Espacio | Hipercubo centrado en el origen con semiancho 10.000, es decir `[-10000, 10000]` en cada eje |
| Ubicación de referencia | Centro del espacio, `(0, 0)` |
| Radio de búsqueda | 500 |
| Dimensión | `k = 2` |
| Puntos | 10.000 generados con distribución uniforme (semilla `31102025`) |
| Capacidad del bucket | 16 |

## Ejecución paso a paso

Parado en la raíz del repositorio (justo después del `git clone`), entra a esta carpeta:

```bash
cd "Laboratorio 4"
```

### 1. Pruebas visuales

```bash
python test.py
```

Ejecuta el vecino más cercano y la búsqueda por radio, comprueba el resultado contra fuerza bruta (si no coincide, el programa se detiene con un error) y guarda `vecino_mas_cercano.png` y `busqueda_radio.png`. Cada figura también se muestra en una ventana de `matplotlib`; ciérrala para continuar con la siguiente.

### 2. Benchmark y análisis

```bash
python analisis.py
```

No se necesitan entradas del usuario. Al ejecutarse muestra el avance en consola: la tabla de tiempos por consulta y el número de consultas. Al final genera las gráficas `.png` indicadas arriba.

La corrida completa (`N` hasta 300000) puede tardar varios minutos, sobre todo por la fuerza bruta. Antes de medir, el script verifica que el árbol y la fuerza bruta devuelven los mismos resultados.

## Parámetros configurables
En análisis (`analisis.py`) y test (`test.py`) hay parámetros configurables, los cuales están marcados con commits


## Código de Honor y Uso de IA

En el desarrollo de este laboratorio se utilizaron herramientas de Inteligencia Artificial (Gen AI) como apoyo para revisar y mejorar el script de análisis (`analisis.py`) y test (`test.py`), en la producción de gráficas comparativas mediante `matplotlib`.
También en la creación de la estructura de la documentación base (README y Wiki).

Como autor, certifico que asumo la responsabilidad absoluta sobre el resultado final. He verificado que las estructuras y consultas implementadas funcionan correctamente, que la comparación con la fuerza bruta es justa y reproducible, y que las interpretaciones expuestas en las gráficas corresponden a la teoría de estructuras de datos.

## Disclaimer: uso de código y material de referencia

Para la elaboración de este laboratorio me basé en código, documentación y artículos de terceros como referencia. Estas fuentes se consultaron para comprender el funcionamiento de los árboles de subdivisión espacial (quadtree, octree y su generalización a `k` dimensiones) y para guiar el diseño de la implementación. No pretendo atribuirme la autoría de las ideas y algoritmos originales descritos en ellas; cualquier similitud con esos materiales se debe a que fueron utilizados como base.

**Fuentes consultadas:**

* [hypoct (repositorio de klho)](https://github.com/klho/hypoct)
* [hypoct: documentación, visión general algorítmica](https://klho.github.io/hypoct/doc/html/intro.html#algorithmic-overview)
* [Quadtree, parte 1: fundamentos (SciPython)](https://scipython.com/blog/quadtree-1-background/)
* [Quadtree, parte 2: implementación en Python (SciPython)](https://scipython.com/blog/quadtrees-2-implementation-in-python/)
* [Ortante (Wikipedia)](https://es.wikipedia.org/wiki/Ortante)
* [Árbol octal (Wikipedia)](https://es.wikipedia.org/wiki/%C3%81rbol_octal)
* [Quadtree (Wikipedia)](https://es.wikipedia.org/wiki/Quadtree)
* [Árbol kd (Wikipedia)](https://es.wikipedia.org/wiki/%C3%81rbol_kd)
