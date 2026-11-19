"""Práctica 1, paso 3: la misma consulta sobre CSV y sobre Parquet.

Cada consulta se corre 3 veces y se toma la mediana, para que no influya
si el disco estaba en caché o no.

Uso:
    python practica1_duckdb/03_comparar.py
"""
import statistics
import time

import duckdb

CONSULTAS = {
    "Contar anotaciones por clase (1 columna)": """
        SELECT clase, COUNT(*) AS cantidad
        FROM {fuente}
        GROUP BY clase
        ORDER BY cantidad DESC
    """,
    "Radio promedio de las anotaciones con severidad M, por clase (3 columnas)": """
        SELECT clase, ROUND(AVG(radio), 1) AS radio_promedio
        FROM {fuente}
        WHERE severidad = 'M'
        GROUP BY clase
        ORDER BY clase
    """,
}

FUENTES = {
    "CSV": "read_csv('data/anotaciones.csv')",
    "Parquet": "'data/anotaciones.parquet'",
}


def medir(con, sql, repeticiones=3):
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        filas = con.execute(sql).fetchall()
        tiempos.append(time.perf_counter() - inicio)
    return statistics.median(tiempos), filas


con = duckdb.connect()
for titulo, plantilla in CONSULTAS.items():
    print(f"\n=== {titulo}")
    print(plantilla.format(fuente="<tabla>").strip())
    resultados = {}
    for nombre, fuente in FUENTES.items():
        segundos, filas = medir(con, plantilla.format(fuente=fuente))
        resultados[nombre] = (segundos, filas)
        print(f"\n  {nombre:8} {segundos * 1000:8.0f} ms")

    # Las dos fuentes tienen que dar exactamente el mismo resultado
    assert resultados["CSV"][1] == resultados["Parquet"][1]
    print("\n  Resultado (igual en las dos):")
    for fila in resultados["Parquet"][1]:
        print("   ", *fila)
    veces = resultados["CSV"][0] / resultados["Parquet"][0]
    print(f"\n  Parquet fue {veces:.0f} veces más rápido.")
