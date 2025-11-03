#!/bin/bash
# Setup test database with new schema

DB_NAME="remoteled"

echo "=== Setting up database with latest schema ==="

# Add PostgreSQL to PATH if needed
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# Recreate database
echo "1. Dropping existing database..."
dropdb --if-exists $DB_NAME 2>/dev/null

echo "2. Creating fresh database..."
createdb $DB_NAME

echo "3. Loading schema..."
psql -d $DB_NAME -f database/schema.sql -q

echo "4. Loading seed data..."
psql -d $DB_NAME -f database/seed.sql -q

echo "5. Verifying tables..."
psql -d $DB_NAME -c "\dt" | grep -E "admins|admin_logs|devices|services"

echo ""
echo "✅ Database ready: $DB_NAME"
echo "   Tables: admins (with password_hash), admin_logs, devices, services, orders, logs"
echo "   Test user: admin@remoteled.com / password123"

