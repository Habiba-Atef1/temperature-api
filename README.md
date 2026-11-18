# Temperature API

A small REST API for storing and querying city temperature readings.
Built with FastAPI, SQLAlchemy (async) and SQLite. Auth is JWT based.

I built this as a simplified version of a temperature data service, mainly to practice
async routes, Pydantic models, auth and testing.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs for the Swagger UI.

Optional env variables: `SECRET_KEY` (JWT secret) and `DATABASE_URL`.

## Docker

```bash
docker build -t temperature-api .
docker run -p 8000:8000 -e SECRET_KEY=change-me temperature-api
```

## Tests

```bash
pytest
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | no | create a user |
| POST | `/auth/login` | no | get a JWT (form: username, password) |
| GET | `/cities` | no | list cities |
| POST | `/cities` | yes | add a city |
| POST | `/cities/{id}/readings` | yes | add a temperature reading |
| GET | `/cities/{id}/readings?from=&to=` | no | list readings, optional date filter |
| GET | `/cities/{id}/stats` | no | count, min, max and average temperature |

## Example

```bash
curl -X POST localhost:8000/auth/register -H "Content-Type: application/json" \
  -d '{"username":"habiba","password":"secret123"}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login -d "username=habiba&password=secret123" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -X POST localhost:8000/cities -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"name":"Cairo","country":"Egypt"}'

curl -X POST localhost:8000/cities/1/readings -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"temperature": 36.5}'

curl localhost:8000/cities/1/stats
```

## Project structure

```
app/
  main.py        app setup
  database.py    async engine + session
  models.py      User, City, Reading tables
  schemas.py     Pydantic models
  auth.py        password hashing + JWT helpers
  routers/       auth and cities endpoints
tests/           pytest tests
```
