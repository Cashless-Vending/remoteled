-- RemoteLED Seed Data
-- Mock data for testing the complete QR-to-activation flow
-- PostgreSQL 15+
-- Created: 2025-10-13
-- Updated: 2025-11-03 - Corrected for global services model with valid UUIDs

-- ============================================================
-- CLEAR EXISTING DATA
-- ============================================================
TRUNCATE TABLE logs, authorizations, orders, device_services, services, devices, device_models, locations, service_types, admins CASCADE;

-- ============================================================
-- ADMINS
-- ============================================================
-- Note: password_hash is bcrypt hash of 'password123' for all test users
INSERT INTO admins (id, email, password_hash, role, created_at) VALUES
('a1111111-1111-1111-1111-111111111111', 'admin@remoteled.com', '$2b$12$jIK7wrS49hEcFqJ194tuZ.Of1Xco2ENclslsc3XXCzztp4bLIXQrO', 'super_admin', NOW() - INTERVAL '90 days'),
('a2222222-2222-2222-2222-222222222222', 'owner@laundromat.com', '$2b$12$jIK7wrS49hEcFqJ194tuZ.Of1Xco2ENclslsc3XXCzztp4bLIXQrO', 'device_owner', NOW() - INTERVAL '60 days'),
('a3333333-3333-3333-3333-333333333333', 'manager@vending.com', '$2b$12$jIK7wrS49hEcFqJ194tuZ.Of1Xco2ENclslsc3XXCzztp4bLIXQrO', 'manager', NOW() - INTERVAL '30 days');

-- ============================================================
-- DEVICE MODELS (Reference Data)
-- ============================================================
INSERT INTO device_models (id, name, description, created_at) VALUES
('1a111111-1111-1111-1111-111111111111', 'RPi 4 Model B', 'Raspberry Pi 4 Model B - 4GB RAM', NOW() - INTERVAL '180 days'),
('2a222222-2222-2222-2222-222222222222', 'RPi Zero 2 W', 'Raspberry Pi Zero 2 W - Compact wireless model', NOW() - INTERVAL '180 days'),
('3a333333-3333-3333-3333-333333333333', 'RPi 3 Model B+', 'Raspberry Pi 3 Model B+ - Previous generation', NOW() - INTERVAL '180 days'),
('4a444444-4444-4444-4444-444444444444', 'RPi 400', 'Raspberry Pi 400 - Keyboard computer', NOW() - INTERVAL '180 days');

-- ============================================================
-- LOCATIONS (Reference Data)
-- ============================================================
INSERT INTO locations (id, name, description, created_at) VALUES
('1b111111-1111-1111-1111-111111111111', 'Building 5, Floor 2', 'Main office building, second floor', NOW() - INTERVAL '180 days'),
('2b222222-2222-2222-2222-222222222222', 'Main Lobby', 'Ground floor main entrance area', NOW() - INTERVAL '180 days'),
('3b333333-3333-3333-3333-333333333333', 'Garage Level -1', 'Underground parking level 1', NOW() - INTERVAL '180 days'),
('4b444444-4444-4444-4444-444444444444', 'Warehouse A', 'Primary storage warehouse', NOW() - INTERVAL '180 days'),
('5b555555-5555-5555-5555-555555555555', 'Production Floor', 'Main production area', NOW() - INTERVAL '180 days');

-- ============================================================
-- SERVICE TYPES (Reference Data)
-- ============================================================
INSERT INTO service_types (id, name, code, description, created_at) VALUES
('1c111111-1111-1111-1111-111111111111', 'Trigger Service', 'TRIGGER', 'One-time activation service triggered by QR scan', NOW() - INTERVAL '180 days'),
('2c222222-2222-2222-2222-222222222222', 'Fixed Duration Service', 'FIXED', 'Service with a predetermined fixed duration', NOW() - INTERVAL '180 days'),
('3c333333-3333-3333-3333-333333333333', 'Variable Duration Service', 'VARIABLE', 'Service with flexible duration based on usage', NOW() - INTERVAL '180 days');

-- ============================================================
-- DEVICES
-- ============================================================
INSERT INTO devices (id, label, public_key, model, location, model_id, location_id, gpio_pin, status, created_at) VALUES
('d1111111-1111-1111-1111-111111111111', 'Laundry Room A', '04a12b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f', 'RPi 4 Model B', 'Building 5, Floor 2', '1a111111-1111-1111-1111-111111111111', '1b111111-1111-1111-1111-111111111111', 17, 'ACTIVE', NOW() - INTERVAL '60 days'),
('d2222222-2222-2222-2222-222222222222', 'Vending Machine #42', '045f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a', 'RPi 4 Model B', 'Main Lobby', '1a111111-1111-1111-1111-111111111111', '2b222222-2222-2222-2222-222222222222', 18, 'ACTIVE', NOW() - INTERVAL '45 days'),
('d3333333-3333-3333-3333-333333333333', 'Air Compressor Station', '04b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1', 'RPi Zero 2 W', 'Garage Level -1', '2a222222-2222-2222-2222-222222222222', '3b333333-3333-3333-3333-333333333333', 22, 'ACTIVE', NOW() - INTERVAL '30 days'),
('d4444444-4444-4444-4444-444444444444', 'Massage Chair #7', '046e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5', 'RPi 4 Model B', 'Spa Center, 3rd Floor', '1a111111-1111-1111-1111-111111111111', NULL, 23, 'OFFLINE', NOW() - INTERVAL '15 days'),
('d5555555-5555-5555-5555-555555555555', 'EV Charging Station #3', '04c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2', 'RPi 400', 'Parking Lot East', '4a444444-4444-4444-4444-444444444444', '3b333333-3333-3333-3333-333333333333', 27, 'MAINTENANCE', NOW() - INTERVAL '10 days');

-- ============================================================
-- GLOBAL SERVICES
-- ============================================================
INSERT INTO services (id, type, price_cents, fixed_minutes, minutes_per_25c, active, created_at) VALUES
('11111111-1111-1111-1111-111111111111', 'FIXED', 250, 40, NULL, true, NOW() - INTERVAL '60 days'),
('11111111-2222-2222-2222-222222222222', 'FIXED', 500, 15, NULL, true, NOW() - INTERVAL '60 days'),
('11111111-3333-3333-3333-333333333333', 'FIXED', 300, 8, NULL, true, NOW() - INTERVAL '60 days'),
('11111111-4444-4444-4444-444444444444', 'FIXED', 100, 10, NULL, true, NOW() - INTERVAL '60 days'),
('22222222-1111-1111-1111-111111111111', 'TRIGGER', 100, NULL, NULL, true, NOW() - INTERVAL '60 days'),
('22222222-2222-2222-2222-222222222222', 'TRIGGER', 150, NULL, NULL, true, NOW() - INTERVAL '60 days'),
('22222222-3333-3333-3333-333333333333', 'TRIGGER', 200, NULL, NULL, true, NOW() - INTERVAL '60 days'),
('33333333-1111-1111-1111-111111111111', 'VARIABLE', 25, NULL, 6, true, NOW() - INTERVAL '60 days'),
('33333333-2222-2222-2222-222222222222', 'VARIABLE', 25, NULL, 3, true, NOW() - INTERVAL '60 days');

-- ============================================================
-- DEVICE-SERVICE ASSIGNMENTS
-- ============================================================
INSERT INTO device_services (device_id, service_id) VALUES
('d1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111'),
('d1111111-1111-1111-1111-111111111111', '22222222-1111-1111-1111-111111111111'),
('d1111111-1111-1111-1111-111111111111', '33333333-1111-1111-1111-111111111111'),
('d2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222'),
('d2222222-2222-2222-2222-222222222222', '22222222-3333-3333-3333-333333333333'),
('d3333333-3333-3333-3333-333333333333', '33333333-2222-2222-2222-222222222222'),
('d3333333-3333-3333-3333-333333333333', '11111111-4444-4444-4444-444444444444'),
('d4444444-4444-4444-4444-444444444444', '11111111-2222-2222-2222-222222222222'),
('d4444444-4444-4444-4444-444444444444', '11111111-3333-3333-3333-333333333333'),
('d5555555-5555-5555-5555-555555555555', '33333333-1111-1111-1111-111111111111');

-- ============================================================
-- ORDERS (Hourly data for the past 48 hours)
-- ============================================================
INSERT INTO orders (id, device_id, service_id, amount_cents, authorized_minutes, status, created_at, updated_at) VALUES
-- 48 hours ago
('aa100001-0000-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 250, 40, 'DONE', NOW() - INTERVAL '48 hours', NOW() - INTERVAL '47 hours 20 minutes'),
('aa100001-0000-0000-0000-000000000002', 'd2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 150, 0, 'DONE', NOW() - INTERVAL '48 hours', NOW() - INTERVAL '47 hours 59 minutes'),
('aa100001-0000-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '33333333-2222-2222-2222-222222222222', 100, 12, 'DONE', NOW() - INTERVAL '48 hours', NOW() - INTERVAL '47 hours 48 minutes'),
-- 47 hours ago
('aa100002-0000-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '22222222-1111-1111-1111-111111111111', 100, 0, 'DONE', NOW() - INTERVAL '47 hours', NOW() - INTERVAL '46 hours 59 minutes'),
('aa100002-0000-0000-0000-000000000002', 'd4444444-4444-4444-4444-444444444444', '11111111-2222-2222-2222-222222222222', 500, 15, 'FAILED', NOW() - INTERVAL '47 hours', NOW() - INTERVAL '46 hours 30 minutes'),
-- 46 hours ago
('aa100003-0000-0000-0000-000000000001', 'd2222222-2222-2222-2222-222222222222', '22222222-3333-3333-3333-333333333333', 200, 0, 'DONE', NOW() - INTERVAL '46 hours', NOW() - INTERVAL '45 hours 59 minutes'),
('aa100003-0000-0000-0000-000000000002', 'd1111111-1111-1111-1111-111111111111', '33333333-1111-1111-1111-111111111111', 75, 18, 'DONE', NOW() - INTERVAL '46 hours', NOW() - INTERVAL '45 hours 42 minutes'),
('aa100003-0000-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '11111111-4444-4444-4444-444444444444', 100, 10, 'DONE', NOW() - INTERVAL '46 hours', NOW() - INTERVAL '45 hours 50 minutes'),
-- 24 hours ago
('aa100024-0000-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 250, 40, 'DONE', NOW() - INTERVAL '24 hours', NOW() - INTERVAL '23 hours 20 minutes'),
('aa100024-0000-0000-0000-000000000002', 'd2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 150, 0, 'DONE', NOW() - INTERVAL '24 hours', NOW() - INTERVAL '23 hours 59 minutes'),
('aa100024-0000-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '33333333-2222-2222-2222-222222222222', 100, 12, 'DONE', NOW() - INTERVAL '24 hours', NOW() - INTERVAL '23 hours 48 minutes'),
('aa100024-0000-0000-0000-000000000004', 'd4444444-4444-4444-4444-444444444444', '11111111-2222-2222-2222-222222222222', 500, 15, 'DONE', NOW() - INTERVAL '24 hours', NOW() - INTERVAL '23 hours 45 minutes'),
-- 12 hours ago
('aa100012-0000-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '22222222-1111-1111-1111-111111111111', 100, 0, 'DONE', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '11 hours 59 minutes'),
('aa100012-0000-0000-0000-000000000002', 'd2222222-2222-2222-2222-222222222222', '22222222-3333-3333-3333-333333333333', 200, 0, 'DONE', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '11 hours 59 minutes'),
('aa100012-0000-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '11111111-4444-4444-4444-444444444444', 100, 10, 'DONE', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '11 hours 50 minutes'),
('aa100012-0000-0000-0000-000000000004', 'd1111111-1111-1111-1111-111111111111', '33333333-1111-1111-1111-111111111111', 75, 18, 'DONE', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '11 hours 42 minutes'),
('aa100012-0000-0000-0000-000000000005', 'd4444444-4444-4444-4444-444444444444', '11111111-3333-3333-3333-333333333333', 300, 8, 'DONE', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '11 hours 52 minutes'),
-- 6 hours ago
('aa100006-1111-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 250, 40, 'DONE', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 20 minutes'),
('aa100006-1111-0000-0000-000000000002', 'd2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 150, 0, 'DONE', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 59 minutes'),
('aa100006-1111-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '33333333-2222-2222-2222-222222222222', 125, 15, 'DONE', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 45 minutes'),
('aa100006-1111-0000-0000-000000000004', 'd1111111-1111-1111-1111-111111111111', '22222222-1111-1111-1111-111111111111', 100, 0, 'DONE', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 59 minutes'),
('aa100006-1111-0000-0000-000000000005', 'd4444444-4444-4444-4444-444444444444', '11111111-2222-2222-2222-222222222222', 500, 15, 'DONE', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 45 minutes'),
('aa100006-1111-0000-0000-000000000006', 'd2222222-2222-2222-2222-222222222222', '22222222-3333-3333-3333-333333333333', 200, 0, 'DONE', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 59 minutes'),
-- 3 hours ago
('aa100003-1111-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '33333333-1111-1111-1111-111111111111', 50, 12, 'DONE', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours 48 minutes'),
('aa100003-1111-0000-0000-000000000002', 'd3333333-3333-3333-3333-333333333333', '11111111-4444-4444-4444-444444444444', 100, 10, 'DONE', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours 50 minutes'),
('aa100003-1111-0000-0000-000000000003', 'd2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 150, 0, 'DONE', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours 59 minutes'),
('aa100003-1111-0000-0000-000000000004', 'd1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 250, 40, 'DONE', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours 20 minutes'),
('aa100003-1111-0000-0000-000000000005', 'd4444444-4444-4444-4444-444444444444', '11111111-3333-3333-3333-333333333333', 300, 8, 'DONE', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours 52 minutes'),
-- 2 hours ago
('aa100002-1111-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '22222222-1111-1111-1111-111111111111', 100, 0, 'DONE', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 59 minutes'),
('aa100002-1111-0000-0000-000000000002', 'd2222222-2222-2222-2222-222222222222', '22222222-3333-3333-3333-333333333333', 200, 0, 'DONE', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 59 minutes'),
('aa100002-1111-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '33333333-2222-2222-2222-222222222222', 100, 12, 'DONE', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 48 minutes'),
('aa100002-1111-0000-0000-000000000004', 'd1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 250, 40, 'RUNNING', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 20 minutes'),
-- 1 hour ago
('aa100001-1111-0000-0000-000000000001', 'd2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 150, 0, 'DONE', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '59 minutes'),
('aa100001-1111-0000-0000-000000000002', 'd3333333-3333-3333-3333-333333333333', '11111111-4444-4444-4444-444444444444', 100, 10, 'DONE', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '50 minutes'),
('aa100001-1111-0000-0000-000000000003', 'd1111111-1111-1111-1111-111111111111', '33333333-1111-1111-1111-111111111111', 75, 18, 'RUNNING', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '42 minutes'),
('aa100001-1111-0000-0000-000000000004', 'd4444444-4444-4444-4444-444444444444', '11111111-2222-2222-2222-222222222222', 500, 15, 'PAID', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour'),
-- Recent (30 min)
('aa100000-1111-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '22222222-1111-1111-1111-111111111111', 100, 0, 'RUNNING', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '9 minutes'),
('aa100000-1111-0000-0000-000000000002', 'd2222222-2222-2222-2222-222222222222', '22222222-3333-3333-3333-333333333333', 200, 0, 'PAID', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes'),
('aa100000-1111-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '33333333-2222-2222-2222-222222222222', 50, 6, 'CREATED', NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '2 minutes');

-- ============================================================
-- AUTHORIZATIONS
-- ============================================================
INSERT INTO authorizations (id, order_id, device_id, payload_json, signature_hex, expires_at, created_at) VALUES
('aaaa0001-1111-1111-1111-111111111111', 'aa100001-0000-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', '{"service_id":"11111111-1111-1111-1111-111111111111","duration":2400}'::jsonb, 'f9d0e8c7b6a5948372615049382716053948a29b1c0d2e3f4a5b6c7d8e9f0a1b', NOW() + INTERVAL '1 day', NOW() - INTERVAL '48 hours'),
('aaaa0002-2222-2222-2222-222222222222', 'aa100001-0000-0000-0000-000000000002', 'd2222222-2222-2222-2222-222222222222', '{"service_id":"22222222-2222-2222-2222-222222222222","duration":2}'::jsonb, 'a1b2c3d4e5f6071829384950617283940526374859607182930415263748596071', NOW() + INTERVAL '1 day', NOW() - INTERVAL '48 hours'),
('aaaa0003-3333-3333-3333-333333333333', 'aa100001-0000-0000-0000-000000000003', 'd3333333-3333-3333-3333-333333333333', '{"service_id":"33333333-2222-2222-2222-222222222222","duration":720}'::jsonb, 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3', NOW() + INTERVAL '1 day', NOW() - INTERVAL '48 hours');

-- ============================================================
-- LOGS
-- ============================================================
INSERT INTO logs (id, device_id, direction, payload_hash, ok, details, created_at) VALUES
-- Device heartbeats
('aaaaaaaa-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 'PI_TO_SRV', 'a1b2c3d4e5f6', true, 'Device heartbeat - online', NOW() - INTERVAL '60 days'),
('aaaaaaaa-2222-2222-2222-222222222222', 'd2222222-2222-2222-2222-222222222222', 'PI_TO_SRV', 'b2c3d4e5f6a7', true, 'Device heartbeat - online', NOW() - INTERVAL '45 days'),
('aaaaaaaa-3333-3333-3333-333333333333', 'd3333333-3333-3333-3333-333333333333', 'PI_TO_SRV', 'c3d4e5f6a7b8', true, 'Device heartbeat - online', NOW() - INTERVAL '30 days'),
('aaaaaaaa-4444-4444-4444-444444444444', 'd4444444-4444-4444-4444-444444444444', 'PI_TO_SRV', 'd4e5f6a7b8c9', false, 'Device connection lost', NOW() - INTERVAL '15 days'),
('aaaaaaaa-5555-5555-5555-555555555555', 'd5555555-5555-5555-5555-555555555555', 'PI_TO_SRV', 'e5f6a7b8c9d0', true, 'Device maintenance mode', NOW() - INTERVAL '10 days'),
-- Server commands
('bbbbbbbb-6666-6666-6666-666666666666', 'd1111111-1111-1111-1111-111111111111', 'SRV_TO_PI', 'f6a7b8c9d0e1', true, 'Activation command sent - FIXED 40min', NOW() - INTERVAL '48 hours'),
('bbbbbbbb-7777-7777-7777-777777777777', 'd2222222-2222-2222-2222-222222222222', 'SRV_TO_PI', '071829384950', true, 'Activation command sent - TRIGGER', NOW() - INTERVAL '48 hours'),
('bbbbbbbb-8888-8888-8888-888888888888', 'd3333333-3333-3333-3333-333333333333', 'SRV_TO_PI', '182930415263', true, 'Activation command sent - VARIABLE 12min', NOW() - INTERVAL '48 hours'),
('bbbbbbbb-9999-9999-9999-999999999999', 'd1111111-1111-1111-1111-111111111111', 'SRV_TO_PI', '293041526374', true, 'Activation command sent - TRIGGER', NOW() - INTERVAL '10 minutes'),
('bbbbbbbb-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'd1111111-1111-1111-1111-111111111111', 'SRV_TO_PI', '304152637485', true, 'Activation command sent - VARIABLE 18min', NOW() - INTERVAL '1 hour'),
-- Recent communications
('cccccccc-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'd1111111-1111-1111-1111-111111111111', 'PI_TO_SRV', '415263748596', true, 'QR scan acknowledgment', NOW() - INTERVAL '10 minutes'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'd2222222-2222-2222-2222-222222222222', 'PI_TO_SRV', '526374859607', true, 'Payment confirmation received', NOW() - INTERVAL '5 minutes'),
('cccccccc-dddd-dddd-dddd-dddddddddddd', 'd3333333-3333-3333-3333-333333333333', 'PI_TO_SRV', '637485960718', true, 'Service completion notification', NOW() - INTERVAL '3 hours'),
('cccccccc-eeee-eeee-eeee-eeeeeeeeeeee', 'd4444444-4444-4444-4444-444444444444', 'PI_TO_SRV', '748596071829', false, 'Failed to send heartbeat', NOW() - INTERVAL '15 days'),
('cccccccc-ffff-ffff-ffff-ffffffffffff', 'd1111111-1111-1111-1111-111111111111', 'SRV_TO_PI', '859607182930', false, 'Failed to deliver command - device offline', NOW() - INTERVAL '2 days');

-- ============================================================
-- COMPLETION MESSAGE
-- ============================================================
SELECT 'Seed data loaded successfully!' AS message;
SELECT 'Tables populated:' AS info;
SELECT '- admins (3 test accounts)' AS detail;
SELECT '- device_models (4 models)' AS detail;
SELECT '- locations (5 locations)' AS detail;
SELECT '- service_types (3 service types)' AS detail;
SELECT '- devices (5 test devices)' AS detail;
SELECT '- services (9 global services)' AS detail;
SELECT '- device_services (10 assignments)' AS detail;
SELECT '- orders (40+ orders with hourly timestamps)' AS detail;
SELECT '- authorizations (3 test authorizations)' AS detail;
SELECT '- logs (15 communication logs)' AS detail;
