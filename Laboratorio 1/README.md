# Labo 1 — Matriz binaria 100.000 x 100.000

Genera y consulta una matriz binaria masiva almacenada en un formato compacto de acceso aleatorio, sin necesidad de cargarla completa en memoria. Documentación completa del diseño y formato de archivo en la wiki: **[Laboratorio 1](https://github.com/Nazarick-q/Estructuras-de-Datos-y-Laboratorio/wiki/Laboratorio-1)**.

## Requisitos

- **JDK 17 o superior**
- **Espacio en disco:** el generador crea un archivo `matriz_100k.bin` de **~1.25 GB** — asegúrate de tener eso disponible antes de ejecutarlo.

## Archivos de esta carpeta

| Archivo | Rol |
|---|---|
| `Labo1ED.java` | Genera `matriz_100k.bin` |
| `Labo1_2.java` | Lee y consulta la matriz (menú interactivo) |
| `Diagnostico.java` | Verifica que el `.bin` tenga el formato correcto |

## Ejecución paso a paso

Parado en la raíz del repositorio (justo después del `git clone`), entra a esta carpeta:

```bash
cd "Laboratorio 1"
```
### 1. Generar la matriz

```bash
javac Labo1ED.java
java Labo1ED
```

Espera a que termine — imprime `Listo en X.X s` y el tamaño final en disco al terminar.

### 2. (Opcional) Verificar que el archivo se generó bien

```bash
javac Diagnostico.java
java Diagnostico
```

Debe mostrar `Tamano exacto: 1250100016 bytes`, con los primeros bytes en `FF` y el separador en `00`.

### 3. Consultar la matriz

```bash
javac Labo1_2.java
java Labo1_2
```

Se abre un menú interactivo para leer filas, columnas, intervalos, un dato puntual, o un chunk. Cada consulta sobrescribe dos archivos:

- `info_carga.txt` — resumen de lo cargado (cuántas filas/columnas y cuáles).
- `datos_cargados.txt` — los valores cargados en esa consulta.

## Más detalle

El formato exacto del archivo binario, la explicación de cada opción del menú, y la herramienta de diagnóstico están documentados a fondo en la **[wiki de este laboratorio](https://github.com/Nazarick-q/Estructuras-de-Datos-y-Laboratorio/wiki/Laboratorio-1)**.
