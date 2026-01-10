#!/bin/bash

# Reset Alembic version table and create Bar tables directly via SQL

echo "🔄 Resetting Alembic and creating Bar tables..."

# Execute SQL commands via Railway
railway run --service generalbackend bash -c '
# Delete alembic version entries that might cause conflicts
psql $DATABASE_URL -c "DELETE FROM alembic_version WHERE version_num LIKE '\''20260110%'\'';"

# Create all Bar tables if they don'\''t exist
psql $DATABASE_URL << EOF
-- 1. bar_info
CREATE TABLE IF NOT EXISTS bar_info (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    google_maps_url TEXT,
    description JSON,
    price_range VARCHAR(50),
    rating VARCHAR(10),
    opening_hours JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. bar_newsletter
CREATE TABLE IF NOT EXISTS bar_newsletter (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    language VARCHAR(5) DEFAULT '\''ca'\'',
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP DEFAULT NOW(),
    unsubscribed_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_bar_newsletter_email ON bar_newsletter(email);
CREATE INDEX IF NOT EXISTS idx_bar_newsletter_active ON bar_newsletter(is_active);

-- Insert bar info if not exists
INSERT INTO bar_info (name, phone, address, city, postal_code, latitude, longitude, google_maps_url, price_range, rating)
SELECT '\''Bar Ca l'\''Elena'\'', '\''+34 933 36 50 43'\'', '\''Carrer d'\''Amadeu Torner, 20'\'', '\''L'\''Hospitalet de Llobregat'\'', '\''08902'\'', 41.361305556, 2.116388889, '\''https://maps.app.goo.gl/gXUiS3RRQ4FV52HS7'\'', '\''€-€€'\'', '\''4.0/5'\''
WHERE NOT EXISTS (SELECT 1 FROM bar_info WHERE id = 1);

-- Mark migration as applied
INSERT INTO alembic_version (version_num) VALUES ('\''20260110_bar_complete'\'')
ON CONFLICT (version_num) DO NOTHING;

EOF

echo "✅ Done!"
'
