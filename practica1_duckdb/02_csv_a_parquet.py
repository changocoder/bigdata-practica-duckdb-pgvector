"""Práctica 1, paso 2: convertir el CSV a Parquet.

CSV guarda la tabla por filas y como texto.
Parquet la guarda por columnas, con tipos y comprimida.

Uso:
    python practica1_duckdb/02_csv_a_parquet.py
"""
import os
import time

import duckdb

origen = "data/anotaciones.csv"
destino = "data/anotaciones.parquet"

con = duckdb.connect()
inicio = time.perf_counter()
con.execute(f"""
COPY (SELECT * FROM read_csv('{origen}'))
TO '{destino}' (FORMAT parquet, COMPRESSION zstd)
""")
segundos = time.perf_counter() - inicio

mb_csv = os.path.getsize(origen) / 1024**2
mb_parquet = os.path.getsize(destino) / 1024**2
print(f"Conversión en {segundos:.1f} s")
print(f"CSV:     {mb_csv:8,.0f} MB")
print(f"Parquet: {mb_parquet:8,.0f} MB  ({mb_csv / mb_parquet:.1f} veces más chico)")

# Parquet guarda el esquema: no hace falta adivinar los tipos al leer
print("\nEsquema guardado en el Parquet:")
for nombre, tipo, *_ in con.execute(f"DESCRIBE SELECT * FROM '{destino}'").fetchall():
    print(f"  {nombre:10} {tipo}")
