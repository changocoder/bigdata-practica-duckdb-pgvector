-- Se ejecuta una sola vez, cuando el contenedor de PostgreSQL arranca con el volumen vacío.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS imagen (
    id        TEXT PRIMARY KEY,
    clase     TEXT NOT NULL,
    embedding vector(512) NOT NULL   -- 512 valores, como la salida de VGG-16 sin clasificador
);
