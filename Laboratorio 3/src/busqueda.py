"""Algoritmos de búsqueda escritos a mano (bucles explícitos en Python).

No se usa `in`, `index` ni `bisect`: esas funciones corren en C y darían
a las listas una ventaja constante injusta frente a los árboles, que están
escritos en Python puro. Así las cuatro estructuras se miden en igualdad
de condiciones.
"""


def busqueda_lineal(estudiantes, id_buscado):
    """Recorre la lista completa. O(N). Devuelve el estudiante o None."""
    for est in estudiantes:
        if est.id == id_buscado:
            return est
    return None


def limite_inferior_estudiantes(estudiantes, id_buscado):
    """Búsqueda binaria sobre una lista de Estudiante ordenada por ID.

    Devuelve el primer índice i con estudiantes[i].id >= id_buscado
    (len(estudiantes) si todos son menores). O(log N).
    """
    bajo = 0
    alto = len(estudiantes)
    while bajo < alto:
        medio = (bajo + alto) // 2
        if estudiantes[medio].id < id_buscado:
            bajo = medio + 1
        else:
            alto = medio
    return bajo


def limite_inferior(llaves, k):
    """Primer índice i con llaves[i] >= k, sobre una lista de enteros ordenada."""
    bajo = 0
    alto = len(llaves)
    while bajo < alto:
        medio = (bajo + alto) // 2
        if llaves[medio] < k:
            bajo = medio + 1
        else:
            alto = medio
    return bajo


def limite_superior(llaves, k):
    """Primer índice i con llaves[i] > k, sobre una lista de enteros ordenada.

    Equivale a contar cuántas llaves son <= k.
    """
    bajo = 0
    alto = len(llaves)
    while bajo < alto:
        medio = (bajo + alto) // 2
        if llaves[medio] <= k:
            bajo = medio + 1
        else:
            alto = medio
    return bajo
