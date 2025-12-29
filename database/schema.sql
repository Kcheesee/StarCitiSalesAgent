-- StarCitiSalesAgent Database Schema
-- PostgreSQL 15+
-- Created: 2025-12-27

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SHIPS & VEHICLES DATA
-- ============================================================================

-- Manufacturers Table
CREATE TABLE manufacturers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_manufacturers_code ON manufacturers(code);

-- Ships Main Table
CREATE TABLE ships (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    class_name VARCHAR(255),

    -- Manufacturer
    manufacturer_id INTEGER REFERENCES manufacturers(id),
    manufacturer_name VARCHAR(255), -- Denormalized for quick access

    -- Classification
    focus VARCHAR(255), -- e.g., "Light Fighter", "Heavy Cargo", "Exploration"
    type VARCHAR(100), -- e.g., "combat", "industrial", "exploration"

    -- Dimensions (meters)
    length DECIMAL(10,2),
    beam DECIMAL(10,2),
    height DECIMAL(10,2),
    mass INTEGER, -- kg

    -- Capacity
    cargo_capacity INTEGER DEFAULT 0, -- SCU
    vehicle_inventory DECIMAL(10,2), -- SCU
    personal_inventory DECIMAL(10,2), -- SCU

    -- Crew
    crew_min INTEGER,
    crew_max INTEGER,
    crew_weapon INTEGER,
    crew_operation INTEGER,

    -- Health & Shields
    health INTEGER,
    shield_hp INTEGER,
    shield_face_type VARCHAR(50), -- "Bubble" or "Quadrant"

    -- Speed (m/s)
    speed_scm INTEGER,
    speed_max INTEGER,
    speed_zero_to_scm DECIMAL(10,2), -- seconds
    speed_zero_to_max DECIMAL(10,2), -- seconds

    -- Agility (deg/s)
    agility_pitch DECIMAL(10,2),
    agility_yaw DECIMAL(10,2),
    agility_roll DECIMAL(10,2),

    -- Acceleration (m/s²)
    accel_main DECIMAL(10,2),
    accel_retro DECIMAL(10,2),
    accel_vtol DECIMAL(10,2),
    accel_maneuvering DECIMAL(10,2),

    -- Fuel
    fuel_capacity DECIMAL(10,2), -- liters
    fuel_intake_rate DECIMAL(10,2), -- L/s
    fuel_usage_main DECIMAL(10,2),
    fuel_usage_maneuvering DECIMAL(10,2),

    -- Quantum Drive
    quantum_speed BIGINT, -- m/s
    quantum_spool_time DECIMAL(10,2), -- seconds
    quantum_fuel_capacity DECIMAL(10,2),
    quantum_range BIGINT, -- meters

    -- Emissions
    emission_ir INTEGER,
    emission_em_idle INTEGER,
    emission_em_max INTEGER,

    -- Descriptions (English only for MVP)
    description TEXT,
    description_de TEXT, -- German
    description_cn TEXT, -- Chinese

    -- External Data (to be scraped)
    marketing_description TEXT,
    price_usd DECIMAL(10,2),
    price_auec INTEGER,
    store_url VARCHAR(500),
    image_url VARCHAR(500),
    image_local_path VARCHAR(500),

    -- Metadata
    raw_data JSONB, -- Store complete API response
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_ships_manufacturer ON ships(manufacturer_id);
CREATE INDEX idx_ships_focus ON ships(focus);
CREATE INDEX idx_ships_type ON ships(type);
CREATE INDEX idx_ships_cargo ON ships(cargo_capacity);
CREATE INDEX idx_ships_price_usd ON ships(price_usd);
CREATE INDEX idx_ships_crew_min ON ships(crew_min);
CREATE INDEX idx_ships_slug ON ships(slug);

-- ============================================================================
-- SHIP COMPONENTS & HARDPOINTS
-- ============================================================================

-- Ship Hardpoints (weapon mounts)
CREATE TABLE ship_hardpoints (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE,

    hardpoint_name VARCHAR(255),
    size INTEGER, -- S1, S2, S3, etc.
    type VARCHAR(100), -- "Weapon", "Turret", "Missile", "Utility"
    category VARCHAR(100), -- "Fixed", "Gimbaled", "Manned Turret"
    quantity INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hardpoints_ship ON ship_hardpoints(ship_id);

-- Ship Components (shields, engines, etc.)
CREATE TABLE ship_components (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE,

    component_type VARCHAR(100), -- "Shield", "Power Plant", "Cooler", "Quantum Drive"
    component_name VARCHAR(255),
    size INTEGER,
    manufacturer VARCHAR(255),
    quantity INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_components_ship ON ship_components(ship_id);

-- Ship Vehicle Bays (for ships that can carry other vehicles)
CREATE TABLE ship_vehicle_bays (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE,

    bay_type VARCHAR(100), -- "Vehicle", "Snub Fighter", "Docking Collar"
    capacity INTEGER, -- How many vehicles
    max_size VARCHAR(50), -- "Small", "Medium", "Large"

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vehicle_bays_ship ON ship_vehicle_bays(ship_id);

-- ============================================================================
-- RAG / EMBEDDINGS FOR AI SEARCH
-- ============================================================================

-- Ship Embeddings for semantic search
-- Note: Using JSONB for MVP. Can migrate to pgvector later for better performance
CREATE TABLE ship_embeddings (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE UNIQUE,

    -- Searchable text (concatenated for embedding)
    search_text TEXT NOT NULL,

    -- Embedding vector (OpenAI: 1536 dimensions)
    -- Using JSONB array for MVP, will migrate to vector type with pgvector extension
    embedding JSONB,

    -- Metadata
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings_ship ON ship_embeddings(ship_id);
-- For pgvector later: CREATE INDEX ON ship_embeddings USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- CONVERSATIONS & USER SESSIONS
-- ============================================================================

-- Conversations Table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    conversation_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,

    -- User Info (anonymous, optional)
    user_email VARCHAR(255),
    user_budget_usd INTEGER,
    user_playstyle VARCHAR(100), -- "Solo", "Crew", "Mixed"
    user_preferences JSONB, -- Flexible JSON storage for various preferences

    -- Conversation State
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'abandoned'
    transcript JSONB, -- Array of {role: "user"|"assistant", content: "...", timestamp: "..."}

    -- AI Recommendations
    recommended_ships JSONB, -- Array of {ship_id, ship_name, reasoning}

    -- Generated Documents
    transcript_pdf_path VARCHAR(500),
    fleet_guide_pdf_path VARCHAR(500),

    -- Email Delivery
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP,

    -- Timestamps
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_email ON conversations(user_email);
CREATE INDEX idx_conversations_started ON conversations(started_at);

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View for ships with manufacturer info
CREATE VIEW v_ships_full AS
SELECT
    s.*,
    m.name as manufacturer_full_name,
    m.code as manufacturer_code
FROM ships s
LEFT JOIN manufacturers m ON s.manufacturer_id = m.id;

-- View for ship recommendations (most commonly queried data)
CREATE VIEW v_ships_for_recommendation AS
SELECT
    s.id,
    s.slug,
    s.name,
    s.manufacturer_name,
    s.focus,
    s.type,
    s.cargo_capacity,
    s.crew_min,
    s.crew_max,
    s.length,
    s.price_usd,
    s.price_auec,
    s.description,
    s.image_local_path,
    s.speed_scm,
    s.speed_max
FROM ships s
WHERE s.description IS NOT NULL
ORDER BY s.name;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to ships table
CREATE TRIGGER update_ships_updated_at BEFORE UPDATE ON ships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to embeddings table
CREATE TRIGGER update_embeddings_updated_at BEFORE UPDATE ON ship_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Insert common manufacturers (will be expanded during ETL)
INSERT INTO manufacturers (name, code, description) VALUES
('Aegis Dynamics', 'AEGS', 'Manufacturer of military-grade spacecraft'),
('Anvil Aerospace', 'ANVL', 'Renowned for durable and reliable ships'),
('Origin Jumpworks', 'ORIG', 'Luxury spacecraft manufacturer'),
('MISC', 'MISC', 'Musashi Industrial and Starflight Concern'),
('Roberts Space Industries', 'RSI', 'Iconic manufacturer of versatile spacecraft'),
('Drake Interplanetary', 'DRAK', 'Affordable, no-frills spacecraft'),
('Crusader Industries', 'CRUS', 'Large-scale industrial spacecraft'),
('Argo Astronautics', 'ARGO', 'Utility and industrial vehicles'),
('Consolidated Outland', 'CNOU', 'Starter ships and utility craft'),
('Esperia', 'ESPR', 'Replica alien spacecraft')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE ships IS 'Main ships and vehicles table with complete specifications';
COMMENT ON TABLE ship_embeddings IS 'Vector embeddings for semantic ship search (RAG system)';
COMMENT ON TABLE conversations IS 'User conversation sessions with AI consultant';
COMMENT ON COLUMN ships.raw_data IS 'Complete API response stored as JSONB for reference';
COMMENT ON COLUMN conversations.transcript IS 'Full conversation history in JSONB format';

-- ============================================================================
-- SCHEMA COMPLETE
-- ============================================================================

-- Show table summary
SELECT
    schemaname,
    tablename,
    CAST(pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS VARCHAR) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
