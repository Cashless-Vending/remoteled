-- RemoteLED Database Schema
-- PostgreSQL 15+
-- Created: 2025-10-13

-- ============================================================
-- DROP EXISTING TABLES (for clean setup)
-- ============================================================
DROP TABLE IF EXISTS admin_logs CASCADE;
DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS authorizations CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS device_services CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS admins CASCADE;

-- Drop custom types if they exist
DROP TYPE IF EXISTS service_type CASCADE;
DROP TYPE IF EXISTS order_status CASCADE;
DROP TYPE IF EXISTS log_direction CASCADE;
DROP TYPE IF EXISTS device_status CASCADE;

-- ============================================================
-- CUSTOM TYPES
-- ============================================================

-- Service/Product types
CREATE TYPE service_type AS ENUM ('TRIGGER', 'FIXED', 'VARIABLE');

-- Order status lifecycle
CREATE TYPE order_status AS ENUM ('CREATED', 'PAID', 'RUNNING', 'DONE', 'FAILED');

-- Log direction for telemetry
CREATE TYPE log_direction AS ENUM ('PI_TO_SRV', 'SRV_TO_PI');

-- Device operational status
CREATE TYPE device_status AS ENUM ('ACTIVE', 'OFFLINE', 'MAINTENANCE', 'DEACTIVATED');

-- ============================================================
-- ADMINS TABLE
-- ============================================================
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Index for faster email lookups
CREATE INDEX idx_admins_email ON admins(email);

-- ============================================================
-- DEVICES TABLE
-- ============================================================
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(255) NOT NULL,
    public_key TEXT NOT NULL,
    model VARCHAR(100),
    location VARCHAR(255),
    model_id UUID,
    location_id UUID,
    gpio_pin INTEGER,
    status device_status DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT label_not_empty CHECK (length(trim(label)) > 0),
    CONSTRAINT public_key_not_empty CHECK (length(trim(public_key)) > 0),
    CONSTRAINT gpio_pin_range CHECK (gpio_pin IS NULL OR (gpio_pin >= 0 AND gpio_pin <= 40))
);

-- Indexes for common queries
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_label ON devices(label);
CREATE INDEX idx_devices_created_at ON devices(created_at DESC);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DEVICE MODELS TABLE (Reference Data)
-- ============================================================
CREATE TABLE device_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT model_name_not_empty CHECK (length(trim(name)) > 0)
);

-- Index for common queries
CREATE INDEX idx_device_models_name ON device_models(name);

COMMENT ON TABLE device_models IS 'Reference table for device hardware models (e.g., RPi 4 Model B, RPi Zero 2 W)';

-- ============================================================
-- LOCATIONS TABLE (Reference Data)
-- ============================================================
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT location_name_not_empty CHECK (length(trim(name)) > 0)
);

-- Index for common queries
CREATE INDEX idx_locations_name ON locations(name);

COMMENT ON TABLE locations IS 'Reference table for device locations (e.g., Building 5 Floor 2, Main Lobby)';

-- ============================================================
-- SERVICE TYPES TABLE (Reference Data)
-- ============================================================
CREATE TABLE service_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    code service_type NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT service_type_name_not_empty CHECK (length(trim(name)) > 0)
);

-- Index for common queries
CREATE INDEX idx_service_types_code ON service_types(code);
CREATE INDEX idx_service_types_name ON service_types(name);

COMMENT ON TABLE service_types IS 'Reference table mapping user-friendly names to service type ENUMs (TRIGGER, FIXED, VARIABLE)';

-- Add foreign key constraints for devices table (after reference tables are created)
ALTER TABLE devices
    ADD CONSTRAINT fk_devices_model
    FOREIGN KEY (model_id) REFERENCES device_models(id) ON DELETE SET NULL;

ALTER TABLE devices
    ADD CONSTRAINT fk_devices_location
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL;

-- Indexes for foreign keys
CREATE INDEX idx_devices_model_id ON devices(model_id);
CREATE INDEX idx_devices_location_id ON devices(location_id);

-- ============================================================
-- SERVICES TABLE (Global services/products)
-- ============================================================
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type service_type NOT NULL,
    price_cents INTEGER NOT NULL,
    fixed_minutes INTEGER,
    minutes_per_25c INTEGER,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT price_positive CHECK (price_cents >= 0),
    CONSTRAINT fixed_minutes_positive CHECK (fixed_minutes IS NULL OR fixed_minutes > 0),
    CONSTRAINT minutes_per_25c_positive CHECK (minutes_per_25c IS NULL OR minutes_per_25c > 0),
    
    -- Type-specific validation
    CONSTRAINT trigger_validation CHECK (
        type != 'TRIGGER' OR (fixed_minutes IS NULL AND minutes_per_25c IS NULL)
    ),
    CONSTRAINT fixed_validation CHECK (
        type != 'FIXED' OR (fixed_minutes IS NOT NULL AND minutes_per_25c IS NULL)
    ),
    CONSTRAINT variable_validation CHECK (
        type != 'VARIABLE' OR (minutes_per_25c IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_services_active ON services(active);
CREATE INDEX idx_services_type ON services(type);

-- Trigger to auto-update updated_at
CREATE TRIGGER update_services_updated_at
    BEFORE UPDATE ON services
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DEVICE_SERVICES TABLE (Many-to-Many relationship)
-- ============================================================
CREATE TABLE device_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure a device can't have the same service assigned twice
    CONSTRAINT unique_device_service UNIQUE (device_id, service_id)
);

-- Indexes for junction table
CREATE INDEX idx_device_services_device_id ON device_services(device_id);
CREATE INDEX idx_device_services_service_id ON device_services(service_id);

-- ============================================================
-- ORDERS TABLE
-- ============================================================
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE RESTRICT,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    amount_cents INTEGER NOT NULL,
    authorized_minutes INTEGER NOT NULL,
    status order_status DEFAULT 'CREATED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT amount_positive CHECK (amount_cents >= 0),
    CONSTRAINT authorized_minutes_positive CHECK (authorized_minutes >= 0)
);

-- Indexes for common queries
CREATE INDEX idx_orders_device_id ON orders(device_id);
CREATE INDEX idx_orders_service_id ON orders(service_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_device_status ON orders(device_id, status);

-- Trigger to auto-update updated_at
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- AUTHORIZATIONS TABLE
-- ============================================================
CREATE TABLE authorizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    payload_json JSONB NOT NULL,
    signature_hex TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT signature_not_empty CHECK (length(trim(signature_hex)) > 0),
    CONSTRAINT expires_in_future CHECK (expires_at > created_at),
    
    -- Ensure one authorization per order
    CONSTRAINT unique_order_authorization UNIQUE (order_id)
);

-- Indexes
CREATE INDEX idx_authorizations_order_id ON authorizations(order_id);
CREATE INDEX idx_authorizations_device_id ON authorizations(device_id);
CREATE INDEX idx_authorizations_expires_at ON authorizations(expires_at);
CREATE INDEX idx_authorizations_payload_json ON authorizations USING GIN (payload_json);

-- ============================================================
-- LOGS TABLE (Telemetry and Communication Logs)
-- ============================================================
CREATE TABLE logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    direction log_direction NOT NULL,
    payload_hash VARCHAR(64),
    ok BOOLEAN DEFAULT true,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for analytics and debugging
CREATE INDEX idx_logs_device_id ON logs(device_id);
CREATE INDEX idx_logs_direction ON logs(direction);
CREATE INDEX idx_logs_ok ON logs(ok);
CREATE INDEX idx_logs_created_at ON logs(created_at DESC);
CREATE INDEX idx_logs_device_created ON logs(device_id, created_at DESC);

-- ============================================================
-- ADMIN LOGS TABLE (Admin Action Audit Trail)
-- ============================================================
CREATE TABLE admin_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID REFERENCES admins(id) ON DELETE SET NULL,
    admin_email VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for audit queries
CREATE INDEX idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX idx_admin_logs_action ON admin_logs(action);
CREATE INDEX idx_admin_logs_created_at ON admin_logs(created_at DESC);
CREATE INDEX idx_admin_logs_entity ON admin_logs(entity_type, entity_id);

-- ============================================================
-- VIEWS (for common queries)
-- ============================================================

-- Active devices with service counts
CREATE OR REPLACE VIEW v_devices_summary AS
SELECT 
    d.id,
    d.label,
    d.model,
    d.location,
    d.status,
    COUNT(DISTINCT ds.service_id) as service_count,
    COUNT(DISTINCT ds.service_id) FILTER (WHERE s.active = true) as active_service_count,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT o.id) FILTER (WHERE o.status = 'DONE') as completed_orders,
    d.created_at
FROM devices d
LEFT JOIN device_services ds ON d.id = ds.device_id
LEFT JOIN services s ON ds.service_id = s.id
LEFT JOIN orders o ON d.id = o.device_id
GROUP BY d.id, d.label, d.model, d.location, d.status, d.created_at;

-- Order details with device and service info
CREATE OR REPLACE VIEW v_orders_detailed AS
SELECT 
    o.id,
    o.status,
    o.amount_cents,
    o.authorized_minutes,
    o.created_at,
    o.updated_at,
    d.id as device_id,
    d.label as device_label,
    d.location as device_location,
    s.id as service_id,
    s.type as service_type,
    CASE 
        WHEN a.id IS NOT NULL THEN true
        ELSE false
    END as has_authorization
FROM orders o
JOIN devices d ON o.device_id = d.id
JOIN services s ON o.service_id = s.id
LEFT JOIN authorizations a ON o.id = a.order_id;

-- Recent logs with device info
CREATE OR REPLACE VIEW v_logs_recent AS
SELECT 
    l.id,
    l.direction,
    l.ok,
    l.details,
    l.created_at,
    d.label as device_label,
    d.location as device_location
FROM logs l
JOIN devices d ON l.device_id = d.id
ORDER BY l.created_at DESC
LIMIT 100;

-- ============================================================
-- FUNCTIONS (utility functions)
-- ============================================================

-- Function to get active services for a device
CREATE OR REPLACE FUNCTION get_device_services(device_uuid UUID)
RETURNS TABLE (
    id UUID,
    type service_type,
    price_cents INTEGER,
    fixed_minutes INTEGER,
    minutes_per_25c INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT s.id, s.type, s.price_cents, s.fixed_minutes, s.minutes_per_25c
    FROM services s
    JOIN device_services ds ON s.id = ds.service_id
    WHERE ds.device_id = device_uuid AND s.active = true;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate authorization minutes for variable pricing
CREATE OR REPLACE FUNCTION calculate_variable_minutes(
    service_uuid UUID,
    amount_paid_cents INTEGER
)
RETURNS INTEGER AS $$
DECLARE
    minutes_per_quarter INTEGER;
    quarters INTEGER;
BEGIN
    SELECT s.minutes_per_25c INTO minutes_per_quarter
    FROM services s
    WHERE s.id = service_uuid;
    
    IF minutes_per_quarter IS NULL THEN
        RAISE EXCEPTION 'Service not found or not VARIABLE type';
    END IF;
    
    quarters := amount_paid_cents / 25;
    RETURN quarters * minutes_per_quarter;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- PERMISSIONS (basic setup - adjust for your needs)
-- ============================================================

-- Create application user (optional)
-- DO $$
-- BEGIN
--     IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'remoteled_app') THEN
--         CREATE USER remoteled_app WITH PASSWORD 'change_me_in_production';
--     END IF;
-- END
-- $$;

-- Grant permissions (uncomment if using app user)
-- GRANT CONNECT ON DATABASE remoteled TO remoteled_app;
-- GRANT USAGE ON SCHEMA public TO remoteled_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO remoteled_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO remoteled_app;

-- ============================================================
-- COMMENTS (documentation)
-- ============================================================

COMMENT ON TABLE devices IS 'Raspberry Pi devices running RemoteLED';
COMMENT ON TABLE services IS 'Global services/products (TRIGGER, FIXED, VARIABLE)';
COMMENT ON TABLE device_services IS 'Many-to-many relationship between devices and services';
COMMENT ON TABLE orders IS 'Customer orders tracking payment and execution lifecycle';
COMMENT ON TABLE authorizations IS 'Cryptographically signed authorizations sent to devices';
COMMENT ON TABLE logs IS 'Telemetry and communication logs between Pi and server';
COMMENT ON TABLE admins IS 'Administrative users managing the system';

COMMENT ON COLUMN devices.public_key IS 'ECDSA public key for signature verification';
COMMENT ON COLUMN devices.gpio_pin IS 'GPIO pin number for relay/LED control';
COMMENT ON COLUMN services.type IS 'TRIGGER: one-time pulse, FIXED: fixed duration, VARIABLE: pay-per-time';
COMMENT ON COLUMN authorizations.payload_json IS 'Signed payload sent to device via BLE';
COMMENT ON COLUMN authorizations.signature_hex IS 'ECDSA signature in hexadecimal format';
COMMENT ON COLUMN logs.direction IS 'PI_TO_SRV: telemetry from device, SRV_TO_PI: commands to device';

-- ============================================================
-- COMPLETION MESSAGE
-- ============================================================

DO $$
BEGIN
    RAISE NOTICE '✓ RemoteLED database schema created successfully!';
    RAISE NOTICE '  - Tables: admins, devices, services, device_services, orders, authorizations, logs';
    RAISE NOTICE '  - Views: v_devices_summary, v_orders_detailed, v_logs_recent';
    RAISE NOTICE '  - Functions: get_device_services, calculate_variable_minutes';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Run seed.sql to populate with test data';
    RAISE NOTICE '  2. Update connection string in your application';
    RAISE NOTICE '  3. Review and adjust permissions for production';
END $$;

