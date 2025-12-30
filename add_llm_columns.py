#!/usr/bin/env python3
"""
Add LLM analysis columns to elastic_job_analyses table.
Run this once to add the missing columns.
"""
import asyncio
import sys
from sqlalchemy import text
from backend.database import engine

async def add_columns():
    """Add LLM analysis columns to the database."""
    print("🔧 Adding LLM analysis columns to elastic_job_analyses...")

    sql = """
    DO $$
    BEGIN
        -- Add job_analysis column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'elastic_job_analyses'
            AND column_name = 'job_analysis'
        ) THEN
            ALTER TABLE elastic_job_analyses
            ADD COLUMN job_analysis JSONB NOT NULL DEFAULT '{}';
            RAISE NOTICE 'Added column: job_analysis';
        ELSE
            RAISE NOTICE 'Column job_analysis already exists';
        END IF;

        -- Add fit_score column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'elastic_job_analyses'
            AND column_name = 'fit_score'
        ) THEN
            ALTER TABLE elastic_job_analyses
            ADD COLUMN fit_score JSONB NOT NULL DEFAULT '{}';
            RAISE NOTICE 'Added column: fit_score';
        ELSE
            RAISE NOTICE 'Column fit_score already exists';
        END IF;

        -- Add success_probability column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'elastic_job_analyses'
            AND column_name = 'success_probability'
        ) THEN
            ALTER TABLE elastic_job_analyses
            ADD COLUMN success_probability JSONB NOT NULL DEFAULT '{}';
            RAISE NOTICE 'Added column: success_probability';
        ELSE
            RAISE NOTICE 'Column success_probability already exists';
        END IF;
    END $$;
    """

    async with engine.begin() as conn:
        await conn.execute(text(sql))
        print("✅ Columns added successfully!")

    # Verify columns exist
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'elastic_job_analyses'
            AND column_name IN ('job_analysis', 'fit_score', 'success_probability')
            ORDER BY column_name;
        """))
        columns = [row[0] for row in result]

        print(f"\n✅ Verification:")
        for col in ['job_analysis', 'fit_score', 'success_probability']:
            if col in columns:
                print(f"   ✅ {col} exists")
            else:
                print(f"   ❌ {col} missing")

        if len(columns) == 3:
            print("\n🎉 All columns successfully added!")
            return 0
        else:
            print(f"\n❌ Error: Only {len(columns)}/3 columns were added")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(add_columns())
    sys.exit(exit_code)
