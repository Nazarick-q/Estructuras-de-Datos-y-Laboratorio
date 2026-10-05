"""Árbol binario de búsqueda (ABB) sin balanceo, totalmente iterativo.

Sin recursión a propósito: con IDs insertados en orden creciente el árbol
degenera en una cadena de N niveles y una versión recursiva toparía con el
límite de recursión de Python.
"""


class _Nodo:
    __slots__ = ("clave", "est", "izq", "der")

    def __init__(self, est):
        self.clave = est.id
        self.est = est
        self.izq = None
        self.der = None


class ArbolBinarioBusqueda:
    """Buscar e insertar: O(h), con h entre log N (aleatorio) y N (ordenado)."""

    def __init__(self):
        self._raiz = None
        self._n = 0

    def __len__(self):
        return self._n

    def insertar(self, estudiante):
        nuevo = _Nodo(estudiante)
        if self._raiz is None:
            self._raiz = nuevo
            self._n = 1
            return
        k = nuevo.clave
        actual = self._raiz
        while True:
            if k < actual.clave:
                if actual.izq is None:
                    actual.izq = nuevo
                    break
                actual = actual.izq
            elif k > actual.clave:
                if actual.der is None:
                    actual.der = nuevo
                    break
                actual = actual.der
            else:
                raise ValueError(f"ID duplicado: {k}")
        self._n += 1

    def buscar(self, id_buscado):
        actual = self._raiz
        while actual is not None:
            if id_buscado < actual.clave:
                actual = actual.izq
            elif id_buscado > actual.clave:
                actual = actual.der
            else:
                return actual.est
        return None

    def listar(self):
        """Recorrido inorden iterativo con pila explícita. O(N)."""
        resultado = []
        pila = []
        actual = self._raiz
        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izq
            actual = pila.pop()
            resultado.append(actual.est)
            actual = actual.der
        return resultado

    def altura(self):
        """Número de niveles del camino más largo (vacío = 0, solo raíz = 1).

        Cuesta O(N): se calcula después de construir el árbol, fuera de las
        mediciones de tiempo.
        """
        if self._raiz is None:
            return 0
        maxima = 0
        pila = [(self._raiz, 1)]
        while pila:
            nodo, nivel = pila.pop()
            if nivel > maxima:
                maxima = nivel
            if nodo.izq is not None:
                pila.append((nodo.izq, nivel + 1))
            if nodo.der is not None:
                pila.append((nodo.der, nivel + 1))
        return maxima
