-- =============================================================================
-- QueryMind AI — PostgreSQL Least-Privilege Application Role Setup Script
-- =============================================================================
--
-- PURPOSE:
-- Creates a dedicated, restricted application database role ('querymind_app')
-- granting strictly read-only SELECT permissions on approved QueryMind tables:
--   - students
--   - courses
--   - enrollments
--
-- SECURITY GUARANTEES:
-- 1. Non-Superuser: Role cannot alter schemas, create tables, or manage the database.
-- 2. Read-Only Scope: Granted SELECT only; all mutations (INSERT, UPDATE, DELETE,
--    TRUNCATE, REFERENCES, TRIGGER) are strictly revoked.
-- 3. Read-Only Transaction Mode: Configures 'default_transaction_read_only = on'
--    as a user-level configuration parameter in PostgreSQL.
-- 4. Defense-in-Depth: Enforces database-level access control as the final boundary
--    behind application SQLGlot AST query validation.
--
-- INSTRUCTIONS FOR DATABASE ADMINISTRATOR:
-- 1. Connect to PostgreSQL as an administrator (superuser or database owner).
-- 2. Replace 'REPLACE_WITH_A_STRONG_PASSWORD' below with a secure secret
--    from your secrets manager or environment configuration.
-- 3. Execute this script against target database 'querymind_db':
--      psql -U postgres -d querymind_db -f setup_restricted_role.sql
-- 4. Configure the application environment with this role:
--      DATABASE_URL=postgresql+psycopg://querymind_app:YOUR_PASSWORD@localhost:5432/querymind_db
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;

-- 1. Create dedicated application role if it does not already exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'querymind_app') THEN
        CREATE ROLE querymind_app WITH
            LOGIN
            PASSWORD 'REPLACE_WITH_A_STRONG_PASSWORD'
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOINHERIT;
        RAISE NOTICE 'Role querymind_app created successfully.';
    ELSE
        RAISE NOTICE 'Role querymind_app already exists; updating permissions.';
    END IF;
END
$$;

-- 2. Ensure schema usage is permitted but object creation is denied
GRANT USAGE ON SCHEMA public TO querymind_app;
REVOKE CREATE ON SCHEMA public FROM querymind_app;

-- 3. Grant SELECT strictly on approved QueryMind academic schema tables
GRANT SELECT ON TABLE students TO querymind_app;
GRANT SELECT ON TABLE courses TO querymind_app;
GRANT SELECT ON TABLE enrollments TO querymind_app;

-- 4. Explicitly revoke any mutation privileges
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON TABLE students FROM querymind_app;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON TABLE courses FROM querymind_app;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON TABLE enrollments FROM querymind_app;

-- 5. Revoke access to PostgreSQL sequence mutation functions
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM querymind_app;

-- 6. Enforce read-only transactions at the database session level
ALTER ROLE querymind_app SET default_transaction_read_only = on;

COMMIT;

-- =============================================================================
-- Verification queries (Run as querymind_app to confirm):
--   SELECT COUNT(*) FROM students;              -- SUCCESS
--   INSERT INTO students (name) VALUES ('bad'); -- PERMISSION DENIED ERROR
-- =============================================================================
