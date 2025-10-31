-- RemoteLED Seed Data
-- Mock data for testing the complete QR-to-activation flow
-- PostgreSQL 15+
-- Created: 2025-10-13

-- ============================================================
-- CLEAR EXISTING DATA
-- ============================================================
TRUNCATE TABLE logs, authorizations, orders, services, devices, admins CASCADE;

-- ============================================================
-- ADMINS
-- ============================================================
-- Note: password_hash is bcrypt hash of 'password123' for all test users
INSERT INTO admins (id, email, password_hash, role, created_at) VALUES
('a1111111-1111-1111-1111-111111111111', 'admin@remoteled.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5uyT5z.qNqI5i', 'super_admin', NOW() - INTERVAL '90 days'),
('a2222222-2222-2222-2222-222222222222', 'owner@laundromat.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5uyT5z.qNqI5i', 'device_owner', NOW() - INTERVAL '60 days'),
('a3333333-3333-3333-3333-333333333333', 'manager@vending.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5uyT5z.qNqI5i', 'manager', NOW() - INTERVAL '30 days');

-- ============================================================
-- DEVICES
-- ============================================================
-- Mock ECDSA public keys (for demo purposes - replace with real keys in production)
INSERT INTO devices (id, label, public_key, model, location, gpio_pin, status, created_at) VALUES
(
    'd1111111-1111-1111-1111-111111111111',
    'Laundry Room A',
    '04a12b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f',
    'RPi 4 Model B',
    'Building 5, Floor 2',
    17,
    'ACTIVE',
    NOW() - INTERVAL '60 days'
),
(
    'd2222222-2222-2222-2222-222222222222',
    'Vending Machine #42',
    '045f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a',
    'RPi 4 Model B',
    'Main Lobby',
    18,
    'ACTIVE',
    NOW() - INTERVAL '45 days'
),
(
    'd3333333-3333-3333-3333-333333333333',
    'Air Compressor Station',
    '04b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1',
    'RPi Zero 2 W',
    'Garage Level -1',
    22,
    'ACTIVE',
    NOW() - INTERVAL '30 days'
),
(
    'd4444444-4444-4444-4444-444444444444',
    'Massage Chair #7',
    '046e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5',
    'RPi 4 Model B',
    'Spa Center, 3rd Floor',
    23,
    'OFFLINE',
    NOW() - INTERVAL '15 days'
);

-- ============================================================
-- SERVICES (Products for each device)
-- ============================================================

-- Laundry Room A Services
INSERT INTO services (id, device_id, type, price_cents, fixed_minutes, minutes_per_25c, active) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'd1111111-1111-1111-1111-111111111111',
    'FIXED',
    250, -- $2.50
    40,  -- 40 minutes
    NULL,
    true
),
(
    '11111111-2222-2222-2222-222222222222',
    'd1111111-1111-1111-1111-111111111111',
    'TRIGGER',
    100, -- $1.00
    NULL,
    NULL,
    true
),
(
    '11111111-3333-3333-3333-333333333333',
    'd1111111-1111-1111-1111-111111111111',
    'VARIABLE',
    25,  -- $0.25 per increment
    NULL,
    6,   -- 6 minutes per 25 cents
    true
);

-- Vending Machine Services
INSERT INTO services (id, device_id, type, price_cents, fixed_minutes, minutes_per_25c, active) VALUES
(
    '22222222-1111-1111-1111-111111111111',
    'd2222222-2222-2222-2222-222222222222',
    'TRIGGER',
    150, -- $1.50 - single dispense
    NULL,
    NULL,
    true
),
(
    '22222222-2222-2222-2222-222222222222',
    'd2222222-2222-2222-2222-222222222222',
    'TRIGGER',
    200, -- $2.00 - premium dispense
    NULL,
    NULL,
    true
);

-- Air Compressor Services
INSERT INTO services (id, device_id, type, price_cents, fixed_minutes, minutes_per_25c, active) VALUES
(
    '33333333-1111-1111-1111-111111111111',
    'd3333333-3333-3333-3333-333333333333',
    'VARIABLE',
    25,  -- $0.25 per increment
    NULL,
    3,   -- 3 minutes per quarter
    true
),
(
    '33333333-2222-2222-2222-222222222222',
    'd3333333-3333-3333-3333-333333333333',
    'FIXED',
    100, -- $1.00
    10,  -- 10 minutes
    NULL,
    true
);

-- Massage Chair Services
INSERT INTO services (id, device_id, type, price_cents, fixed_minutes, minutes_per_25c, active) VALUES
(
    '44444444-1111-1111-1111-111111111111',
    'd4444444-4444-4444-4444-444444444444',
    'FIXED',
    500, -- $5.00
    15,  -- 15 minutes
    NULL,
    true
),
(
    '44444444-2222-2222-2222-222222222222',
    'd4444444-4444-4444-4444-444444444444',
    'FIXED',
    300, -- $3.00
    8,   -- 8 minutes
    NULL,
    true
);

-- ============================================================
-- ORDERS (Various states demonstrating the lifecycle)
-- ============================================================

-- COMPLETED ORDER (full lifecycle example)
INSERT INTO orders (id, device_id, product_id, amount_cents, authorized_minutes, status, created_at, updated_at) VALUES
(
    '01111111-1111-1111-1111-111111111111',
    'd1111111-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    250,
    40,
    'DONE',
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '1 hour 20 minutes'
);

-- CURRENTLY RUNNING ORDER
INSERT INTO orders (id, device_id, product_id, amount_cents, authorized_minutes, status, created_at, updated_at) VALUES
(
    '02222222-2222-2222-2222-222222222222',
    'd2222222-2222-2222-2222-222222222222',
    '22222222-1111-1111-1111-111111111111',
    150,
    0, -- TRIGGER has 0 duration
    'RUNNING',
    NOW() - INTERVAL '30 seconds',
    NOW() - INTERVAL '10 seconds'
);

-- PAID BUT NOT YET ACTIVATED
INSERT INTO orders (id, device_id, product_id, amount_cents, authorized_minutes, status, created_at, updated_at) VALUES
(
    '03333333-3333-3333-3333-333333333333',
    'd3333333-3333-3333-3333-333333333333',
    '33333333-1111-1111-1111-111111111111',
    100, -- $1.00 = 4 quarters = 12 minutes
    12,
    'PAID',
    NOW() - INTERVAL '45 seconds',
    NOW() - INTERVAL '45 seconds'
);

-- CREATED BUT NOT YET PAID
INSERT INTO orders (id, device_id, product_id, amount_cents, authorized_minutes, status, created_at, updated_at) VALUES
(
    '04444444-4444-4444-4444-444444444444',
    'd1111111-1111-1111-1111-111111111111',
    '11111111-3333-3333-3333-333333333333',
    200, -- $2.00 = 8 quarters = 48 minutes
    48,
    'CREATED',
    NOW() - INTERVAL '2 minutes',
    NOW() - INTERVAL '2 minutes'
);

-- FAILED ORDER (payment succeeded but device activation failed)
INSERT INTO orders (id, device_id, product_id, amount_cents, authorized_minutes, status, created_at, updated_at) VALUES
(
    '05555555-5555-5555-5555-555555555555',
    'd4444444-4444-4444-4444-444444444444',
    '44444444-1111-1111-1111-111111111111',
    500,
    15,
    'FAILED',
    NOW() - INTERVAL '10 minutes',
    NOW() - INTERVAL '9 minutes'
);

-- Additional completed orders for analytics
INSERT INTO orders (id, device_id, product_id, amount_cents, authorized_minutes, status, created_at, updated_at) VALUES
('06666666-6666-6666-6666-666666666666', 'd1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 250, 40, 'DONE', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '40 minutes'),
('07777777-7777-7777-7777-777777777777', 'd1111111-1111-1111-1111-111111111111', '11111111-2222-2222-2222-222222222222', 100, 0, 'DONE', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '2 seconds'),
('08888888-8888-8888-8888-888888888888', 'd2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 200, 0, 'DONE', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours' + INTERVAL '2 seconds'),
('09999999-9999-9999-9999-999999999999', 'd3333333-3333-3333-3333-333333333333', '33333333-2222-2222-2222-222222222222', 100, 10, 'DONE', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours' + INTERVAL '10 minutes');

-- ============================================================
-- AUTHORIZATIONS
-- ============================================================

-- Authorization for completed order
INSERT INTO authorizations (id, order_id, device_id, payload_json, signature_hex, expires_at, created_at) VALUES
(
    '00a11111-1111-1111-1111-111111111111',
    '01111111-1111-1111-1111-111111111111',
    'd1111111-1111-1111-1111-111111111111',
    '{
        "deviceId": "d1111111-1111-1111-1111-111111111111",
        "orderId": "01111111-1111-1111-1111-111111111111",
        "type": "FIXED",
        "seconds": 2400,
        "nonce": "abc123def456",
        "exp": 1728849600
    }'::jsonb,
    '3045022100a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890022012345678901234567890abcdef1234567890abcdef1234567890abcdef123456',
    NOW() - INTERVAL '1 hour 50 minutes',
    NOW() - INTERVAL '2 hours'
);

-- Authorization for currently running order
INSERT INTO authorizations (id, order_id, device_id, payload_json, signature_hex, expires_at, created_at) VALUES
(
    '00a22222-2222-2222-2222-222222222222',
    '02222222-2222-2222-2222-222222222222',
    'd2222222-2222-2222-2222-222222222222',
    '{
        "deviceId": "d2222222-2222-2222-2222-222222222222",
        "orderId": "02222222-2222-2222-2222-222222222222",
        "type": "TRIGGER",
        "seconds": 2,
        "nonce": "xyz789ghi012",
        "exp": 1728950400
    }'::jsonb,
    '30450221009876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef02200fedcba0987654321fedcba0987654321fedcba0987654321fedcba098765432',
    NOW() + INTERVAL '4 minutes 30 seconds',
    NOW() - INTERVAL '30 seconds'
);

-- Authorization for paid but not activated order
INSERT INTO authorizations (id, order_id, device_id, payload_json, signature_hex, expires_at, created_at) VALUES
(
    '00a33333-3333-3333-3333-333333333333',
    '03333333-3333-3333-3333-333333333333',
    'd3333333-3333-3333-3333-333333333333',
    '{
        "deviceId": "d3333333-3333-3333-3333-333333333333",
        "orderId": "03333333-3333-3333-3333-333333333333",
        "type": "VARIABLE",
        "seconds": 720,
        "nonce": "mno345pqr678",
        "exp": 1728950700
    }'::jsonb,
    '3044022056789abcdef0123456789abcdef0123456789abcdef0123456789abcdef012345022023456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123',
    NOW() + INTERVAL '4 minutes 15 seconds',
    NOW() - INTERVAL '45 seconds'
);

-- ============================================================
-- LOGS (Communication and telemetry logs)
-- ============================================================

-- Logs for completed order lifecycle
INSERT INTO logs (device_id, direction, payload_hash, ok, details, created_at) VALUES
('d1111111-1111-1111-1111-111111111111', 'SRV_TO_PI', 'sha256:a1b2c3d4e5f6', true, 'Authorization sent to device', NOW() - INTERVAL '2 hours'),
('d1111111-1111-1111-1111-111111111111', 'PI_TO_SRV', 'sha256:f6e5d4c3b2a1', true, 'STARTED event received', NOW() - INTERVAL '2 hours' + INTERVAL '3 seconds'),
('d1111111-1111-1111-1111-111111111111', 'PI_TO_SRV', 'sha256:123abc456def', true, 'DONE event received', NOW() - INTERVAL '1 hour 20 minutes');

-- Logs for currently running order
INSERT INTO logs (device_id, direction, payload_hash, ok, details, created_at) VALUES
('d2222222-2222-2222-2222-222222222222', 'SRV_TO_PI', 'sha256:9876543210ab', true, 'Authorization sent to device', NOW() - INTERVAL '30 seconds'),
('d2222222-2222-2222-2222-222222222222', 'PI_TO_SRV', 'sha256:ba0123456789', true, 'STARTED event received', NOW() - INTERVAL '20 seconds');

-- Logs for paid but not activated order
INSERT INTO logs (device_id, direction, payload_hash, ok, details, created_at) VALUES
('d3333333-3333-3333-3333-333333333333', 'SRV_TO_PI', 'sha256:def456abc789', true, 'Authorization sent to device', NOW() - INTERVAL '45 seconds');

-- Logs for failed order
INSERT INTO logs (device_id, direction, payload_hash, ok, details, created_at) VALUES
('d4444444-4444-4444-4444-444444444444', 'SRV_TO_PI', 'sha256:fedcba987654', true, 'Authorization sent to device', NOW() - INTERVAL '10 minutes'),
('d4444444-4444-4444-4444-444444444444', 'PI_TO_SRV', 'sha256:456789abcdef', false, 'ERROR: Device offline', NOW() - INTERVAL '9 minutes 50 seconds');

-- Additional system logs
INSERT INTO logs (device_id, direction, payload_hash, ok, details, created_at) VALUES
('d1111111-1111-1111-1111-111111111111', 'PI_TO_SRV', 'sha256:heartbeat001', true, 'Device heartbeat', NOW() - INTERVAL '5 minutes'),
('d2222222-2222-2222-2222-222222222222', 'PI_TO_SRV', 'sha256:heartbeat002', true, 'Device heartbeat', NOW() - INTERVAL '3 minutes'),
('d3333333-3333-3333-3333-333333333333', 'PI_TO_SRV', 'sha256:heartbeat003', true, 'Device heartbeat', NOW() - INTERVAL '2 minutes'),
('d4444444-4444-4444-4444-444444444444', 'PI_TO_SRV', 'sha256:heartbeat004', false, 'Device heartbeat timeout', NOW() - INTERVAL '30 minutes');

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

DO $$
DECLARE
    admin_count INTEGER;
    device_count INTEGER;
    service_count INTEGER;
    order_count INTEGER;
    auth_count INTEGER;
    log_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO admin_count FROM admins;
    SELECT COUNT(*) INTO device_count FROM devices;
    SELECT COUNT(*) INTO service_count FROM services;
    SELECT COUNT(*) INTO order_count FROM orders;
    SELECT COUNT(*) INTO auth_count FROM authorizations;
    SELECT COUNT(*) INTO log_count FROM logs;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '✓ RemoteLED seed data loaded successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Data Summary:';
    RAISE NOTICE '  - Admins: % records', admin_count;
    RAISE NOTICE '  - Devices: % records', device_count;
    RAISE NOTICE '  - Services: % records', service_count;
    RAISE NOTICE '  - Orders: % records', order_count;
    RAISE NOTICE '  - Authorizations: % records', auth_count;
    RAISE NOTICE '  - Logs: % records', log_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Sample Data Highlights:';
    RAISE NOTICE '  - Laundry Room A (Device 1): 3 services, multiple orders';
    RAISE NOTICE '  - Vending Machine #42 (Device 2): 2 services, active order';
    RAISE NOTICE '  - Air Compressor (Device 3): 2 services, pending activation';
    RAISE NOTICE '  - Massage Chair #7 (Device 4): 2 services, offline';
    RAISE NOTICE '';
    RAISE NOTICE 'Order States:';
    RAISE NOTICE '  - DONE: Completed orders';
    RAISE NOTICE '  - RUNNING: Currently active';
    RAISE NOTICE '  - PAID: Awaiting device activation';
    RAISE NOTICE '  - CREATED: Awaiting payment';
    RAISE NOTICE '  - FAILED: Activation failed';
    RAISE NOTICE '========================================';
END $$;

