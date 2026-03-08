# MileProfit — Operations Runbook

Quick reference for managing the production server.

All commands assume you are SSHed in as `parrot` and the app lives at `/opt/mileprofit`.

```bash
ssh parrot@<server-ip>
```

---

## Shortcuts

Add these to `~/.bashrc` on the server to save typing:

```bash
alias mp='docker compose -f /opt/mileprofit/docker-compose.yml'
alias mpcli='docker compose -f /opt/mileprofit/docker-compose.yml exec backend python -m app.cli'
```

Then `source ~/.bashrc`. The examples below use these aliases.

---

## Containers

```bash
# Status — health, uptime, ports
mp ps

# Live logs (both containers)
mp logs -f

# Logs for one container only
mp logs -f backend
mp logs -f frontend

# Restart all
mp restart

# Restart one container
mp restart backend

# Stop everything
mp down

# Start everything (without rebuilding)
mp up -d
```

---

## Deploy & Update

```bash
# Pull latest code and rebuild changed images
/opt/mileprofit/deploy.sh

# Or manually step by step
cd /opt/mileprofit
git pull
mp up -d --build
docker image prune -f
sudo systemctl reload nginx
```

---

## Users

```bash
# Create a regular user
mpcli create-user --email user@example.com --password securepass --name "Full Name"

# Create an admin user
mpcli create-user --email admin@example.com --password securepass --name "Admin" --admin

# Seed sample data for a user (useful for testing)
mpcli seed --email user@example.com --days 90
```

---

## Database

### Location

The SQLite database is stored in a named Docker volume:

```
Volume name : mileprofit-db
Path on host: /var/lib/docker/volumes/mileprofit-db/_data/mileprofit.db
```

```bash
# Confirm the path
docker volume inspect mileprofit-db
```

### Backup

```bash
# One-off backup to home directory
docker run --rm \
  -v mileprofit-db:/data \
  -v $HOME/backups:/backup \
  alpine tar czf /backup/mileprofit-db-$(date +%F).tar.gz -C /data .

ls ~/backups/
```

### Scheduled daily backup (keep last 7 days)

```bash
# Create backup directory
mkdir -p ~/backups

# Add the cron job
crontab -e
```

Paste this line:

```
0 2 * * * docker run --rm -v mileprofit-db:/data -v /root/backups:/backup alpine tar czf /backup/mileprofit-db-$(date +\%F).tar.gz -C /data . && find /root/backups -name "mileprofit-db-*.tar.gz" -mtime +7 -delete
```

### Restore from backup

```bash
# Stop the backend first
mp stop backend

# Restore
docker run --rm \
  -v mileprofit-db:/data \
  -v $HOME/backups:/backup \
  alpine tar xzf /backup/mileprofit-db-<DATE>.tar.gz -C /data

# Start again
mp start backend
```

### Inspect the database directly

```bash
# Open an interactive SQLite shell inside the container
mp exec backend sqlite3 /data/mileprofit.db

# Useful SQLite commands once inside:
.tables                        -- list all tables
SELECT * FROM users;           -- list users
SELECT COUNT(*) FROM earnings; -- count records
.quit
```

### Run migrations manually

```bash
mp exec backend alembic upgrade head

# Check current migration version
mp exec backend alembic current

# Migration history
mp exec backend alembic history
```

---

## Server

### Disk & memory

```bash
# Disk usage
df -h

# Docker disk usage (images, volumes, containers)
docker system df

# Memory
free -h

# Running processes
htop
```

### Free up disk space

```bash
# Remove unused Docker images
docker image prune -f

# Remove everything unused (images, stopped containers, networks, build cache)
# Safe to run — won't touch running containers or named volumes
docker system prune -f
```

### Nginx

```bash
# Test config before reloading
sudo nginx -t

# Reload (no downtime)
sudo systemctl reload nginx

# Full restart
sudo systemctl restart nginx

# Logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Firewall

```bash
# Check status and open ports
sudo ufw status verbose

# Open a port (if needed)
sudo ufw allow 8080

# Remove a rule
sudo ufw delete allow 8080
```

### fail2ban (SSH protection)

```bash
# Check status — shows banned IPs
sudo fail2ban-client status sshd

# Unban an IP
sudo fail2ban-client set sshd unbanip <IP>
```

---

## HTTPS / SSL

### Enable with sslip.io (no domain needed)

Replace dots in your server IP with dashes, e.g. `1.2.3.4` → `1-2-3-4.sslip.io`:

```bash
sudo certbot --nginx -d 1-2-3-4.sslip.io
```

Update `CORS_ORIGINS` in `/opt/mileprofit/backend/.env`:

```
CORS_ORIGINS=["https://1-2-3-4.sslip.io"]
```

Then redeploy:

```bash
/opt/mileprofit/deploy.sh
```

### Renew certificate (auto, but can be forced)

```bash
sudo certbot renew --dry-run   # test
sudo certbot renew             # force renew
```

### Check certificate expiry

```bash
sudo certbot certificates
```

---

## Environment Variables

Config lives at `/opt/mileprofit/backend/.env`. Edit and redeploy to apply changes:

```bash
nano /opt/mileprofit/backend/.env
/opt/mileprofit/deploy.sh
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing key — generate with `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Session duration (default: 1440 = 24h) |
| `DATABASE_URL` | SQLite path inside the container — do not change |
| `CORS_ORIGINS` | Allowed origins, e.g. `["https://yourdomain.com"]` |

---

## Troubleshooting

### Container keeps restarting

```bash
# Check exit code and last logs
mp ps
mp logs --tail 50 backend
```

### Frontend shows 502 Bad Gateway

The backend container is unhealthy or not started yet.

```bash
mp ps                   # check health status
mp logs backend         # look for startup errors
mp restart backend
```

### Can't connect to the server

```bash
# Check firewall
sudo ufw status

# Check Nginx is running
sudo systemctl status nginx

# Check containers are up
mp ps
```

### Check what's listening on which port

```bash
sudo ss -tlnp | grep -E '80|443|3000|8000'
```
