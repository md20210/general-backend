-- Create bar_newsletter table if it doesn't exist

CREATE TABLE IF NOT EXISTS bar_newsletter (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    language VARCHAR(5) DEFAULT 'ca',
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP DEFAULT NOW(),
    unsubscribed_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_bar_newsletter_email ON bar_newsletter(email);
CREATE INDEX IF NOT EXISTS idx_bar_newsletter_active ON bar_newsletter(is_active);

SELECT 'bar_newsletter table created successfully!' AS status;
