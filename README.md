Author: Joonas Nietosvaara

This is a simple todo management webapp. Below are instructions for running and modifying it.

## Running the app locally

These instructions are for Linux/Mac.

These prerequisites must be installed:
- docker and docker-compose
- Python 3.8+ and pip
- `openssl`
- git

To run the app locally, do the following.

1. Clone the repository and `cd` into it.

2. Launch the server:
   ```bash
   docker-compose up -d
   ```

3. Access the application from your browser:
   - Visit `https://localhost:8000`
   - For interactive API documentation visit `https://localhost:8000/docs`
   - You will need to accept a security exception for the self-signed certificate.

Note on SSL certificates: the app will automatically generate self-signed SSL certificates if they don't exist and store them in `certs/`. If you wish to manually generate certificates, run the following in the project root: `mkdir -p certs && openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1 `.

## Running tests

To run the tests, do the following:

1. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r tests/test-requirements.txt
   pip install -r app/requirements.txt
   ```
Then run the tests as follows:

Run all tests:
```bash
pytest tests/ -v
```

Run tests matching a specific pattern:
```bash
pytest tests/ -k "keyword" -v
```

When finished, deactivate the virtual environment:
```bash
deactivate
```

## Project Structure
- `app/`: FastAPI backend with SQLAlchemy ORM
  - For API documentation, launch the app and visit `https://localhost:8000/docs`.
- `frontend/`: Vanilla JavaScript, HTML, CSS  
- `app/migrations/`: Alembic database migration scripts

## Database Migrations
To manage database changes:

```bash
# Create a new migration
cd app
alembic revision --autogenerate -m "description"

# Apply all migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```
