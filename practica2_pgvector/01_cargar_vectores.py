"""Práctica 2, paso 1: cargar embeddings en PostgreSQL con pgvector.

En la clase, cada imagen pasa por VGG-16 sin clasificador y sale un vector de 512 valores.
Para no depender de imágenes ni de una GPU, acá se simulan esos vectores:
cada clase tiene un "centro" y cada imagen es ese centro más un poco de ruido.
Así, imágenes de la misma clase quedan cerca, igual que con un embedding real.

Uso:
    python practica2_pgvector/01_cargar_vectores.py              # 50.000 imágenes
    python practica2_pgvector/01_cargar_vectores.py --cantidad 100000
"""
import argparse
import time

import numpy as np

from conexion import conectar

CLASES = ["NORM", "CALC", "CIRC", "SPIC", "MISC", "ARCH", "ASYM"]
DIM = 512

parser = argparse.ArgumentParser()
parser.add_argument("--cantidad", type=int, default=50_000)
args = parser.parse_args()

rng = np.random.default_rng(42)  # misma semilla: todos obtienen los mismos vectores
centros = rng.normal(size=(len(CLASES), DIM))

con = conectar()
con.execute("TRUNCATE imagen")
con.execute("DROP INDEX IF EXISTS imagen_embedding_hnsw")

inicio = time.perf_counter()
with con.cursor() as cur:
    # COPY en formato binario: la forma más rápida de cargar muchas filas
    with cur.copy("COPY imagen (id, clase, embedding) FROM STDIN WITH (FORMAT BINARY)") as copy:
        copy.set_types(["text", "text", "vector"])
        for i in range(args.cantidad):
            c = rng.integers(len(CLASES))
            v = centros[c] + rng.normal(scale=1.2, size=DIM)
            v = (v / np.linalg.norm(v)).astype(np.float32)  # largo 1, como suele hacerse
            copy.write_row([f"img{i:06d}", CLASES[c], v])
segundos = time.perf_counter() - inicio

total, = con.execute("SELECT COUNT(*) FROM imagen").fetchone()
tamano, = con.execute("SELECT pg_size_pretty(pg_total_relation_size('imagen'))").fetchone()
print(f"Cargadas {total:,} imágenes en {segundos:.1f} s")
print(f"Tamaño de la tabla en disco: {tamano}")
print(f"Cada vector ocupa {DIM} × 4 bytes = {DIM * 4 / 1024:.0f} KB")
