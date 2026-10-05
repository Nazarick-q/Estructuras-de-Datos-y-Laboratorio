"""Árbol B+ implementado desde cero (inserción, búsqueda y listado).

Convención de ORDEN (m): máximo de hijos de un nodo interno.
    - Un nodo interno tiene hasta m-1 llaves y m hijos.
    - Una hoja guarda hasta m-1 registros.
    - Un nodo se divide cuando llega a m llaves (desbordamiento).

En un nodo interno, llaves[i] es la menor llave del subárbol hijos[i+1]:
una llave k baja por el hijo número "cantidad de llaves <= k".

Las hojas están enlazadas (siguiente), por lo que listar recorre solo las
hojas, en orden. No hay borrado: el laboratorio no lo pide.

La búsqueda dentro de cada nodo es binaria y está escrita a mano
(ver busqueda.py), con la misma justificación que en las listas.
"""

from .busqueda import limite_inferior, limite_superior


class _Hoja:
    __slots__ = ("llaves", "registros", "siguiente")

    def __init__(self):
        self.llaves = []
        self.registros = []
        self.siguiente = None


class _Interno:
    __slots__ = ("llaves", "hijos")

    def __init__(self):
        self.llaves = []
        self.hijos = []


class ArbolBMas:
    def __init__(self, orden=32):
        if orden < 3:
            raise ValueError("El orden del árbol B+ debe ser al menos 3")
        self.orden = orden
        self._raiz = _Hoja()
        self._n = 0

    def __len__(self):
        return self._n

    def buscar(self, id_buscado):
        nodo = self._raiz
        while type(nodo) is _Interno:
            nodo = nodo.hijos[limite_superior(nodo.llaves, id_buscado)]
        pos = limite_inferior(nodo.llaves, id_buscado)
        if pos < len(nodo.llaves) and nodo.llaves[pos] == id_buscado:
            return nodo.registros[pos]
        return None

    def insertar(self, estudiante):
        k = estudiante.id

        # 1) Bajar hasta la hoja, recordando el camino (padre, índice del hijo).
        camino = []
        nodo = self._raiz
        while type(nodo) is _Interno:
            i = limite_superior(nodo.llaves, k)
            camino.append((nodo, i))
            nodo = nodo.hijos[i]

        # 2) Insertar en la hoja.
        pos = limite_inferior(nodo.llaves, k)
        if pos < len(nodo.llaves) and nodo.llaves[pos] == k:
            raise ValueError(f"ID duplicado: {k}")
        nodo.llaves.insert(pos, k)
        nodo.registros.insert(pos, estudiante)
        self._n += 1
        if len(nodo.llaves) < self.orden:
            return

        # 3) Dividir la hoja: la llave del medio se COPIA hacia el padre.
        mitad = len(nodo.llaves) // 2
        derecha = _Hoja()
        derecha.llaves = nodo.llaves[mitad:]
        derecha.registros = nodo.registros[mitad:]
        del nodo.llaves[mitad:]
        del nodo.registros[mitad:]
        derecha.siguiente = nodo.siguiente
        nodo.siguiente = derecha
        llave_subida = derecha.llaves[0]
        izq, der = nodo, derecha

        # 4) Propagar hacia arriba mientras haya desbordamiento.
        while True:
            if not camino:
                nueva_raiz = _Interno()
                nueva_raiz.llaves = [llave_subida]
                nueva_raiz.hijos = [izq, der]
                self._raiz = nueva_raiz
                return
            padre, i = camino.pop()
            padre.llaves.insert(i, llave_subida)
            padre.hijos.insert(i + 1, der)
            if len(padre.llaves) < self.orden:
                return
            # División de nodo interno: la llave del medio SUBE (no se copia).
            mitad = len(padre.llaves) // 2
            llave_subida = padre.llaves[mitad]
            nuevo = _Interno()
            nuevo.llaves = padre.llaves[mitad + 1:]
            nuevo.hijos = padre.hijos[mitad + 1:]
            del padre.llaves[mitad:]
            del padre.hijos[mitad + 1:]
            izq, der = padre, nuevo

    def listar(self):
        """Baja a la hoja más a la izquierda y recorre las hojas enlazadas."""
        nodo = self._raiz
        while type(nodo) is _Interno:
            nodo = nodo.hijos[0]
        resultado = []
        while nodo is not None:
            resultado.extend(nodo.registros)
            nodo = nodo.siguiente
        return resultado

    def altura(self):
        """Niveles del árbol (solo hoja raíz = 1). Todas las hojas están a la misma profundidad."""
        nivel = 1
        nodo = self._raiz
        while type(nodo) is _Interno:
            nodo = nodo.hijos[0]
            nivel += 1
        return nivel
