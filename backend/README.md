# RemoteLED Backend API

Python FastAPI backend for the RemoteLED QR-to-device activation system.

## Features

- ✅ Device and service/product management
- ✅ Order creation and lifecycle management
- ✅ ECDSA cryptographic signing for authorizations
- ✅ Mock payment processing (development)
- ✅ Telemetry logging from devices
- ✅ PostgreSQL database integration
- ✅ Full REST API with OpenAPI documentation

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database connection string
```

### 3. Ensure Database is Running

```bash
# Make sure PostgreSQL is running and the database is created
psql remoteled -c "SELECT COUNT(*) FROM devices;"
```

### 4. Run the API

```bash
# Development mode with auto-reload
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Devices

- `GET /devices/{device_id}` - Get device by ID
- `GET /devices/{device_id}/services` - Get active services for a device
- `GET /devices/{device_id}/full` - Get device with all services

### Orders

- `POST /orders` - Create a new order
- `GET /orders/{order_id}` - Get order by ID
- `PATCH /orders/{order_id}/status` - Update order status

### Authorizations

- `POST /authorizations` - Create signed authorization for a paid order
- `GET /authorizations/{auth_id}` - Get authorization by ID
- `GET /authorizations/order/{order_id}` - Get authorization by order ID

### Payments

- `POST /payments/intent` - Create payment intent
- `POST /payments/mock` - Process mock payment (development only)

### Telemetry

- `POST /devices/{device_id}/telemetry` - Log device event (STARTED, DONE, ERROR)
- `GET /devices/{device_id}/logs` - Get recent device logs

### Health

- `GET /health` - Health check endpoint

## Complete Flow Example

### 1. Customer scans QR code containing device UUID

```bash
# QR contains: remoteled://device/d1111111-1111-1111-1111-111111111111
```

### 2. App fetches device and services

```bash
GET /devices/d1111111-1111-1111-1111-111111111111/full
```

Response:
```json
{
  "device": {
    "id": "d1111111-1111-1111-1111-111111111111",
    "label": "Laundry Room A",
    "location": "Building 5, Floor 2",
    "status": "ACTIVE"
  },
  "services": [
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "type": "FIXED",
      "price_cents": 250,
      "fixed_minutes": 40
    }
  ]
}
```

### 3. Customer selects product and creates order

```bash
POST /orders
Content-Type: application/json

{
  "device_id": "d1111111-1111-1111-1111-111111111111",
  "product_id": "11111111-1111-1111-1111-111111111111",
  "amount_cents": 250
}
```

Response:
```json
{
  "id": "order-uuid",
  "status": "CREATED",
  "authorized_minutes": 40
}
```

### 4. Process mock payment

```bash
POST /payments/mock
Content-Type: application/json

{
  "order_id": "order-uuid",
  "success": true
}
```

Response:
```json
{
  "success": true,
  "status": "PAID"
}
```

### 5. Create signed authorization

```bash
POST /authorizations
Content-Type: application/json

{
  "order_id": "order-uuid"
}
```

Response:
```json
{
  "id": "auth-uuid",
  "payload": {
    "deviceId": "d1111111-1111-1111-1111-111111111111",
    "orderId": "order-uuid",
    "type": "FIXED",
    "seconds": 2400,
    "nonce": "abc123def456",
    "exp": 1728849600
  },
  "signature_hex": "3045022100..."
}
```

### 6. App relays authorization to Pi via BLE

```bash
# Mobile app sends signed authorization to Pi via Bluetooth
```

### 7. Pi sends telemetry back via app

```bash
POST /devices/d1111111-1111-1111-1111-111111111111/telemetry
Content-Type: application/json

{
  "event": "STARTED",
  "order_id": "order-uuid"
}
```

### 8. Session completes

```bash
POST /devices/d1111111-1111-1111-1111-111111111111/telemetry
Content-Type: application/json

{
  "event": "DONE",
  "order_id": "order-uuid"
}
```

## Order Status Flow

```
CREATED → PAID → RUNNING → DONE
           ↓         ↓
         FAILED   FAILED
```

## Security

- **ECDSA Signing**: All authorizations are signed with secp256k1
- **Nonce Protection**: One-time nonces prevent replay attacks
- **Expiry Times**: Authorizations expire after 5 minutes
- **Status Validation**: Order status transitions are strictly validated

## Development

### Run Tests

```bash
pytest
```

### Check API is Working

```bash
curl http://localhost:8000/health
```

### View Logs

The API logs to stdout. In development mode, you'll see detailed request/response logs.

## Production Deployment

### Environment Variables

Set these in production:

- `DATABASE_URL` - PostgreSQL connection string
- `API_DEBUG=False` - Disable debug mode
- `ENABLE_MOCK_PAYMENT=False` - Disable mock payments
- `CORS_ORIGINS` - Restrict to your frontend domains

### Run with Gunicorn

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Database

The API expects the RemoteLED PostgreSQL database to be set up. See `../database/README.md` for setup instructions.

## License

See main project README

