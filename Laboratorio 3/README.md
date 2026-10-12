# Laboratorio 3: Sistema de Búsqueda

## Descripción
Este laboratorio implementa y evalúa un sistema de administración de estudiantes utilizando múltiples estructuras de datos para contrastar su eficiencia empírica frente a su complejidad teórica. Se administran registros de estudiantes (ID, Nombre, Edad, Promedio) a través de cuatro enfoques de almacenamiento:
1. Lista Desordenada (Búsqueda Lineal).
2. Lista Ordenada (Búsqueda Binaria).
3. Árbol Binario de Búsqueda (ABB).
4. Árbol B+.

El sistema mide los tiempos de ejecución de las operaciones de Inserción, Búsqueda y Listado bajo escenarios de datos aleatorios y secuenciales (ordenados), exportando los resultados estadísticos a un archivo CSV y generando gráficas comparativas.

## Requisitos
* Python 3.8 o superior.
* Librerías estándar de Python: `time`, `random`, `statistics`, `sys`, `bisect`, `csv`, `gc`.
* Librería externa: `matplotlib`.

## Ejecución paso a paso

Parado en la raíz del repositorio (justo después del `git clone`), entra a esta carpeta:

```bash
cd "Laboratorio 3"
```

### 1. Ejecutar el laboratorio

```bash
python lab3.py
```

No se necesitan entradas del usuario: al ejecutarse mostrara el avance en consola, al final se generaran 3 archivos `.png` y un archivo `.csv` 


## Código de Honor y Uso de IA

En el desarrollo de este laboratorio se utilizaron herramientas de Inteligencia Artificial (Gen AI) para la generación y optimización del código fuente, el diseño del marco estadístico de medición y la producción de gráficas comparativas mediante `matplotlib`.

Como autor, certifico que asumo la responsabilidad absoluta sobre el resultado final. He verificado que los algoritmos implementan correctamente las estructuras solicitadas, que la metodología de recolección de datos (incluyendo el aislamiento del Garbage Collector y la validación cruzada) es rigurosa, y que las interpretaciones de la complejidad algorítmica ($O(N)$, $O(\log N)$, $O(N^2) $) expuestas en las gráficas corresponden fidedignamente a la teoría de estructuras de datos.
