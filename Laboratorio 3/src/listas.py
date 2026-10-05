"""Dos variantes de lista sobre la `list` nativa de Python (arreglo dinámico).

Interfaz común a todas las estructuras del laboratorio:
    insertar(estudiante), buscar(id) -> Estudiante | None,
    listar() -> lista de estudiantes en orden ascendente de ID, len(estructura).

Precondición general: los IDs son únicos.
"""

from operator import attrgetter

from .busqueda import busqueda_lineal, limite_inferior_estudiantes


class ListaDesordenada:
    """Inserta al final (O(1)) y busca recorriendo todo (O(N)).

    No verifica duplicados al insertar: hacerlo costaría O(N) y cambiaría la
    complejidad de la inserción. Se asume que los IDs son únicos.
    """

    def __init__(self):
        self._datos = []

    def __len__(self):
        return len(self._datos)

    def insertar(self, estudiante):
        self._datos.append(estudiante)

    def buscar(self, id_buscado):
        return busqueda_lineal(self._datos, id_buscado)

    def listar(self):
        # Hay que ordenar en cada listado: O(N log N).
        return sorted(self._datos, key=attrgetter("id"))


class ListaOrdenada:
    """Mantiene la lista ordenada por ID.

    Buscar es O(log N) con búsqueda binaria; insertar es O(N) porque hay que
    desplazar elementos (aunque el desplazamiento lo hace C internamente);
    listar es O(N).
    """

    def __init__(self):
        self._datos = []

    def __len__(self):
        return len(self._datos)

    def insertar(self, estudiante):
        i = limite_inferior_estudiantes(self._datos, estudiante.id)
        if i < len(self._datos) and self._datos[i].id == estudiante.id:
            raise ValueError(f"ID duplicado: {estudiante.id}")
        self._datos.insert(i, estudiante)

    def buscar(self, id_buscado):
        i = limite_inferior_estudiantes(self._datos, id_buscado)
        if i < len(self._datos) and self._datos[i].id == id_buscado:
            return self._datos[i]
        return None

    def listar(self):
        return list(self._datos)
