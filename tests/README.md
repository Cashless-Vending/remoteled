# RemoteLED Test Suite

Automated tests for the RemoteLED backend API, focusing on authentication, CRUD operations, and admin logging.

## Test Files

### 1. `setup_test_db.sh`
Sets up a fresh test database with the latest schema and seed data.

**Usage:**
```bash
./tests/setup_test_db.sh
```

**What it does:**
- Drops and recreates `remoteled_test` database
- Loads `database/schema.sql` (includes admin_logs table)
- Loads `database/seed.sql`
- Verifies all tables exist

### 2. `test_auth_api.sh`
Tests all authentication endpoints.

**Usage:**
```bash
./tests/test_auth_api.sh
```

**Tests:**
- ✅ User registration (POST /auth/register)
- ✅ Get current user (GET /auth/me)
- ✅ User login (POST /auth/login)
- ✅ Wrong password rejection
- ✅ Logout (POST /auth/logout)
- ✅ Protected endpoints require auth

### 3. `test_crud_with_auth.sh`
Tests CRUD operations with authentication and admin logging.

**Usage:**
```bash
./tests/test_crud_with_auth.sh
```

**Tests:**
- ✅ Create device (POST /admin/devices)
- ✅ Update device (PUT /admin/devices/{id})
- ✅ Create service (POST /admin/services)
- ✅ Delete service (DELETE /admin/services/{id})
- ✅ Delete device (DELETE /admin/devices/{id})
- ✅ Admin action logging (GET /admin/logs/admin-actions)

## Running All Tests

**Prerequisites:**
1. PostgreSQL installed (via Homebrew)
2. Python virtual environment activated
3. Backend dependencies installed
4. Backend server running on http://localhost:8000

**Run tests:**
```bash
# 1. Setup test database
./tests/setup_test_db.sh

# 2. Start backend (in another terminal)
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Run authentication tests
./tests/test_auth_api.sh

# 4. Run CRUD tests
./tests/test_crud_with_auth.sh
```

## Expected Results

All tests should pass with ✅ indicators. If any test fails, check:
- Backend is running on port 8000
- Database connection is working
- New dependencies (passlib, python-jose) are installed
- Schema includes password_hash and admin_logs table

## Test Coverage

- **Authentication**: Registration, login, logout, token validation
- **Authorization**: Protected endpoints, invalid tokens
- **CRUD Operations**: Create, Read, Update, Delete for devices and services
- **Audit Logging**: All admin actions recorded in admin_logs table
- **Error Handling**: Invalid credentials, missing auth, validation errors

