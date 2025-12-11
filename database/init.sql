-- RemoteLED Database Initialization Script
-- Run this ONCE as postgres superuser to set up everything
-- Usage: sudo -u postgres psql -f init.sql
--
-- This script:
-- 1. Creates the remoteled database (if not exists)
-- 2. Creates the remoteled user with password
-- 3. Grants all necessary permissions
-- 4. Runs schema.sql to create tables
-- 5. Runs seed.sql to populate test data

-- ============================================================
-- STEP 1: Create database (run as postgres superuser)
-- ============================================================
-- Note: Cannot use IF NOT EXISTS with CREATE DATABASE in plain SQL
-- This will error if database exists - that's OK, just continue

\echo '=== Step 1: Creating database ==='
SELECT 'Creating database remoteled...' AS status;

-- Connect to postgres database first to create the new database
\c postgres

-- Drop and recreate for clean setup (comment out if you want to preserve data)
DROP DATABASE IF EXISTS remoteled;
CREATE DATABASE remoteled;

\echo '✓ Database created'

-- ============================================================
-- STEP 2: Create user with password
-- ============================================================
\echo '=== Step 2: Creating user ==='

-- Drop user if exists (to reset password)
DROP USER IF EXISTS remoteled;
CREATE USER remoteled WITH PASSWORD 'remoteled_dev_password';

\echo '✓ User created with password: remoteled_dev_password'

-- ============================================================
-- STEP 3: Connect to remoteled database and set up permissions
-- ============================================================
\echo '=== Step 3: Setting up permissions ==='
\c remoteled

-- Grant connect
GRANT CONNECT ON DATABASE remoteled TO remoteled;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO remoteled;

-- Grant all on future tables (before creating them)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO remoteled;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO remoteled;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO remoteled;

\echo '✓ Default privileges set'

-- ============================================================
-- STEP 4: Run schema.sql
-- ============================================================
\echo '=== Step 4: Creating schema ==='
\i schema.sql

-- Grant permissions on all existing tables (after schema creation)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO remoteled;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO remoteled;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO remoteled;

\echo '✓ Schema created and permissions granted'

-- ============================================================
-- STEP 5: Run seed.sql
-- ============================================================
\echo '=== Step 5: Loading seed data ==='
\i seed.sql

\echo '✓ Seed data loaded'

-- ============================================================
-- VERIFICATION
-- ============================================================
\echo ''
\echo '=============================================='
\echo '✅ RemoteLED Database Initialization Complete!'
\echo '=============================================='
\echo ''
\echo 'Database: remoteled'
\echo 'User: remoteled'
\echo 'Password: remoteled_dev_password'
\echo ''
\echo 'Connection string for backend/.env:'
\echo 'DATABASE_URL=postgresql://remoteled:remoteled_dev_password@localhost:5432/remoteled'
\echo ''
\echo 'Test connection with:'
\echo '  PGPASSWORD=remoteled_dev_password psql -h localhost -U remoteled -d remoteled -c "SELECT COUNT(*) FROM devices;"'
\echo ''

-- Quick verification query
SELECT 'Verification:' AS status;
SELECT COUNT(*) AS device_count FROM devices;
SELECT COUNT(*) AS service_count FROM services;
