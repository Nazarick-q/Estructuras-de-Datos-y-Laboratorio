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

## Archivos de esta carpeta
| Archivo | Rol |
| --- | --- |
| `lab3.py` | Script principal que contiene la implementación de las estructuras de datos (Listas, ABB, B+), el marco de pruebas de medición de tiempo y la generación de las gráficas del laboratorio. |
| `grafica_1_insercion.png` | Visualización comparativa del tiempo total de construcción (inserción masiva) frente al tamaño de entrada $N$. |
| `grafica_2_busqueda.png` | Visualización comparativa del tiempo promedio por búsqueda (en escala logarítmica) para contrastar la eficiencia $O(\log N)$ de estructuras balanceadas frente al $O(N)$ del peor caso. |
| `grafica_3_listar.png` | Visualización comparativa del tiempo de ejecución al recorrer y extraer todos los registros de manera secuencial y ordenada ($O(N) $). |
| `resultados_laboratorio.csv` | Registro de datos crudos en formato largo (Tidy Data) que contiene las métricas estadísticas (tiempos, medianas, desviación estándar) para auditar y reproducir el experimento en herramientas externas. |

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

## Más detalle

El formato exacto del archivo binario, la explicación de cada opción del menú, y la herramienta de diagnóstico están documentados a fondo en la **[wiki de este laboratorio](https://github.com/Nazarick-q/Estructuras-de-Datos-y-Laboratorio/wiki/Laboratorio-3)**.


## Código de Honor y Uso de IA

En el desarrollo de este laboratorio se utilizaron herramientas de Inteligencia Artificial (Gen AI) para la generación y optimización del código fuente, el diseño del marco estadístico de medición y la producción de gráficas comparativas mediante `matplotlib`.

Como autor, certifico que asumo la responsabilidad absoluta sobre el resultado final. He verificado que los algoritmos implementan correctamente las estructuras solicitadas, que la metodología de recolección de datos (incluyendo el aislamiento del Garbage Collector y la validación cruzada) es rigurosa, y que las interpretaciones de la complejidad algorítmica ($O(N)$, $O(\log N)$, $O(N^2) $) expuestas en las gráficas corresponden fidedignamente a la teoría de estructuras de datos.
