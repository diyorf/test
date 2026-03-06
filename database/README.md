# Database Setup

This project uses PostgreSQL.

## Local database

1. Ensure PostgreSQL server is running.
2. Execute `init.sql`:

```bash
psql -U postgres -f database/init.sql
```

3. Configure environment variables used by Django:

- `POSTGRES_DB=python_learning`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `POSTGRES_HOST=127.0.0.1`
- `POSTGRES_PORT=5432`
