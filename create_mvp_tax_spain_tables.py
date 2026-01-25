"""
Standalone script to create MVP Tax Spain tables on Railway.
Bypasses Alembic to avoid revision chain issues.
"""
import asyncio
from sqlalchemy import text
from backend.database import get_async_engine

async def create_mvp_tax_spain_tables():
    """Create all MVP Tax Spain tables and columns directly with SQL."""
    engine = get_async_engine()

    async with engine.begin() as conn:
        print("🔄 Creating MVP Tax Spain tables and columns...")

        # Step 1: Add profile columns to users table if they don't exist
        await conn.execute(text("""
            DO $$
            BEGIN
                -- Add vorname column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name='users' AND column_name='vorname') THEN
                    ALTER TABLE users ADD COLUMN vorname VARCHAR(100);
                    RAISE NOTICE 'Added vorname column';
                END IF;

                -- Add nachname column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name='users' AND column_name='nachname') THEN
                    ALTER TABLE users ADD COLUMN nachname VARCHAR(100);
                    RAISE NOTICE 'Added nachname column';
                END IF;

                -- Add sprache column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name='users' AND column_name='sprache') THEN
                    ALTER TABLE users ADD COLUMN sprache VARCHAR(5) DEFAULT 'de' NOT NULL;
                    RAISE NOTICE 'Added sprache column';
                END IF;

                -- Add telefonnummer column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name='users' AND column_name='telefonnummer') THEN
                    ALTER TABLE users ADD COLUMN telefonnummer VARCHAR(50);
                    RAISE NOTICE 'Added telefonnummer column';
                END IF;
            END$$;
        """))

        # Step 2: Create h7_form_data table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS h7_form_data (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES users(id) ON DELETE SET NULL,
                email VARCHAR(255) NOT NULL,
                sendungsart VARCHAR(255),
                warenwert_gesamt VARCHAR(50),
                waehrung VARCHAR(10),
                versandkosten VARCHAR(50),
                gesamtbetrag_zoll VARCHAR(50),
                art_lieferung VARCHAR(255),
                absender_name VARCHAR(255),
                absender_strasse VARCHAR(255),
                absender_plz VARCHAR(50),
                absender_ort VARCHAR(255),
                absender_land VARCHAR(255),
                absender_email VARCHAR(255),
                absender_telefon VARCHAR(50),
                empfaenger_name VARCHAR(255),
                empfaenger_strasse VARCHAR(255),
                empfaenger_plz VARCHAR(50),
                empfaenger_ort VARCHAR(255),
                empfaenger_insel VARCHAR(255),
                empfaenger_nif VARCHAR(50),
                empfaenger_email VARCHAR(255),
                empfaenger_telefon VARCHAR(50),
                warenpositionen JSONB,
                exported_pdf_url VARCHAR(500),
                wahrheitserklaerung VARCHAR(10),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
        """))

        # Create indices
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_h7_form_data_user_id ON h7_form_data(user_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_h7_form_data_email ON h7_form_data(email);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_h7_form_data_created_at ON h7_form_data(created_at);
        """))

        # Step 3: Create admin_settings table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                email_sender VARCHAR(255) NOT NULL DEFAULT 'michael.dabrock@gmx.es',
                resend_api_key VARCHAR(500),
                email_verification_required VARCHAR(10) DEFAULT 'Ja',
                auto_logout_minutes INTEGER DEFAULT 30,
                CONSTRAINT admin_settings_singleton CHECK (id = 1)
            );
        """))

        # Insert default settings
        await conn.execute(text("""
            INSERT INTO admin_settings (id, email_sender, resend_api_key, email_verification_required, auto_logout_minutes)
            VALUES (1, 'michael.dabrock@gmx.es', 're_hTZxVL5t_9CcWhbdQLNzCC6aJkd6bd1FW', 'Ja', 30)
            ON CONFLICT (id) DO NOTHING;
        """))

        # Step 4: Create password_reset_tokens table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) NOT NULL UNIQUE,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                used VARCHAR(10) DEFAULT 'Nein' NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
        """))

        # Create indices
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_id ON password_reset_tokens(user_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_token ON password_reset_tokens(token);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);
        """))

        print("✅ MVP Tax Spain tables and columns created successfully!")

if __name__ == "__main__":
    asyncio.run(create_mvp_tax_spain_tables())
