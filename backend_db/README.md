# backend_db

Flask backend API for the project. Handles scraping and data handling through API endpoints and the database.

## Quick start — Docker

Run the backend using Docker. From the project root you can start the backend service with Docker Compose:

Start the backend service (build image if needed):

```bash
docker compose up --build backend_db
```

Start the backend only in detached mode:

```bash
docker compose up -d --build backend_db
```

Bring the Compose stack down:

```bash
docker compose down
```

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

## Scraper — `universal_scraper.py`

Scraper built on Selenium and BeautifulSoup. This file includes:

- `build_driver(headless: bool = True)` — create/configure a Chrome WebDriver (respects `CHROMEDRIVER_PATH` and `CHROME_BIN` env vars; falls back to `webdriver-manager`).
- `scrape(url, driver, timeout=15, headless=True)` — scrape a single page and return a dict with `url`, `name`, and `images`.
- `get_scraping_data(url, driver)` — public helper that validates the URL and retries once with an extended timeout.

Basic usage example:

```python
from universal_scraper import build_driver, get_scraping_data

driver = build_driver(headless=True)
data = get_scraping_data('https://example.com', driver)
driver.quit()
```

Notes:

- Requires Chrome/Chromedriver or set env vars `CHROME_BIN` and `CHROMEDRIVER_PATH` to point to the binaries.
- `webdriver-manager` is used as a fallback when running outside Docker on developer machines.
- The scraper handles common cookie banners/popups and retries once on failure.

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

- `app.py` Application factory and blueprint registration
- `routes/` Flask route handlers (`backend.py`, `saved_data.py`, ...)
- `models/` SQLAlchemy models
- `db_utils.py` Helpers that persist scraped results
- `requirements.txt` Python dependencies
- `Dockerfile` Container build for the backend
- `universal_scraper` Handles webscraping

## Links

- Root README: [../README.md](../README.md)
- Docker compose: [../docker-compose.yml](../docker-compose.yml)
