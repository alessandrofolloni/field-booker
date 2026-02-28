-- ========================================
-- Field Booker — Database Initialization
-- ========================================

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Spatial index for fast ST_DWithin geospatial queries on fields table.
-- This runs after table creation via SQLAlchemy, so we use a DO block
-- to create it only if the table exists (avoids errors on first startup).
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'fields'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_fields_location ON fields USING GIST(location);
    END IF;
END
$$;
