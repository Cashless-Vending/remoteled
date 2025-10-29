-- Migration to add authentication fields to admins table
-- Run this on existing databases

-- Add password_hash and last_login columns
ALTER TABLE admins 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- For existing admins without password, you'll need to manually set passwords
-- Example: UPDATE admins SET password_hash = '$2b$12$...' WHERE email = 'admin@example.com';

-- Make password_hash required for new entries (existing rows may have NULL temporarily)
-- ALTER TABLE admins ALTER COLUMN password_hash SET NOT NULL;

COMMENT ON COLUMN admins.password_hash IS 'Bcrypt hashed password for authentication';
COMMENT ON COLUMN admins.last_login IS 'Timestamp of last successful login';

