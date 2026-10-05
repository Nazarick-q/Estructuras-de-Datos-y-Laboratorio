"""Registro de estudiante usado por todas las estructuras."""


class Estudiante:
    """Registro con ID único, nombre, edad y promedio.

    Se usa __slots__ para reducir la memoria por objeto: en los
    experimentos se crean hasta un millón de registros.
    """

    __slots__ = ("id", "nombre", "edad", "promedio")

    def __init__(self, id, nombre, edad, promedio):
        self.id = id
        self.nombre = nombre
        self.edad = edad
        self.promedio = promedio

    def __repr__(self):
        return (f"Estudiante(id={self.id}, nombre={self.nombre!r}, "
                f"edad={self.edad}, promedio={self.promedio})")
