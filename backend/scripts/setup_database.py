#!/usr/bin/env python3
"""
One-time database setup script for Render deployment
Creates tables and loads initial data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal, Base
# Import all models so they register with Base
from app.models import Ship, Manufacturer, ShipEmbedding, ShipHardpoint, ShipComponent, ShipVehicleBay, Conversation
import subprocess


def create_tables():
    """Create all database tables"""
    print("=" * 80)
    print("STEP 1: Creating Database Tables")
    print("=" * 80)

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")

        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def fetch_ship_data():
    """Fetch ship data from Star Citizen API"""
    print("\n" + "=" * 80)
    print("STEP 2: Fetching Ship Data from API")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, "scripts/fetch_ships.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Ship data fetched successfully!")
            return True
        else:
            print(f"⚠️ Fetch script returned code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error fetching ship data: {e}")
        return False


def run_etl():
    """Run ETL pipeline to load data into database"""
    print("\n" + "=" * 80)
    print("STEP 3: Running ETL Pipeline")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, "scripts/etl_pipeline.py"],
            capture_output=True,
            text=True,
            timeout=300
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print("✅ ETL pipeline completed!")
            return True
        else:
            print(f"⚠️ ETL pipeline returned code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error running ETL: {e}")
        return False


def generate_embeddings():
    """Generate embeddings for semantic search"""
    print("\n" + "=" * 80)
    print("STEP 4: Generating Embeddings")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, "scripts/generate_embeddings.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for embeddings
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Embeddings generated!")
            return True
        else:
            print(f"⚠️ Embeddings script returned code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False


def verify_setup():
    """Verify database setup"""
    print("\n" + "=" * 80)
    print("VERIFICATION: Checking Database")
    print("=" * 80)

    try:
        from app.models import Ship, Manufacturer, ShipEmbedding

        session = SessionLocal()

        ship_count = session.query(Ship).count()
        mfr_count = session.query(Manufacturer).count()
        embedding_count = session.query(ShipEmbedding).count()

        print(f"\n📊 Database Statistics:")
        print(f"   Ships: {ship_count}")
        print(f"   Manufacturers: {mfr_count}")
        print(f"   Embeddings: {embedding_count}")

        if ship_count > 0 and embedding_count > 0:
            print("\n✅ Database setup complete and verified!")
            return True
        else:
            print("\n⚠️ Database setup incomplete - missing data")
            return False

    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False
    finally:
        session.close()


def main():
    """Main setup function"""
    print("\n" + "=" * 80)
    print("🚀 RENDER DATABASE SETUP")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Create database tables")
    print("2. Fetch ship data from Star Citizen API")
    print("3. Load data into database")
    print("4. Generate embeddings for search")
    print("\nEstimated time: 5-10 minutes")
    print("=" * 80)

    steps = [
        ("Creating tables", create_tables),
        ("Fetching ship data", fetch_ship_data),
        ("Running ETL", run_etl),
        ("Generating embeddings", generate_embeddings),
        ("Verifying setup", verify_setup),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please check the errors above and try again.")
            sys.exit(1)

    print("\n" + "=" * 80)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("=" * 80)
    print("\nYour Star Citizen ship database is ready!")
    print("You can now use the API for ship searches.")
    print("=" * 80)


if __name__ == "__main__":
    main()
