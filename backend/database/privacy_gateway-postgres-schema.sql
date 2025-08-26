-- privacy-gateway-postgres-schema.sql
-- Privacy Gateway schema for PostgreSQL
-- Provides role-aware, privacy-preserving access to sensitive patient data.
-- Doctors see full raw records, researchers get pseudonymized datasets,
-- developers get fake but realistic test data, and all access is logged.

BEGIN;

-- 1) Enable pgcrypto extension
-- Why: Provides cryptographic primitives needed for security:
--   - gen_random_uuid() to generate secure UUIDs
--   - gen_random_bytes() for keys
--   - hmac() for deterministic pseudonymization
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2) Create a dedicated schema
-- Why: Keeps all privacy-related tables, functions, and views isolated
-- in their own namespace (privacy_gateway), avoiding clutter and conflicts
CREATE SCHEMA IF NOT EXISTS privacy_gateway;

-- 3) Application role catalogue
-- Why: Defines high-level application roles (admin, clinician, researcher, developer).
-- These are not database roles, but conceptual roles that map to data access needs.
-- This makes it possible to enforce role-aware data transformations.
CREATE TABLE IF NOT EXISTS privacy_gateway.roles (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT
);

-- 4) Users / actors table
-- Why: Stores application-level user accounts, linked to their role and identity.
-- Each user has a UUID ID, unique username, email, optional full_name, and
-- OIDC subject identifier for federated login. The role_id links to roles above.
-- This provides the basis for access auditing and privacy enforcement per actor.
CREATE TABLE IF NOT EXISTS privacy_gateway.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT NOT NULL UNIQUE,
  full_name TEXT,
  email TEXT UNIQUE,
  role_id INT NOT NULL REFERENCES privacy_gateway.roles(id),
  oidc_sub TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5) Patients table (raw, sensitive data)
-- Why: The "goldmine" of sensitive healthcare data, containing both identifiers
-- (name, phone, email, address) and clinical/financial attributes (age, disease,
-- purchase_amount, etc). This table is highly protected and only accessible to
-- clinicians and admins who need the full original record.
CREATE TABLE IF NOT EXISTS privacy_gateway.patients (
  id SERIAL PRIMARY KEY,
  patient_uuid UUID NOT NULL DEFAULT gen_random_uuid(),
  name TEXT,
  phone TEXT,
  email TEXT,
  address TEXT,
  date_of_birth DATE,
  age INT,
  disease TEXT,
  purchase_amount NUMERIC(12,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6) Pseudonym keys table
-- Why: Stores pseudonymization keys (demo only). In production, these keys
-- must be stored in a secure KMS/HSM and only referenced here by label.
-- Researchers require consistent pseudonyms (same patient → same fake ID)
-- to support longitudinal studies without exposing identities.
CREATE TABLE IF NOT EXISTS privacy_gateway.pseudonym_keys (
  id SERIAL PRIMARY KEY,
  key_label TEXT NOT NULL UNIQUE,
  key_hex TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7) Audit logs
-- Why: GDPR and HIPAA require hospitals to log every access to patient data.
-- This immutable, append-only log records:
--   - who accessed (actor_id, actor_role)
--   - what they did (action, e.g., VIEW_PATIENT)
--   - which patient was involved
--   - the outcome and optional metadata
-- This provides accountability and legal compliance.
CREATE TABLE IF NOT EXISTS privacy_gateway.audit_logs (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor_id UUID,
  actor_role TEXT,
  action TEXT NOT NULL,
  patient_id INT,
  outcome TEXT,
  meta JSONB
);

-- 8) Indexes for audit logs
-- Why: Efficiently supports common compliance queries such as:
--   - "Show me all accesses for patient X"
--   - "Show me all actions by user Y"
CREATE INDEX IF NOT EXISTS idx_audit_patient ON privacy_gateway.audit_logs (patient_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON privacy_gateway.audit_logs (actor_id);

-- 9) Deterministic pseudonymization function
-- Why: Researchers need to study patterns across patients without knowing identities.
-- This function:
--   - Takes a patient_id + key_label
--   - Uses HMAC-SHA256 with the key from pseudonym_keys
--   - Returns a pseudonym like "anon-abcd1234"
-- Uses a stored key from pseudonym_keys (hex-encoded). Returns "anon-<hex-prefix>"
-- Deterministic → the same patient always maps to the same pseudonym,
-- allowing consistent analysis over time.

CREATE OR REPLACE FUNCTION privacy_gateway.pseudonymize_with_key_label(
  p_patient_id INT,
  p_key_label TEXT,
  p_len INT DEFAULT 16
) RETURNS TEXT LANGUAGE SQL STABLE AS $$
  SELECT (
    'anon-' || 
    substr(
      encode(
        hmac(convert_to(p_patient_id::text, 'UTF8'), decode(pk.key_hex, 'hex'), 'sha256'),
        'hex'
      ), 
      1, p_len
    )
  )
  FROM privacy_gateway.pseudonym_keys pk 
  WHERE pk.key_label = p_key_label;
$$;


-- 10) Developer view
-- Why: Developers need realistic-looking data for testing hospital systems,
-- but must never see real patient identities. This view:
--   - Replaces name, phone, email, address with synthetic fakes
--   - Preserves clinical/financial values (age, disease, purchase_amount)
-- Example: lets developers test "billing works for ₹500" without exposing Ravi Kumar’s identity.
CREATE OR REPLACE VIEW privacy_gateway.v_patients_developer AS
SELECT
  id,
  ('TestUser-' || id::TEXT) AS name,
  ('+91-9' || lpad(id::TEXT, 8, '0')) AS phone,
  ('user' || id::TEXT || '@example.com') AS email,
  ('Fake Address, Bangalore') AS address,
  age, disease, purchase_amount, created_at
FROM privacy_gateway.patients;

-- 11) Researcher view
-- Why: Researchers don’t need identity, just statistically accurate datasets.
-- This view:
--   - Replaces patient_id with a pseudonym
--   - Extracts only city/location from address
--   - Keeps age, disease, purchase_amount intact
-- Example: lets researchers ask "Is diabetes more common in Delhi?"
-- without knowing who the patients are.
CREATE OR REPLACE VIEW privacy_gateway.v_patients_researcher AS
SELECT
  privacy_gateway.pseudonymize_with_key_label(p.id, 'demo-key') AS patient_id,
  regexp_replace(p.address, '.*,\s*', '') AS location,
  p.age,
  p.disease,
  p.purchase_amount
FROM privacy_gateway.patients p;

-- 12) Seed roles (idempotent)
-- Why: Pre-populates the app-level roles needed by the gateway.
-- Admin → full system privileges
-- Clinician → full patient data
-- Researcher → pseudonymized data
-- Developer → synthetic data
INSERT INTO privacy_gateway.roles (name, description)
VALUES
  ('admin', 'System administrators'),
  ('clinician', 'Medical staff with full access'),
  ('researcher', 'Researchers with de-identified access'),
  ('developer', 'Developers with synthetic identity access')
ON CONFLICT (name) DO NOTHING;

-- 13) Seed a demo pseudonym key
-- Why: Provides a sample key so the pseudonymization function works out-of-the-box.
-- In production, keys should be injected from a secure Key Management System.
INSERT INTO privacy_gateway.pseudonym_keys (key_label, key_hex)
VALUES ('demo-key', encode(gen_random_bytes(32),'hex'))
ON CONFLICT (key_label) DO NOTHING;

COMMIT;

-- End of file
-- Usage: run with `psql -d yourdb -f privacy-gateway-postgres-schema.sql`
-- Notes:
--   - In production, manage pseudonymization keys via KMS
--   - Handle database-level role GRANTs separately in infra code
--   - This schema enforces "privacy-as-a-service" at the data layer
