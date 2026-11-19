"""Práctica 2, paso 2: buscar las 5 imágenes más parecidas a una dada.

La consulta no busca por igualdad (WHERE clase = ...), sino por distancia:
ordena todas las imágenes por cercanía al vector de consulta y se queda con 5.

Uso:
    python practica2_pgvector/02_buscar_similares.py              # consulta img000042
    python practica2_pgvector/02_buscar_similares.py img001234
"""
import sys
import time

from conexion import conectar

consulta_id = sys.argv[1] if len(sys.argv) > 1 else "img000042"

SQL = """
SELECT id, clase, embedding <-> %(v)s AS distancia
FROM imagen
WHERE id <> %(id)s
ORDER BY embedding <-> %(v)s
LIMIT 5
"""

con = conectar()
fila = con.execute("SELECT clase, embedding FROM imagen WHERE id = %s", [consulta_id]).fetchone()
if fila is None:
    sys.exit(f"No existe la imagen {consulta_id}. ¿Corriste 01_cargar_vectores.py?")
clase, vector = fila

print(f"Imagen de consulta: {consulta_id} (clase {clase})\n")
print(SQL.strip(), "\n")

inicio = time.perf_counter()
resultados = con.execute(SQL, {"v": vector, "id": consulta_id}).fetchall()
ms = (time.perf_counter() - inicio) * 1000

print(f"{'id':12} {'clase':6} distancia")
for id_, clase_r, distancia in resultados:
    print(f"{id_:12} {clase_r:6} {distancia:.4f}")
print(f"\nTiempo: {ms:.0f} ms")

# Cómo la resolvió PostgreSQL
plan = con.execute("EXPLAIN " + SQL, {"v": vector, "id": consulta_id}).fetchall()
usa_indice = any("hnsw" in linea[0].lower() or "Index Scan" in linea[0] for linea in plan)
print("Plan:", "usa el índice HNSW" if usa_indice else "recorre toda la tabla (Seq Scan) y ordena")
