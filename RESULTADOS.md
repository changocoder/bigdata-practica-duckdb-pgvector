# Resultados de referencia

Medidos al preparar la práctica. Los tiempos dependen de cada máquina: lo que importa es la proporción entre una opción y otra, no el número exacto.

## Parte 1: CSV vs. Parquet (5 millones de filas)

| | CSV | Parquet |
|---|---:|---:|
| Tamaño en disco | 163 MB | 19 MB (8,6 veces menos) |
| Contar por clase (1 columna) | 560 ms | 20 ms (27 veces más rápido) |
| Radio promedio con severidad M (3 columnas) | 559 ms | 37 ms (15 veces más rápido) |

Conteo por clase (igual en los dos formatos):

| clase | cantidad |
|---|---:|
| NORM | 3.098.038 |
| CALC | 800.916 |
| CIRC | 400.205 |
| SPIC | 299.582 |
| ARCH | 151.018 |
| MISC | 150.155 |
| ASYM | 100.086 |

**Por qué.** Con CSV, DuckDB tiene que leer y convertir a números el archivo completo, todas las columnas, en cada consulta. Con Parquet lee solo las columnas que pide la consulta, ya tipadas y comprimidas. Por eso la ventaja es mayor cuando la consulta toca una sola columna: con tres columnas hay más para leer y la diferencia se achica.

## Parte 2: pgvector

Medido con 10.000 imágenes. Con las 50.000 de la configuración por defecto, la búsqueda sin índice tarda proporcionalmente más y la ventaja del índice crece.

Las 5 más parecidas a `img000042` (clase CIRC) son todas de la clase CIRC:

| id | clase | distancia |
|---|---|---:|
| img002696 | CIRC | 0,9930 |
| img006582 | CIRC | 1,0047 |
| img006091 | CIRC | 1,0084 |
| img009997 | CIRC | 1,0102 |
| img007040 | CIRC | 1,0120 |

| | Sin índice | Con HNSW |
|---|---:|---:|
| Tiempo por consulta (mediana de 20) | 44 ms | 1,9 ms |
| Plan | Seq Scan + ordenar | Index Scan sobre HNSW |
| Recall@5 | 100 % (exacta) | 100 % |

Construir el índice tardó unos 10 s y ocupa 26 MB.

**Por qué.** Sin índice, PostgreSQL calcula la distancia contra todas las filas y las ordena. Con HNSW recorre un grafo de vecinos y revisa solo una parte. Acá el recall da 100 % porque los vectores simulados forman grupos bien separados. Con embeddings reales, que se mezclan más, es normal ver un recall algo menor; se puede subir con `SET hnsw.ef_search = 100;` a cambio de algo de velocidad.
