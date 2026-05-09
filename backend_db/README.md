# backend_db

Flask backend API for the project. Handles scraping and datahandling through API and database.

## Quick start — Local environment

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app (development / SQLite):

```bash
export FLASK_ENV=development
flask --app app:create_app run --debug --host 0.0.0.0 --port 8000
```

The development configuration uses an SQLite database file located at `backend_db/app.db` by default.

## Environment Variables

- `FLASK_ENV` — environment (e.g. `development`, `production`)
- `AZURE_POSTGRESQL_CONNECTIONSTRING` — production DB connection string (only for `ProductionConfig`) WILL CHANGE
- `COPYCAT_API_CHECK_URL` — URL to the copycat image-check service (used in docker-compose)

## Tests

Run database tests from the repository root or inside the `backend_db` folder:

```bash
pytest backend_db/test.py -q
```

## Key files

- `app.py` — application factory and blueprint registration
- `routes/` — Flask route handlers (`backend.py`, `saved_data.py`, ...)
- `models/` — SQLAlchemy models
- `db_utils.py` — helpers that persist scraped results
- `requirements.txt` — Python dependencies
- `Dockerfile` — container build for the backend

## Links

- Root README: [../README.md](../README.md)
- Docker compose: [../docker-compose.yml](../docker-compose.yml)
