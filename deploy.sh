#!/usr/bin/env bash
# MileProfit — deploy / update script
# Run this on the server after first boot, and on every update.
#
#   First deploy:   /opt/mileprofit/deploy.sh
#   Updates:        git pull && ./deploy.sh   (or just re-run from anywhere)
set -euo pipefail

REPO_URL="<CHANGE_ME: e.g. git@github.com:you/rider-expenses.git>"
APP_DIR="/opt/mileprofit"

# ── 1. Sync code ─────────────────────────────────────────────────────────────
echo "▶ Syncing code..."
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull
else
  git clone "$REPO_URL" "$APP_DIR"
fi

# ── 2. Bootstrap .env on first run ───────────────────────────────────────────
if [ ! -f "$APP_DIR/backend/.env" ]; then
  cp "$APP_DIR/backend/.env.example" "$APP_DIR/backend/.env"
  echo ""
  echo "  backend/.env was created from .env.example."
  echo "  Fill in the required values before continuing:"
  echo "    nano $APP_DIR/backend/.env"
  echo ""
  echo "  Required:"
  echo "    SECRET_KEY   -> openssl rand -hex 32"
  echo "    CORS_ORIGINS -> [\"https://yourdomain.com\"]"
  echo ""
  exit 1
fi

# ── 3. Build images and start containers ─────────────────────────────────────
echo "▶ Building and starting containers..."
docker compose -f "$APP_DIR/docker-compose.yml" up -d --build

# ── 4. Remove dangling images to free disk space ─────────────────────────────
echo "▶ Pruning unused images..."
docker image prune -f

# ── 5. Reload Nginx (picks up any config changes) ────────────────────────────
echo "▶ Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "✓ MileProfit is up."
echo "  Logs: docker compose -f $APP_DIR/docker-compose.yml logs -f"
