# DHI Data Lake Infrastructure

## Setup

1. Copy the example env file:
```bash
cp .env.example .env
```

2. Edit .env with your actual credentials:
```bash
nano .env
```

3. Generate Trino catalog files from templates:
```bash
bash setup.sh
```

4. Start all services:
```bash
docker compose up -d
```

## Services

| Service    | Port  | Purpose                    |
|------------|-------|----------------------------|
| MinIO      | 9001  | Object storage (S3)        |
| Trino      | 8080  | SQL query engine           |
| Nessie     | 19120 | Iceberg catalog            |
| PostgreSQL | 5432  | Nessie metadata storage    |
| pgAdmin    | 5050  | PostgreSQL UI              |
