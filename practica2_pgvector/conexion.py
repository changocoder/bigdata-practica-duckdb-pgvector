"""Conexión a PostgreSQL usando las variables de entorno PGHOST, PGUSER, etc.

docker-compose.yml ya las define para el contenedor `lab`.
"""
import psycopg
from pgvector.psycopg import register_vector


def conectar():
    # toma PGHOST, PGPORT, PGUSER... del entorno
    con = psycopg.connect(autocommit=True, prepare_threshold=None)
    register_vector(con)  # permite enviar y recibir vectores como arrays de numpy
    return con
