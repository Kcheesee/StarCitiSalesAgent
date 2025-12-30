#!/usr/bin/env python3
"""
Database Migration: Add user_name column to conversations table
Run this on production to add the missing column
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    """Add user_name column to conversations table if it doesn't exist"""

    print("=" * 80)
    print("DATABASE MIGRATION: Add user_name column")
    print("=" * 80)
    print()

    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'conversations'
                AND column_name = 'user_name'
            """))

            if result.fetchone():
                print("✅ Column 'user_name' already exists - no migration needed")
                return

            # Add the column
            print("📝 Adding user_name column to conversations table...")
            conn.execute(text("""
                ALTER TABLE conversations
                ADD COLUMN user_name VARCHAR(200)
            """))
            conn.commit()

            print("✅ Migration successful!")
            print()
            print("Changes made:")
            print("  - Added column: user_name VARCHAR(200)")
            print()

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ MIGRATION FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()

        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate()
