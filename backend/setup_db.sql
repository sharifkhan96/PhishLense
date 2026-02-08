-- PostgreSQL Database Setup Script for PhishLense
-- Run this with: sudo -u postgres psql < setup_db.sql
-- Or copy-paste these commands into psql

-- Create database
CREATE DATABASE phishlense;

-- Create user (change password as needed)
CREATE USER phishlense_user WITH PASSWORD 'phishlense_pass123';

-- Set encoding and timezone
ALTER ROLE phishlense_user SET client_encoding TO 'utf8';
ALTER ROLE phishlense_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE phishlense_user SET timezone TO 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE phishlense TO phishlense_user;

-- Connect to the new database and grant schema privileges
\c phishlense
GRANT ALL ON SCHEMA public TO phishlense_user;

-- Exit
\q


