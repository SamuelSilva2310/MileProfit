# MileProfit

A mobile-first Progressive Web App for TVDE drivers to track earnings, expenses, mileage, and profitability.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, SQLite, Alembic
- **Frontend:** Vue 3, Vite, Tailwind CSS, Pinia, Vue Router
- **Auth:** JWT (python-jose + passlib/bcrypt)
- **PWA:** vite-plugin-pwa (installable on iOS/Android)

---

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
PYTHONPATH=. alembic upgrade head

# Create an admin user
PYTHONPATH=. python -m app.cli create-user --email admin@test.com --password admin123 --name "Admin" --admin

# Seed sample data (optional)
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

The frontend runs on `http://localhost:5173` and proxies `/api` requests to the backend on port 8000.

### API Docs

With the backend running, visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## Production Deployment (Hetzner + Docker)

### Architecture

```
Internet
  └── Host Nginx (port 80)
        └── Docker: frontend container (Nginx, :3000)
                        └── Docker: backend container (Uvicorn, :8000)
                                        └── Docker volume: SQLite database
```

### Step 1 — Provision the server

1. Create a Hetzner server with **Ubuntu 24.04**
2. Paste the contents of `cloud-config.yaml` into the **"User data"** field
3. The cloud-config will automatically:
   - Create the `parrot` user (sudo + docker groups, SSH key login)
   - Install Nginx, Docker, UFW, fail2ban
   - Configure the firewall (ports 22, 80, 443 only)

> Wait ~3 minutes for cloud-init to finish before SSHing in.

### Step 2 — SSH into the server

```bash
ssh parrot@<server-ip>
```

### Step 3 — Clone the repo

```bash
git clone <your-repo-url> /opt/mileprofit
```

### Step 4 — Configure the environment

```bash
# The deploy script will create this automatically on first run,
# but you can also do it manually:
cp /opt/mileprofit/backend/.env.example /opt/mileprofit/backend/.env
nano /opt/mileprofit/backend/.env
```

Required values to fill in:

| Variable | How to generate |
|---|---|
| `SECRET_KEY` | `openssl rand -hex 32` |
| `CORS_ORIGINS` | `["http://<server-ip>"]` |
| `DATABASE_URL` | Already set correctly in `.env.example` |

### Step 5 — Deploy

```bash
/opt/mileprofit/deploy.sh
```

The script will:
1. Pull the latest code
2. Create `backend/.env` from `.env.example` if missing (and prompt you to fill it in)
3. Build Docker images and start both containers
4. Prune unused images
5. Install and reload the Nginx config

The app is now available at `http://<server-ip>`.

### Step 6 — Create the first user

```bash
docker compose -f /opt/mileprofit/docker-compose.yml exec backend \
  python -m app.cli create-user --email you@example.com --password yourpassword --name "Your Name" --admin
```

---

## Updates

To deploy a new version, just push your changes and re-run the deploy script on the server:

```bash
ssh parrot@<server-ip>
/opt/mileprofit/deploy.sh
```

---

## Useful Commands

```bash
# View live logs
docker compose -f /opt/mileprofit/docker-compose.yml logs -f

# Restart containers
docker compose -f /opt/mileprofit/docker-compose.yml restart

# Stop everything
docker compose -f /opt/mileprofit/docker-compose.yml down

# Open a shell in the backend container
docker compose -f /opt/mileprofit/docker-compose.yml exec backend bash
```

---

## Project Structure

```
rider-expenses/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Environment settings (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── cli.py           # Admin CLI (create-user, seed)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API route handlers
│   │   └── utils/           # JWT + password hashing helpers
│   ├── alembic/             # Database migrations
│   ├── Dockerfile
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia state stores
│   │   ├── services/        # Axios API client
│   │   ├── router/          # Vue Router config
│   │   └── App.vue          # Root component
│   ├── Dockerfile
│   ├── nginx.conf           # Container Nginx (serves SPA + proxies /api/)
│   └── vite.config.js
├── docker-compose.yml
├── nginx-host.conf          # Host Nginx (reverse proxy → Docker :3000)
├── deploy.sh                # Deploy / update script
└── cloud-config.yaml        # Hetzner server bootstrap (cloud-init)
```
