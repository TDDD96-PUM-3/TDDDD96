# Backend

## Overview
This is the backend for the system. It is built upon Python along with Flask, and handles login/authentication, data management, web scraping and all API logic.

The backend uses for database management and JWT-based authentication for the protected endpoints used for user authentication.


## Architecture
Client → Routes → Models / Business Logic → Database
↓
External services (scraper / AI API)

## Stack
The following technologies are used the the backend:

- Python
- Flask
- Databas (hhur blev det här?)
- Docker

# System structure
Core:
- app.py -> entry point for the Flask application
- config.py -> configuration of the system settings
- extensions.py initialization of Flask extensions

API layer: 
- routes/ -> API endpoints, request/response only

Models

Utilities
- utls/ - JWT token logic

Scraping (mer att komma)
- universal_scraper -> Generic scraper to obtain product data

AI (mock just nu)
- Used to fetch  the probability of a product being a counterfeit

# Database


# Authentication


# API endpoints

# API examples
#Base URL

All requests will be made to:

http://localhost:xyzz

Authentication
Login

POST /login

Request:
{
"email": "user@example.com",
"password": "password123"
}

Response:
{
"access_token": "JWT_TOKEN_HERE"
}

Using the token

Using protected routes:

Authorization: Bearer YOUR_TOKEN_HERE

Data API Examples
Create a new entry

POST /data

Request:

{
"title": "My first entry",
"content": "This is some example content"
}

Response:

{
"id": 1,
"title": "My first entry",
"content": "This is some example content",
"created_at": "2026-04-27"
}

Get all entries

GET /data

Response:

[
{
"id": 1,
"title": "My first entry",
"content": "This is some example content"
}
]

# Dcoker
The project uses Docker. The following configuration is used:

```dockerfile
FROM python:3.12.6-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=development

CMD ["flask", "--app", "app:create_app", "run", "--debug",
     "--host=0.0.0.0", "--port=8000"]

```

## Build
docker build -t backend-api .
## Run
docker run -p 8000:8000 backend-api

# Design principles
- Routes contain no business logic
- Models dare used to define the data structure
- Scraper and AI API are differentiated
- SQLAlchemy is used as an ORM abstraction layer (visst?)


