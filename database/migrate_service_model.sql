-- Migration Script: Transform Service Model to Global Services with Many-to-Many
-- This script migrates from device-specific services to global services
-- Run this ONLY if you have an existing database with the old schema

-- ============================================================
-- STEP 1: Create the junction table
-- ============================================================
CREATE TABLE IF NOT EXISTS device_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_device_service UNIQUE (device_id, service_id)
);

-- ============================================================
-- STEP 2: Migrate existing service-device relationships
-- ============================================================
-- Copy existing device_id relationships to the junction table
INSERT INTO device_services (device_id, service_id, created_at)
SELECT device_id, id, created_at
FROM services
WHERE device_id IS NOT NULL
ON CONFLICT (device_id, service_id) DO NOTHING;

-- ============================================================
-- STEP 3: Rename product_id to service_id in orders table
-- ============================================================
ALTER TABLE orders RENAME COLUMN product_id TO service_id;

-- Drop old index
DROP INDEX IF EXISTS idx_orders_product_id;

-- Create new index
CREATE INDEX IF NOT EXISTS idx_orders_service_id ON orders(service_id);

-- ============================================================
-- STEP 4: Remove device_id from services table
-- ============================================================
-- Drop the foreign key constraint and index first
ALTER TABLE services DROP CONSTRAINT IF EXISTS services_device_id_fkey;
DROP INDEX IF EXISTS idx_services_device_id;

-- Remove the column
ALTER TABLE services DROP COLUMN IF EXISTS device_id;

-- ============================================================
-- STEP 5: Create indexes for junction table
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_device_services_device_id ON device_services(device_id);
CREATE INDEX IF NOT EXISTS idx_device_services_service_id ON device_services(service_id);

-- ============================================================
-- STEP 6: Update views
-- ============================================================

-- Drop and recreate v_devices_summary view
DROP VIEW IF EXISTS v_devices_summary;
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

-- Drop and recreate v_orders_detailed view
DROP VIEW IF EXISTS v_orders_detailed;
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

-- ============================================================
-- STEP 7: Update get_device_services function
-- ============================================================
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

-- ============================================================
-- STEP 8: Update table comments
-- ============================================================
COMMENT ON TABLE services IS 'Global services/products (TRIGGER, FIXED, VARIABLE)';
COMMENT ON TABLE device_services IS 'Many-to-many relationship between devices and services';

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
-- Run these to verify the migration was successful:

-- Check that all device-service relationships were migrated
-- SELECT COUNT(*) FROM device_services;

-- Verify orders table has service_id
-- SELECT column_name FROM information_schema.columns 
-- WHERE table_name = 'orders' AND column_name = 'service_id';

-- Verify services table no longer has device_id
-- SELECT column_name FROM information_schema.columns 
-- WHERE table_name = 'services' AND column_name = 'device_id';

-- Test that views work correctly
-- SELECT * FROM v_devices_summary LIMIT 5;
-- SELECT * FROM v_orders_detailed LIMIT 5;

-- ============================================================
-- COMPLETION MESSAGE
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✓ Service model migration completed successfully!';
    RAISE NOTICE '  - Created device_services junction table';
    RAISE NOTICE '  - Migrated existing device-service relationships';
    RAISE NOTICE '  - Renamed orders.product_id to orders.service_id';
    RAISE NOTICE '  - Removed services.device_id column';
    RAISE NOTICE '  - Updated all views and functions';
    RAISE NOTICE '';
    RAISE NOTICE 'Services are now global and can be assigned to multiple devices.';
END $$;

