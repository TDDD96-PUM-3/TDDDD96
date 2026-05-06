# TDDD96

This repository contains three main parts:

- `backend_db`: Flask API and database handling
- `copycat_api_tddd96`: image similarity service
- `frontend/test`: React frontend

## Docker Setup

Use Docker if you want the full stack running with one command.

1. Make sure Docker and Docker Compose are installed.
2. From the project root, build and start everything:

```bash
docker compose up --build
```

3. Open the apps in your browser:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Copycat API: http://localhost:3100

4. When you are done, stop the services:

```bash
docker compose down
```

## Non-Docker Setup

Use this if you want to run each service locally without containers.

### 1. Backend setup

1. Open a terminal in `backend_db`.
2. Create and activate a virtual environment.
3. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

4. Start the Flask app:

```bash
flask --app app:create_app run --debug --host 0.0.0.0 --port 8000
```

The backend uses SQLite in development, so no separate database setup is needed for local use.

### 2. Copycat API setup

1. Open a second terminal in `copycat_api_tddd96`.
2. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 3100 --workers 1
```

### 3. Frontend setup

1. Open a third terminal in `frontend/test`.
2. Install the Node dependencies:

```bash
npm install
```

3. Start the frontend dev server:

```bash
npm run dev
```

4. Open the frontend at http://localhost:5173

## Extension Setup

1. Open this folder in VS Code.
2. Install recommended extensions when prompted.
   - Recommendations are defined in `.vscode/extensions.json`.
3. Keep workspace settings enabled.
   - Shared formatting and lint behavior is defined in `.vscode/settings.json`.

This project uses format-on-save in the workspace:

- Python: `autopep8`
- JavaScript/TypeScript: `Prettier`
- ESLint fixes on save

See [extensions.md](extensions.md) for extension details and setup instructions.
