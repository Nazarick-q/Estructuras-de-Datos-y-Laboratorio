"""Generador de estudiantes de prueba (reproducible con semilla).

Decisiones de diseño (acordadas para el estudio experimental):
- Los IDs son una permutación de 1 a N: únicos y consecutivos.
- Nombre = nombre + apellido, tomados de dos listas de 100 elementos y
  combinados al azar (10.000 combinaciones posibles; con N grande habrá
  nombres repetidos, lo cual no importa porque la clave es el ID).
- Edad entera entre 17 y 35; promedio entre 0.0 y 5.0 con dos decimales.
- Los registros se crean primero en orden de ID y luego, si se pide, se
  barajan: así el caso "aleatorio" y el "ordenado" contienen exactamente los
  mismos registros y solo cambia el orden de inserción.
"""

import random

from .estudiante import Estudiante

NOMBRES = (
    "Juan", "Carlos", "Andrés", "Santiago", "Sebastián", "Daniel", "David",
    "Camilo", "Felipe", "Mateo", "Nicolás", "Alejandro", "Miguel", "Luis",
    "Jorge", "Diego", "Julián", "Samuel", "Esteban", "Cristian", "Sofía",
    "Valentina", "Camila", "Isabella", "Mariana", "Daniela", "Laura",
    "Natalia", "Paula", "Andrea", "Carolina", "Juliana", "Manuela",
    "Gabriela", "Luisa", "María", "Ana", "Lucía", "Sara", "Catalina",
    "Alejandra", "Verónica", "Mónica", "Johana", "Tatiana", "Viviana",
    "Melissa", "Karen", "Diana", "Ángela", "Pedro", "Pablo", "Fernando",
    "Ricardo", "Héctor", "Óscar", "Rafael", "Manuel", "Sergio", "Alberto",
    "Gustavo", "Eduardo", "Javier", "Mauricio", "Iván", "Álvaro", "Hugo",
    "Raúl", "Rodrigo", "Leonardo", "Emilio", "Gabriel", "Tomás", "Martín",
    "Simón", "Joaquín", "Adrián", "Bruno", "Ángel", "Fabián", "Wilson",
    "Jhon", "Brayan", "Kevin", "Yesid", "Elena", "Isabel", "Patricia",
    "Marcela", "Claudia", "Liliana", "Sandra", "Beatriz", "Rosa", "Carmen",
    "Silvia", "Adriana", "Jimena", "Fernanda", "Antonia",
)

APELLIDOS = (
    "García", "Rodríguez", "Martínez", "López", "González", "Hernández",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez",
    "Díaz", "Reyes", "Morales", "Cruz", "Ortiz", "Gutiérrez", "Chávez",
    "Ramos", "Vargas", "Castillo", "Jiménez", "Moreno", "Romero", "Herrera",
    "Medina", "Aguilar", "Garza", "Castro", "Vázquez", "Fernández",
    "Mendoza", "Ruiz", "Álvarez", "Muñoz", "Rojas", "Silva", "Suárez",
    "Salazar", "Cardona", "Giraldo", "Restrepo", "Zapata", "Arango",
    "Ospina", "Londoño", "Builes", "Montoya", "Gaviria", "Mejía", "Uribe",
    "Duque", "Henao", "Marín", "Quintero", "Villa", "Correa", "Osorio",
    "Carvajal", "Valencia", "Cano", "Orozco", "Vélez", "Echeverri",
    "Bedoya", "Acevedo", "Tamayo", "Betancur", "Bustamante", "Cadavid",
    "Calle", "Escobar", "Franco", "Gallego", "Grajales", "Hoyos", "Isaza",
    "Lopera", "Maya", "Naranjo", "Ocampo", "Patiño", "Pineda", "Posada",
    "Ríos", "Sierra", "Toro", "Trujillo", "Úsuga", "Vásquez", "Yepes",
    "Zuluaga", "Cortés", "Navarro", "Peña", "Parra", "Pardo", "Ávila",
)

EDAD_MIN, EDAD_MAX = 17, 35
PROMEDIO_MIN, PROMEDIO_MAX = 0.0, 5.0

# Se construyen una sola vez; cada estudiante reutiliza una de estas cadenas
# en lugar de crear texto nuevo, lo que ahorra memoria con N grande.
NOMBRES_COMPLETOS = [f"{n} {a}" for n in NOMBRES for a in APELLIDOS]


def generar_estudiantes(n, orden="aleatorio", semilla=42):
    """Devuelve una lista de n estudiantes con IDs 1..n.

    orden="aleatorio": la lista sale barajada (orden de inserción aleatorio).
    orden="ordenado":  la lista sale en orden creciente de ID.
    """
    if n < 0:
        raise ValueError("n no puede ser negativo")
    if orden not in ("aleatorio", "ordenado"):
        raise ValueError("orden debe ser 'aleatorio' u 'ordenado'")
    rng = random.Random(semilla)
    estudiantes = [
        Estudiante(
            i,
            rng.choice(NOMBRES_COMPLETOS),
            rng.randint(EDAD_MIN, EDAD_MAX),
            round(rng.uniform(PROMEDIO_MIN, PROMEDIO_MAX), 2),
        )
        for i in range(1, n + 1)
    ]
    if orden == "aleatorio":
        rng.shuffle(estudiantes)
    return estudiantes


def generar_ids_busqueda(n, m, proporcion_ausentes=0.2, semilla=42):
    """IDs a buscar: m valores mezclados al azar.

    - Existentes: enteros al azar en 1..n (con reemplazo, para poder pedir
      más búsquedas que registros cuando n es pequeño).
    - Ausentes: enteros al azar en n+1..2n (la fracción `proporcion_ausentes`).

    Usa un generador aleatorio distinto al de los datos, derivado de la misma
    semilla, para que ambos sean reproducibles e independientes.
    """
    if n < 1:
        raise ValueError("n debe ser al menos 1")
    if m < 0 or not 0 <= proporcion_ausentes <= 1:
        raise ValueError("m no puede ser negativo y la proporción va de 0 a 1")
    rng = random.Random(semilla + 1_000_003)
    n_ausentes = round(m * proporcion_ausentes)
    ids = [rng.randint(1, n) for _ in range(m - n_ausentes)]
    ids += [rng.randint(n + 1, 2 * n) for _ in range(n_ausentes)]
    rng.shuffle(ids)
    return ids
