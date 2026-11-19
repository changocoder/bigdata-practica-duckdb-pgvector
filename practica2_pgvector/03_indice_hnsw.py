"""Práctica 2, paso 3: crear un índice HNSW y comparar.

Sin índice, PostgreSQL calcula la distancia contra todas las filas (búsqueda exacta).
Con HNSW recorre un grafo de vecinos y revisa solo una parte (búsqueda aproximada):
es mucho más rápido, pero puede devolver algún vecino distinto al exacto.

Uso:
    python practica2_pgvector/03_indice_hnsw.py
"""
import statistics
import time

from conexion import conectar

SQL = """
SELECT id FROM imagen
WHERE id <> %(id)s
ORDER BY embedding <-> %(v)s
LIMIT 5
"""


def buscar_todas(con, consultas):
    resultados, tiempos = {}, []
    for qid in consultas:
        v, = con.execute("SELECT embedding FROM imagen WHERE id = %s", [qid]).fetchone()
        inicio = time.perf_counter()
        filas = con.execute(SQL, {"v": v, "id": qid}).fetchall()
        tiempos.append((time.perf_counter() - inicio) * 1000)
        resultados[qid] = {f[0] for f in filas}
    return resultados, statistics.median(tiempos)


con = conectar()
total, = con.execute("SELECT COUNT(*) FROM imagen").fetchone()
CONSULTAS = [f"img{i:06d}" for i in range(0, total, total // 20)][:20]  # 20 imágenes de consulta

con.execute("DROP INDEX IF EXISTS imagen_embedding_hnsw")
exactos, ms_sin = buscar_todas(con, CONSULTAS)
print(f"Sin índice:  {ms_sin:6.1f} ms por consulta (mediana de {len(CONSULTAS)})")

print("\nCreando el índice...")
print("  CREATE INDEX imagen_embedding_hnsw ON imagen USING hnsw (embedding vector_l2_ops);")
inicio = time.perf_counter()
con.execute("CREATE INDEX imagen_embedding_hnsw ON imagen USING hnsw (embedding vector_l2_ops)")
print(f"  Tardó {time.perf_counter() - inicio:.1f} s")
tamano, = con.execute("SELECT pg_size_pretty(pg_relation_size('imagen_embedding_hnsw'))").fetchone()
print(f"  Ocupa {tamano}")

aproximados, ms_con = buscar_todas(con, CONSULTAS)
print(f"\nCon índice:  {ms_con:6.1f} ms por consulta (mediana de {len(CONSULTAS)})")
print(f"Aceleración: {ms_sin / ms_con:.0f} veces")

# Recall: de los 5 vecinos exactos, cuántos encontró el índice
aciertos = sum(len(exactos[q] & aproximados[q]) for q in CONSULTAS)
print(f"Recall@5:    {aciertos / (5 * len(CONSULTAS)):.0%} de los vecinos exactos")
