-- Create a fresh database for PhishLense
-- Run with: sudo -u postgres psql < create_phishlense_db.sql
-- Or: psql -U postgres -f create_phishlense_db.sql

-- Create database
CREATE DATABASE phishlense_db;

-- Create user (if doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'phishlense_user') THEN
        CREATE USER phishlense_user WITH PASSWORD 'phishlense_pass123';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE phishlense_db TO phishlense_user;

-- Connect to the new database
\c phishlense_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO phishlense_user;


