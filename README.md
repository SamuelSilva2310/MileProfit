# TVDE Earnings Tracker

A mobile-first Progressive Web App for TVDE drivers to track earnings, expenses, mileage, and profitability.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, SQLite, Alembic
- **Frontend:** Vue 3, Vite, Tailwind CSS, Pinia, Vue Router
- **Auth:** JWT (python-jose + passlib/bcrypt)
- **PWA:** vite-plugin-pwa (installable on iOS/Android)

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize the database
PYTHONPATH=. alembic upgrade head

# Create an admin user
PYTHONPATH=. python -m app.cli create-user --email admin@test.com --password admin123 --name "Admin" --admin

# Seed sample data (60 days of realistic activity)
PYTHONPATH=. python -m app.cli seed --email admin@test.com --days 180

# Start the server
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API requests to the backend on port 8000.

### Default Login

- **Email:** admin@tvde.local
- **Password:** admin123

## API Docs

With the backend running, visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Project Structure

```
rider-expenses/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Environment settings
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── cli.py           # Admin CLI (create users)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API route modules
│   │   └── utils/           # Auth helpers (JWT, password hashing)
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia state stores
│   │   ├── services/        # API client (axios)
│   │   ├── router/          # Vue Router config
│   │   └── App.vue          # Root component with bottom nav
│   └── vite.config.js
└── TCDE.md                  # Feature specification
```
