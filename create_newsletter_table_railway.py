#!/usr/bin/env python3
"""
Create bar_newsletter table on Railway database
"""
import psycopg2

# Railway database connection
DB_HOST = "roundhouse.proxy.rlwy.net"
DB_PORT = 35555
DB_NAME = "railway"
DB_USER = "postgres"
DB_PASSWORD = "QMsZIHABICYpgVtQSIxJgJHoGtptYlFZ"

def create_newsletter_table():
    """Create bar_newsletter table"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        print("🔧 Creating bar_newsletter table...")

        # Create table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bar_newsletter (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255),
                language VARCHAR(5) DEFAULT 'ca',
                is_active BOOLEAN DEFAULT TRUE,
                subscribed_at TIMESTAMP DEFAULT NOW(),
                unsubscribed_at TIMESTAMP
            );
        """)
        print("   ✅ bar_newsletter table created")

        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_bar_newsletter_email ON bar_newsletter(email);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_bar_newsletter_active ON bar_newsletter(is_active);
        """)
        print("   ✅ Indexes created")

        conn.commit()

        # Verify table exists
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name = 'bar_newsletter';
        """)
        result = cur.fetchone()

        if result:
            print(f"\n✅ Newsletter table verified: {result[0]}")
        else:
            print("\n⚠️  Table not found after creation")

        cur.close()
        conn.close()

        print("\n🎉 Newsletter table ready!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_newsletter_table()
    exit(0 if success else 1)
