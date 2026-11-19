"""Práctica 1, paso 1: generar una tabla grande de anotaciones en CSV.

Simula la tabla `anotacion` de la clase, pero con millones de filas en lugar de 330.
Los datos se generan con SQL dentro de DuckDB, sin pandas.

Uso:
    python practica1_duckdb/01_generar_datos.py            # 5 millones de filas
    python practica1_duckdb/01_generar_datos.py --filas 1000000
"""
import argparse
import os
import time

import duckdb

parser = argparse.ArgumentParser()
parser.add_argument("--filas", type=int, default=5_000_000)
args = parser.parse_args()

os.makedirs("data", exist_ok=True)
destino = "data/anotaciones.csv"

con = duckdb.connect()
con.execute("SELECT setseed(0.42)")  # misma semilla: todos obtienen los mismos datos

inicio = time.perf_counter()
con.execute(f"""
COPY (
    SELECT
        i + 1                                         AS id,
        'img' || lpad(CAST(i // 3 AS VARCHAR), 8, '0') AS imagen_id,
        clase,
        CASE WHEN clase = 'NORM' THEN NULL
             WHEN random() < 0.6 THEN 'B' ELSE 'M' END AS severidad,
        CASE WHEN clase = 'NORM' THEN 0 ELSE CAST(random() * 1024 AS INT) END AS x,
        CASE WHEN clase = 'NORM' THEN 0 ELSE CAST(random() * 1024 AS INT) END AS y,
        CASE WHEN clase = 'NORM' THEN 0 ELSE CAST(5 + random() * 195 AS INT) END AS radio
    FROM (
        SELECT
            i,
            -- reparto aproximado de clases: muchas NORM, pocas ASYM
            CASE
                WHEN r < 0.62 THEN 'NORM'
                WHEN r < 0.78 THEN 'CALC'
                WHEN r < 0.86 THEN 'CIRC'
                WHEN r < 0.92 THEN 'SPIC'
                WHEN r < 0.95 THEN 'MISC'
                WHEN r < 0.98 THEN 'ARCH'
                ELSE 'ASYM'
            END AS clase
        FROM (SELECT range AS i, random() AS r FROM range({args.filas}))
    )
) TO '{destino}' (HEADER, DELIMITER ',')
""")
segundos = time.perf_counter() - inicio

mb = os.path.getsize(destino) / 1024**2
print(f"Generadas {args.filas:,} filas en {segundos:.1f} s")
print(f"{destino}: {mb:,.0f} MB")
