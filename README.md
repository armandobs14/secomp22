# Engenharia de dados - Secom22


```bash

# Baixar imagem do alpine
docker pull alpine

# subir banco de dados
docker compose up -d postgres

# crair banco utilizado pelo airflow
docker exec -i postgres psql -U postgres < schema/schema.sql

# subir servuços do airflow
docker compose up -d
```
