#Laboratorio 2 - Estrcuturas de datos y laboratorio
#Jose Tomas Parra Patiño
#UdeA - 2026

import hashlib

def sha256(data: str) -> str:
    """Calcula el hash SHA-256."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

class MerkleTreeEngine:
    """Motor del Árbol de Merkle (listas anidadas y reconstrucción al vuelo)."""

    @staticmethod
    def build_tree_levels(data_blocks: list[str]) -> list[list[str]]:
        if not data_blocks:
            return []

        levels = [[sha256(block) for block in data_blocks]]

        while len(levels[-1]) > 1:
            current_level = list(levels[-1])
            if len(current_level) % 2 != 0:
                current_level.append(current_level[-1])

            next_level = []
            for i in range(0, len(current_level), 2):
                next_level.append(sha256(current_level[i] + current_level[i + 1]))

            levels.append(next_level)

        return levels

    @classmethod
    def compute_root(cls, data_blocks: list[str]) -> str:
        levels = cls.build_tree_levels(data_blocks)
        return levels[-1][0] if levels else ""

    @classmethod
    def get_proof(cls, data_blocks: list[str], index: int) -> list[tuple[str, str]]:
        levels = cls.build_tree_levels(data_blocks)
        proof = []

        for level in levels[:-1]:
            working_level = list(level)
            if len(working_level) % 2 != 0:
                working_level.append(working_level[-1])

            is_right_child = index % 2 == 1
            sibling_index = index - 1 if is_right_child else index + 1
            direction = "LEFT" if is_right_child else "RIGHT"

            proof.append((working_level[sibling_index], direction))
            index //= 2

        return proof

    @staticmethod
    def verify_proof(data_block: str, proof: list[tuple[str, str]], expected_root: str) -> bool:
        current_hash = sha256(data_block)
        for sibling_hash, direction in proof:
            if direction == "LEFT":
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash
            current_hash = sha256(combined)

        return current_hash == expected_root



# EXPERIMENTOS

if __name__ == "__main__":
    print("=== LABORATORIO 2: ÁRBOL DE MERKLE ===")

    # 1. crear las 5 transacciones simuladas
    datos = [
        "T1",
        "T2",
        "T3",
        "T4",
        "T5",
    ]

    print("\n--- Transacciones ---")
    for i in range(len(datos)):
        print(f"Transacción {i + 1} (índice {i}): {datos[i]}")

    # 2. construir el árbol y mostrar la raíz
    root_almacenada = MerkleTreeEngine.compute_root(datos)
    print("\n--- Merkle Root original ---")
    print(f">> {root_almacenada}")

    # 3. mostrar la estructura de niveles (de la raíz hacia las hojas)
    niveles = MerkleTreeEngine.build_tree_levels(datos)
    print("\n--- Estructura por niveles ---")
    for i, lvl in enumerate(reversed(niveles)):
        profundidad = len(niveles) - 1 - i
        print(f" Nivel {profundidad}: {[h[:12] + '...' for h in lvl]}")

    # 4. modificar una transacción y veo si cambia la raíz
    datos_modificados = datos.copy()
    datos_modificados[1] = "T2M"

    nueva_root = MerkleTreeEngine.compute_root(datos_modificados)
    print("\n--- Modificar la transacción 2 ---")
    print(f"Merkle Root original: {root_almacenada}")
    print(f"Merkle Root nueva:    {nueva_root}")
    print(f"¿Son iguales?: {root_almacenada == nueva_root} (efecto avalancha verificado)")

    # 5. prueba de inclusión de la transacción 3 (índice 2)
    prueba = MerkleTreeEngine.get_proof(datos, 2)
    print("\n--- Prueba de inclusión de la transacción 3 ---")
    print(f"La prueba tiene {len(prueba)} hashes de hermanos:")
    for hermano, direccion in prueba:
        print(f"  {direccion}: {hermano[:12]}...")

    # 6. verificar con el dato correcto
    dato_correcto = datos[2]
    es_valido = MerkleTreeEngine.verify_proof(dato_correcto, prueba, root_almacenada)
    print(f"\nDato correcto:   '{dato_correcto}'")
    print(f"Resultado: {'VALIDO (pertenece al árbol)' if es_valido else 'INVALIDO'}")

    # 7. verificar con un dato incorrecto (debe fallar)
    dato_incorrecto = "T3M"
    es_valido = MerkleTreeEngine.verify_proof(dato_incorrecto, prueba, root_almacenada)
    print(f"\nDato incorrecto: '{dato_incorrecto}'")
    print(f"Resultado: {'VALIDO (pertenece al árbol)' if es_valido else 'INVALIDO (dato alterado o incorrecto)'}")
