-- Fix migration state: Clear django_migrations table and let Django recreate it
-- Run this in psql: psql -U zics -d zics_db -f fix_migrations.sql

-- Clear migration records (this won't delete tables, just migration tracking)
TRUNCATE TABLE django_migrations;

-- If the table doesn't exist, create it
CREATE TABLE IF NOT EXISTS django_migrations (
    id bigserial NOT NULL PRIMARY KEY,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


