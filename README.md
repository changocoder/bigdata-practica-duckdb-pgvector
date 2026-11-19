# Práctica sugerida: DuckDB, Parquet y pgvector

Material complementario de la clase invitada **«De 322 imágenes a petabytes»** (Mg. Ing. Hugo Chanampe, UNLAR 2026).

Es una práctica **opcional**, para quien quiera probar por su cuenta lo que vimos en clase. Tiene dos partes:

| Parte | Qué se prueba | Idea de la clase |
|---|---|---|
| 1. DuckDB | La misma consulta `GROUP BY` sobre un CSV y sobre un Parquet | Almacenamiento por filas vs. por columnas |
| 2. pgvector | Guardar vectores en PostgreSQL y buscar los 5 más parecidos, con y sin índice HNSW | Embeddings y búsqueda por similitud |

Todo corre en Docker, así que no hace falta instalar Python ni PostgreSQL.

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows o macOS) o Docker Engine con el plugin Compose (Linux).
- Unos 2 GB libres de disco.

Para comprobar que Docker funciona:

```bash
docker --version
docker compose version
```

## Puesta en marcha

```bash
git clone https://github.com/changocoder/bigdata-practica-duckdb-pgvector.git
cd bigdata-practica-duckdb-pgvector
docker compose build
```

`docker compose build` arma la imagen con Python, DuckDB y psycopg. Solo hace falta la primera vez.

## Parte 1: CSV vs. Parquet con DuckDB

```bash
docker compose run --rm lab python practica1_duckdb/01_generar_datos.py
docker compose run --rm lab python practica1_duckdb/02_csv_a_parquet.py
docker compose run --rm lab python practica1_duckdb/03_comparar.py
```

1. **Generar los datos.** Crea `data/anotaciones.csv` con 5 millones de anotaciones (id, imagen, clase, severidad, x, y, radio). Si tu máquina es lenta, usá `--filas 1000000`.
2. **Convertir a Parquet.** Escribe la misma tabla en `data/anotaciones.parquet` y muestra cuánto ocupa cada archivo.
3. **Comparar.** Corre dos consultas sobre cada formato, verifica que den el mismo resultado y mide el tiempo.

## Parte 2: búsqueda por similitud con pgvector

```bash
docker compose up -d db
docker compose run --rm lab python practica2_pgvector/01_cargar_vectores.py
docker compose run --rm lab python practica2_pgvector/02_buscar_similares.py
docker compose run --rm lab python practica2_pgvector/03_indice_hnsw.py
```

1. **Cargar vectores.** Inserta 50.000 imágenes con un vector de 512 valores cada una. Los vectores son simulados: cada clase tiene un centro y cada imagen es ese centro más ruido, así que las imágenes de una misma clase quedan cerca, como con un embedding real de VGG-16.
2. **Buscar similares.** Para la imagen `img000042`, devuelve las 5 más cercanas. Se puede pasar otro id: `... 02_buscar_similares.py img001234`.
3. **Índice HNSW.** Mide la búsqueda sin índice, crea el índice, vuelve a medir y calcula el *recall*: qué porcentaje de los vecinos exactos encontró el índice.

Para entrar a PostgreSQL y hacer consultas a mano:

```bash
docker compose exec db psql -U practica
```

```sql
SELECT clase, COUNT(*) FROM imagen GROUP BY clase;
SELECT id, clase FROM imagen
ORDER BY embedding <-> (SELECT embedding FROM imagen WHERE id = 'img000042')
LIMIT 5;
```

Desde un cliente gráfico (DBeaver, pgAdmin): `localhost`, puerto **5433**, usuario, contraseña y base `practica`.

## Para pensar

- ¿Por qué Parquet ocupa mucho menos que el CSV, si tiene los mismos datos?
- La segunda consulta usa 3 columnas y la primera solo 1. ¿Cómo cambia la ventaja de Parquet? ¿Por qué?
- En la búsqueda por similitud, ¿los 5 vecinos son de la misma clase que la imagen de consulta? ¿Qué significa eso?
- El índice HNSW es aproximado. ¿En qué casos aceptarían perder algo de recall a cambio de velocidad?

Los resultados de referencia, medidos en una máquina, están en [RESULTADOS.md](RESULTADOS.md). Los tiempos de cada uno van a variar; lo que importa es la proporción.

## Limpiar

```bash
docker compose down -v      # apaga PostgreSQL y borra su volumen
```

Los archivos generados quedan en `data/` y se pueden borrar a mano.

## Estructura

```
docker-compose.yml        PostgreSQL con pgvector + contenedor de Python
lab/                      Dockerfile y dependencias de Python
db/init.sql               crea la extensión vector y la tabla imagen
practica1_duckdb/         scripts de la parte 1
practica2_pgvector/       scripts de la parte 2
data/                     archivos generados (no se suben al repo)
```

## Referencias

- DuckDB: <https://duckdb.org/docs/>
- Formato Apache Parquet: <https://parquet.apache.org/docs/>
- pgvector: <https://github.com/pgvector/pgvector>
- Malkov y Yashunin (2020), *Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs*, IEEE TPAMI 42(4).
