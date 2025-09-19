-- Initialize databases for saga orchestrator and related services

-- Create saga database (already created by POSTGRES_DB env var)
-- CREATE DATABASE saga_db;

-- Create additional databases for other services if needed
CREATE DATABASE IF NOT EXISTS partners_db;
CREATE DATABASE IF NOT EXISTS alianzas_db;

-- Create saga user with appropriate permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'saga_user') THEN
        CREATE USER saga_user WITH PASSWORD 'saga_password';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE saga_db TO saga_user;
GRANT ALL PRIVILEGES ON DATABASE partners_db TO saga_user;
GRANT ALL PRIVILEGES ON DATABASE alianzas_db TO saga_user;

-- Connect to saga_db and create initial schema
\c saga_db;

-- Create saga_states table if it doesn't exist
CREATE TABLE IF NOT EXISTS saga_states (
    saga_id VARCHAR(255) PRIMARY KEY,
    correlation_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    current_step VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    partner_data JSONB,
    partner_id VARCHAR(255),
    alliance_id VARCHAR(255),
    error TEXT,
    compensation_actions JSONB DEFAULT '[]'::jsonb,
    steps JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_saga_states_status ON saga_states(status);
CREATE INDEX IF NOT EXISTS idx_saga_states_correlation_id ON saga_states(correlation_id);
CREATE INDEX IF NOT EXISTS idx_saga_states_created_at ON saga_states(created_at);
CREATE INDEX IF NOT EXISTS idx_saga_states_partner_id ON saga_states(partner_id);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_saga_states_updated_at ON saga_states;
CREATE TRIGGER update_saga_states_updated_at
    BEFORE UPDATE ON saga_states
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing (optional)
-- INSERT INTO saga_states (saga_id, status, partner_data) 
-- VALUES ('test-saga-1', 'completed', '{"nombre": "Test Partner", "email": "test@example.com"}')
-- ON CONFLICT (saga_id) DO NOTHING;
