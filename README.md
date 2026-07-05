# Notes API

A REST API built with FastAPI for managing personal notes with JWT authentication.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLModel
- Docker
- JWT Authentication (pwdlib + PyJWT)

## Features

- User registration and authentication
- Create, read, update, and delete notes
- Ownership protection — users can only access their own notes
- Structured logging
- Pytest test suite

## Getting Started

### Prerequisites

- Python 3.13+
- Docker

### Setup

1. Clone the repository

2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory

```env
DATABASE_URL=postgresql+psycopg://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/YOUR_DB_NAME
TEST_DATABASE_URL=postgresql+psycopg://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/YOUR_TEST_DB_NAME
POSTGRES_DB=YOUR_DB_NAME
POSTGRES_USER=YOUR_DB_USER
POSTGRES_PASSWORD=YOUR_DB_PASSWORD
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

4. Start the database

```bash
docker-compose up -d db
```

5. Run the development server

```bash
fastapi dev main.py
```

API docs available at `http://127.0.0.1:8000/docs`

## Running with Docker

Create a `.env.docker` file:

```env
DATABASE_URL=postgresql+psycopg://YOUR_DB_USER:YOUR_DB_PASSWORD@notes-postgres:5432/YOUR_DB_NAME
TEST_DATABASE_URL=postgresql+psycopg://YOUR_DB_USER:YOUR_DB_PASSWORD@notes-postgres:5432/YOUR_TEST_DB_NAME
POSTGRES_DB=YOUR_DB_NAME
POSTGRES_USER=YOUR_DB_USER
POSTGRES_PASSWORD=YOUR_DB_PASSWORD
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
```

Then run:

```bash
docker-compose up --build -d
```

API docs available at `http://localhost/docs`

## Running Tests

```bash
pytest -v
```
