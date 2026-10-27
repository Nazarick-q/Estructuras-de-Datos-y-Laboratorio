"""
Tomas Parra
HyperOctree (2^k dimensiones)
Estructuras de datos
Universidad de Antioquia
2026-2
"""

import math


class Punto:
    def __init__(self, coordenadas, data=None):
        self.coordenadas = coordenadas
        self.data = data
        self.k = len(self.coordenadas)

    def distancia(self, otro_punto):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.coordenadas, otro_punto.coordenadas)))


class HiperCubo:
    def __init__(self, centro, mitades):
        self.centro = centro
        self.mitades = mitades
        self.k = len(centro)

    def contiene(self, punto):
        for i in range(self.k):
            if not (self.centro[i] - self.mitades[i] <= punto.coordenadas[i] <= self.centro[i] + self.mitades[i]):
                return False
        return True

    def distancia_cuadrada_a(self, coordenadas):
        """Distancia al cuadrado desde unas coordenadas al hipercubo (0 si está dentro)."""
        total = 0
        for i in range(self.k):
            inferior = self.centro[i] - self.mitades[i]
            superior = self.centro[i] + self.mitades[i]
            if coordenadas[i] < inferior:
                total += (inferior - coordenadas[i]) ** 2
            elif coordenadas[i] > superior:
                total += (coordenadas[i] - superior) ** 2
        return total

    def distancia_al_cubo(self, punto):
        return math.sqrt(self.distancia_cuadrada_a(punto.coordenadas))

    def intersecta_esfera(self, centro_esfera, radio):
        return self.distancia_cuadrada_a(centro_esfera) <= radio ** 2


class HyperOctree:
    def __init__(self, limite, capacidad=8, profundidad_max=8, profundidad=0):
        self.limite = limite
        self.capacidad = capacidad
        self.profundidad_max = profundidad_max
        self.profundidad = profundidad
        self.k = limite.k
        self.puntos = []
        self.ortantes = []
        self.dividido = False

    def subdividir_en_ortantes(self):
        nuevas_mitades = [m / 2 for m in self.limite.mitades]
        for i in range(2 ** self.k):
            nuevo_centro = []
            for dimension in range(self.k):
                if (i >> dimension) & 1:
                    nuevo_centro.append(self.limite.centro[dimension] + nuevas_mitades[dimension])
                else:
                    nuevo_centro.append(self.limite.centro[dimension] - nuevas_mitades[dimension])
            nuevo_limite = HiperCubo(nuevo_centro, nuevas_mitades)
            self.ortantes.append(
                HyperOctree(nuevo_limite, self.capacidad, self.profundidad_max, self.profundidad + 1)
            )
        self.dividido = True

    def insertar(self, punto):
        if not self.limite.contiene(punto):
            return False
        if len(self.puntos) < self.capacidad or self.profundidad >= self.profundidad_max:
            self.puntos.append(punto)
            return True
        if not self.dividido:
            self.subdividir_en_ortantes()
        for ortante in self.ortantes:
            if ortante.insertar(punto):
                return True
        return False

    def busqueda_radio(self, centro, radio, encontrados=None):
        """centro: Punto. Devuelve los puntos a distancia <= radio."""
        if encontrados is None:
            encontrados = []
        if not self.limite.intersecta_esfera(centro.coordenadas, radio):
            return encontrados
        for p in self.puntos:
            if p.distancia(centro) <= radio:
                encontrados.append(p)
        if self.dividido:
            for ortante in self.ortantes:
                ortante.busqueda_radio(centro, radio, encontrados)
        return encontrados

    def vecino_mas_cercano(self, objetivo, mejor_punto=None, mejor_distancia=float('inf')):
        if self.limite.distancia_al_cubo(objetivo) > mejor_distancia:
            return mejor_punto, mejor_distancia
        for p in self.puntos:
            d = p.distancia(objetivo)
            if d < mejor_distancia:
                mejor_distancia = d
                mejor_punto = p
        if self.dividido:
            for ortante in sorted(self.ortantes, key=lambda o: o.limite.distancia_al_cubo(objetivo)):
                mejor_punto, mejor_distancia = ortante.vecino_mas_cercano(objetivo, mejor_punto, mejor_distancia)
        return mejor_punto, mejor_distancia

    def k_vecinos_mas_cercanos(self, objetivo, k):
        if k <= 0:
            return []
        heap = []
        self._k_vecinos(objetivo, k, heap, itertools.count())
        return sorted(((p, -nd) for nd, _, p in heap), key=lambda par: par[1])

    def _k_vecinos(self, objetivo, k, heap, desempate):
        if len(heap) == k and self.limite.distancia_al_cubo(objetivo) > -heap[0][0]:
            return
        for p in self.puntos:
            d = p.distancia(objetivo)
            if len(heap) < k:
                heapq.heappush(heap, (-d, next(desempate), p))
            elif d < -heap[0][0]:
                heapq.heapreplace(heap, (-d, next(desempate), p))
        if self.dividido:
            for ortante in sorted(self.ortantes, key=lambda o: o.limite.distancia_al_cubo(objetivo)):
                ortante._k_vecinos(objetivo, k, heap, desempate)