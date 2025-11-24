# RemoteLED Local Setup Guide

Quick setup guide for running RemoteLED locally on Raspberry Pi.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Nginx

## 1. Database Setup

Install PostgreSQL:
```bash
sudo apt update && sudo apt install -y postgresql postgresql-contrib
```

Create database and user:
```bash
sudo -u postgres psql -c "CREATE DATABASE remoteled;"
sudo -u postgres psql -c "CREATE USER remoteled WITH PASSWORD 'remoteled_dev_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE remoteled TO remoteled;"
```

Initialize schema and seed data:
```bash
sudo -u postgres psql -d remoteled < database/schema.sql
sudo -u postgres psql -d remoteled < database/seed.sql
sudo -u postgres psql -d remoteled -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO remoteled;"
sudo -u postgres psql -d remoteled -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO remoteled;"
```

## 2. Backend API

Activate virtual environment and start:
```bash
source .venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9999
```

Verify health:
```bash
curl http://localhost:9999/health
# Expected: {"status":"healthy","database":"healthy",...}
```

## 3. Pi Services

Start nginx:
```bash
sudo systemctl start nginx
```

Start BLE peripheral:
```bash
cd pi/python
sudo DEVICE_ID=d1111111-1111-1111-1111-111111111111 python3 code.py
```

View QR code kiosk:
```bash
cd pi
./kiosk.sh
```

## 4. Verify Setup

Check all services:
```bash
# PostgreSQL
sudo systemctl status postgresql

# Backend API (health check)
curl http://localhost:9999/devices/d1111111-1111-1111-1111-111111111111/full

# Nginx
sudo systemctl status nginx

# QR data file
cat /var/www/html/qr_data.json
```

## Test Device

**UUID:** `d1111111-1111-1111-1111-111111111111`
**Name:** Laundry Room A
**Services:** 3 (FIXED $2.50/40min, TRIGGER $1.00, VARIABLE $0.25/6min)

## Service Ports

- PostgreSQL: 5432
- Backend API: 9999
- Nginx: 80

## Quick Start (All-in-One)

```bash
# 1. Start PostgreSQL (if not running)
sudo systemctl start postgresql

# 2. Start Backend API (in one terminal)
source .venv/bin/activate && cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9999

# 3. Start Nginx
sudo systemctl start nginx

# 4. Start Pi BLE (in another terminal)
cd pi/python && sudo DEVICE_ID=d1111111-1111-1111-1111-111111111111 python3 code.py

# 5. View QR kiosk (optional)
cd pi && ./kiosk.sh
```
