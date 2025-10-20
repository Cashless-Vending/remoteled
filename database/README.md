# RemoteLED Database Documentation

## Overview

This database powers the RemoteLED system, which enables QR-code-based device activation with cryptographically signed authorizations. The schema supports the complete customer journey from scanning a QR code through payment processing to device activation and session completion.

## 📊 Database Schema

### Tables

#### 1. **admins**
Stores administrative users who can manage the system.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | VARCHAR(255) | Admin email (unique) |
| `role` | VARCHAR(50) | Admin role (e.g., 'super_admin', 'manager') |
| `created_at` | TIMESTAMP | Account creation timestamp |

#### 2. **devices**
Raspberry Pi devices running the RemoteLED service.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `label` | VARCHAR(255) | Human-readable device name |
| `public_key` | TEXT | ECDSA public key for signature verification |
| `model` | VARCHAR(100) | Raspberry Pi model (e.g., 'RPi 4 Model B') |
| `location` | VARCHAR(255) | Physical location of the device |
| `gpio_pin` | INTEGER | GPIO pin number for relay/LED control |
| `status` | ENUM | Device status: ACTIVE, OFFLINE, MAINTENANCE, DEACTIVATED |
| `created_at` | TIMESTAMP | Device registration timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

#### 3. **services** (Products)
Services/products offered by each device.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `device_id` | UUID | Foreign key to devices table |
| `type` | ENUM | Service type: TRIGGER, FIXED, VARIABLE |
| `price_cents` | INTEGER | Price in cents |
| `fixed_minutes` | INTEGER | Duration for FIXED type (nullable) |
| `minutes_per_25c` | INTEGER | Minutes per quarter for VARIABLE type (nullable) |
| `active` | BOOLEAN | Whether service is currently available |
| `created_at` | TIMESTAMP | Service creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

**Service Types:**
- **TRIGGER**: One-time activation (2 seconds), e.g., vending machine dispense
- **FIXED**: Fixed duration, e.g., 40-minute laundry cycle
- **VARIABLE**: Pay-per-time, e.g., $0.25 per 6 minutes for air compressor

#### 4. **orders**
Customer orders tracking the complete transaction lifecycle.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `device_id` | UUID | Foreign key to devices table |
| `product_id` | UUID | Foreign key to services table |
| `amount_cents` | INTEGER | Amount paid in cents |
| `authorized_minutes` | INTEGER | Authorized duration (0 for TRIGGER) |
| `status` | ENUM | Order status (see lifecycle below) |
| `created_at` | TIMESTAMP | Order creation timestamp |
| `updated_at` | TIMESTAMP | Last status update timestamp |

**Order Lifecycle:**
```
CREATED → PAID → RUNNING → DONE
           ↓         ↓
         FAILED   FAILED
```

- **CREATED**: Order initiated, awaiting payment
- **PAID**: Payment successful, authorization signed, ready for device
- **RUNNING**: Device activated, session in progress
- **DONE**: Session completed successfully
- **FAILED**: Payment succeeded but device activation failed

#### 5. **authorizations**
Cryptographically signed authorizations sent to devices via BLE.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `order_id` | UUID | Foreign key to orders table (unique) |
| `device_id` | UUID | Foreign key to devices table |
| `payload_json` | JSONB | Signed payload containing deviceId, orderId, type, seconds, nonce, exp |
| `signature_hex` | TEXT | ECDSA signature in hexadecimal format |
| `expires_at` | TIMESTAMP | Authorization expiration time |
| `created_at` | TIMESTAMP | Authorization creation timestamp |

**Payload Structure:**
```json
{
  "deviceId": "d1111111-1111-1111-1111-111111111111",
  "orderId": "o1111111-1111-1111-1111-111111111111",
  "type": "FIXED",
  "seconds": 2400,
  "nonce": "abc123def456",
  "exp": 1728849600
}
```

#### 6. **logs**
Communication and telemetry logs between Pi devices and server.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `device_id` | UUID | Foreign key to devices table |
| `direction` | ENUM | Log direction: PI_TO_SRV or SRV_TO_PI |
| `payload_hash` | VARCHAR(64) | SHA-256 hash of payload |
| `ok` | BOOLEAN | Whether operation succeeded |
| `details` | TEXT | Additional log details |
| `created_at` | TIMESTAMP | Log entry timestamp |

**Log Directions:**
- **PI_TO_SRV**: Telemetry from device (STARTED, DONE, ERROR events)
- **SRV_TO_PI**: Commands to device (authorization payloads)

## 🚀 Setup Instructions

### Prerequisites

- PostgreSQL 15+ installed (via Homebrew on macOS)
- Access to terminal/command line

### Installation

1. **Install PostgreSQL** (if not already installed):
   ```bash
   brew install postgresql@15
   export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
   ```

2. **Start PostgreSQL service**:
   ```bash
   brew services start postgresql@15
   ```

3. **Create the database**:
   ```bash
   createdb remoteled
   ```

4. **Run the schema**:
   ```bash
   psql -d remoteled -f database/schema.sql
   ```

5. **Load seed data** (for development/testing):
   ```bash
   psql -d remoteled -f database/seed.sql
   ```

### Verification

Check that the database was set up correctly:

```bash
# Connect to database
psql remoteled

# List all tables
\dt

# View devices summary
SELECT * FROM v_devices_summary;

# View recent orders
SELECT id, device_label, service_type, status, amount_cents 
FROM v_orders_detailed 
ORDER BY created_at DESC 
LIMIT 10;

# Exit
\q
```

## 📱 Understanding the Flow

### User Journey

1. **Scan QR Code**
   - Customer scans QR code on device
   - QR contains device UUID
   - App fetches device info and available services

   ```sql
   -- Get device and its active services
   SELECT * FROM get_device_services('d1111111-1111-1111-1111-111111111111');
   ```

2. **Select Product**
   - User selects a service (TRIGGER, FIXED, or VARIABLE)
   - App displays pricing and duration

3. **Payment**
   - Order created with status `CREATED`
   - Payment processed (mock or Stripe)
   - On success, order updated to `PAID`

   ```sql
   -- Create order
   INSERT INTO orders (device_id, product_id, amount_cents, authorized_minutes, status)
   VALUES ('device_uuid', 'service_uuid', 250, 40, 'CREATED');
   
   -- Update to PAID after payment
   UPDATE orders SET status = 'PAID', updated_at = NOW()
   WHERE id = 'order_uuid';
   ```

4. **Authorization**
   - Backend creates signed authorization
   - Stored in `authorizations` table
   - Payload contains: deviceId, orderId, type, seconds, nonce, expiry

   ```sql
   -- Create authorization
   INSERT INTO authorizations (order_id, device_id, payload_json, signature_hex, expires_at)
   VALUES ('order_uuid', 'device_uuid', '{"deviceId": "...", ...}'::jsonb, 'signature', NOW() + INTERVAL '5 minutes');
   ```

5. **BLE Relay**
   - Mobile app relays authorization to Pi via BLE
   - Logged as `SRV_TO_PI` in logs table

   ```sql
   -- Log authorization sent
   INSERT INTO logs (device_id, direction, payload_hash, ok, details)
   VALUES ('device_uuid', 'SRV_TO_PI', 'sha256:abc123', true, 'Authorization sent to device');
   ```

6. **Device Activation**
   - Pi verifies signature, expiry, nonce
   - If valid, actuates GPIO/relay
   - Sends STARTED event back via BLE
   - Order status updated to `RUNNING`

   ```sql
   -- Log STARTED event received
   INSERT INTO logs (device_id, direction, ok, details)
   VALUES ('device_uuid', 'PI_TO_SRV', true, 'STARTED event received');
   
   -- Update order status
   UPDATE orders SET status = 'RUNNING', updated_at = NOW()
   WHERE id = 'order_uuid';
   ```

7. **Session Complete**
   - Device runs for authorized duration
   - Sends DONE event via BLE
   - Order status updated to `DONE`

   ```sql
   -- Log DONE event
   INSERT INTO logs (device_id, direction, ok, details)
   VALUES ('device_uuid', 'PI_TO_SRV', true, 'DONE event received');
   
   -- Complete order
   UPDATE orders SET status = 'DONE', updated_at = NOW()
   WHERE id = 'order_uuid';
   ```

## 🔧 Useful Queries

### Analytics

```sql
-- Total revenue by device
SELECT 
    d.label,
    COUNT(o.id) as total_orders,
    COUNT(o.id) FILTER (WHERE o.status = 'DONE') as completed_orders,
    SUM(o.amount_cents) FILTER (WHERE o.status = 'DONE') / 100.0 as revenue_dollars
FROM devices d
LEFT JOIN orders o ON d.id = o.device_id
GROUP BY d.id, d.label
ORDER BY revenue_dollars DESC;

-- Success rate per device
SELECT 
    d.label,
    COUNT(o.id) FILTER (WHERE o.status IN ('DONE', 'RUNNING', 'PAID')) as successful,
    COUNT(o.id) FILTER (WHERE o.status = 'FAILED') as failed,
    ROUND(100.0 * COUNT(o.id) FILTER (WHERE o.status IN ('DONE', 'RUNNING', 'PAID')) / 
          NULLIF(COUNT(o.id), 0), 2) as success_rate_pct
FROM devices d
LEFT JOIN orders o ON d.id = o.device_id
WHERE o.id IS NOT NULL
GROUP BY d.id, d.label;

-- Recent errors
SELECT 
    l.created_at,
    d.label as device,
    l.direction,
    l.details
FROM logs l
JOIN devices d ON l.device_id = d.id
WHERE l.ok = false
ORDER BY l.created_at DESC
LIMIT 20;

-- Orders awaiting activation (PAID status)
SELECT 
    o.id,
    o.created_at,
    EXTRACT(EPOCH FROM (NOW() - o.created_at)) as seconds_waiting,
    d.label as device,
    s.type as service_type,
    a.expires_at
FROM orders o
JOIN devices d ON o.device_id = d.id
JOIN services s ON o.product_id = s.id
LEFT JOIN authorizations a ON o.id = a.order_id
WHERE o.status = 'PAID';
```

### Debugging

```sql
-- Trace complete order lifecycle
WITH order_trace AS (
    SELECT 'o1111111-1111-1111-1111-111111111111'::uuid as order_id
)
SELECT 
    o.id as order_id,
    o.status,
    o.created_at as order_created,
    a.created_at as auth_created,
    a.expires_at as auth_expires,
    l.created_at as log_time,
    l.direction,
    l.details
FROM orders o
JOIN order_trace ot ON o.id = ot.order_id
LEFT JOIN authorizations a ON o.id = a.order_id
LEFT JOIN logs l ON o.device_id = l.device_id AND l.created_at >= o.created_at
ORDER BY COALESCE(l.created_at, o.created_at);

-- Check authorization validity
SELECT 
    o.id as order_id,
    o.status,
    a.expires_at,
    CASE 
        WHEN a.expires_at > NOW() THEN 'Valid'
        ELSE 'Expired'
    END as auth_status,
    EXTRACT(EPOCH FROM (a.expires_at - NOW())) as seconds_until_expiry
FROM orders o
JOIN authorizations a ON o.id = a.order_id
WHERE o.status IN ('PAID', 'RUNNING');
```

## 🔒 Security Considerations

1. **Signature Verification**: Devices verify ECDSA signatures using stored public keys
2. **Nonce Protection**: Prevents replay attacks via one-time nonces
3. **Expiry Times**: Authorizations expire after 5 minutes
4. **Payload Hashing**: All communication is logged with SHA-256 hashes
5. **JSONB Storage**: Enables flexible querying of authorization payloads

## 🛠️ Maintenance

### Backup

```bash
# Backup entire database
pg_dump remoteled > remoteled_backup_$(date +%Y%m%d).sql

# Restore from backup
psql remoteled < remoteled_backup_20251013.sql
```

### Reset Database

```bash
# Drop and recreate
dropdb remoteled
createdb remoteled
psql -d remoteled -f database/schema.sql
psql -d remoteled -f database/seed.sql
```

### Connection String

For application configuration:

```
postgresql://localhost:5432/remoteled
```

Or with user/password:

```
postgresql://username:password@localhost:5432/remoteled
```

## 📚 Additional Resources

- [PostgreSQL 15 Documentation](https://www.postgresql.org/docs/15/)
- [JSONB Functions](https://www.postgresql.org/docs/15/functions-json.html)
- [UUID Generation](https://www.postgresql.org/docs/15/functions-uuid.html)

## 🤝 Contributing

When making schema changes:

1. Update `schema.sql` with migration-friendly changes
2. Add corresponding seed data to `seed.sql`
3. Update this README with new tables/columns
4. Test locally before committing
5. Document any breaking changes

---

**Last Updated**: October 13, 2025  
**PostgreSQL Version**: 15.14  
**Schema Version**: 1.0.0

