# backend_db

Flask backend API for the project. Handles scraping and data handling through API endpoints and the database.

## Quick start — Local environment (Windows / Linux / macOS)

Follow the platform-specific steps below to create a virtual environment, install dependencies, and run the app in development mode.

### Linux / macOS

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

### Windows (PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app (development / SQLite):

```powershell
$env:FLASK_ENV = "development"
flask --app app:create_app run --debug --host 0.0.0.0 --port 8000
```

If PowerShell blocks the activation script, you can either run PowerShell as Administrator and set the execution policy or activate with the batch script in cmd.exe:

```cmd
\.venv\Scripts\activate.bat
set FLASK_ENV=development
flask --app app:create_app run --debug --host 0.0.0.0 --port 8000
```

### Notes

- The development configuration uses an SQLite database file located at `backend_db/app.db` by default.
- For production, set `AZURE_POSTGRESQL_CONNECTIONSTRING` (or your preferred DB connection string) and use a production configuration.

## Environment Variables

- `FLASK_ENV` — environment (e.g. `development`, `production`)
- `AZURE_POSTGRESQL_CONNECTIONSTRING` — production DB connection string (only for `ProductionConfig`)
- `COPYCAT_API_CHECK_URL` — URL to the copycat image-check service (used in docker-compose)

On Linux/macOS use `export VAR=value`. On PowerShell use `$env:VAR = "value"`. On cmd.exe use `set VAR=value`.

## Tests

Run tests from the repository root or inside the `backend_db` folder:

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
