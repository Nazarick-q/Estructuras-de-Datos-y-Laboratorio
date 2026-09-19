# Labo 2 — Árbol de Merkle

Implementa un Árbol de Merkle en Python usando SHA-256: construye el árbol a partir de un conjunto de transacciones, calcula la Merkle Root, detecta modificaciones y genera y verifica pruebas de inclusión. Documentación completa del diseño y de cada función en la wiki: **[Laboratorio 2](https://github.com/Nazarick-q/Estructuras-de-Datos-y-Laboratorio/wiki/Laboratorio-2)**.

## Requisitos

- **Python 3.9 o superior**
- No necesita instalar librerías externas: solo usa `hashlib`, que ya viene con Python.

## Archivos de esta carpeta

| Archivo | Rol |
|---|---|
| `Labo2ED.py` | Motor del Árbol de Merkle y experimentos del laboratorio |

## Ejecución paso a paso

Parado en la raíz del repositorio (justo después del `git clone`), entra a esta carpeta:

```bash
cd "Laboratorio 2"
```

### 1. Ejecutar el laboratorio

```bash
python Labo2ED.py
```

No necesita entrada del usuario: al ejecutarse corre los 5 experimentos y muestra el resultado de cada uno en consola.

### 2. Qué debes ver en consola

1. Las 5 transacciones simuladas (`T1` a `T5`).
2. La **Merkle Root** original y la estructura del árbol por niveles.
3. La raíz nueva después de modificar la transacción 2, con `¿Son iguales?: False`.
4. La prueba de inclusión de la transacción 3 (3 hashes de hermanos).
5. Verificación con el dato correcto (`T3`) → `VALIDO`.
6. Verificación con un dato incorrecto (`T3M`) → `INVALIDO`.

## Más detalle

La estructura del árbol, la regla de duplicar el último nodo cuando hay cantidad impar, el funcionamiento de la prueba de inclusión y la explicación de cada experimento están documentados a fondo en la **[wiki de este laboratorio](https://github.com/Nazarick-q/Estructuras-de-Datos-y-Laboratorio/wiki/Laboratorio-2)**.
