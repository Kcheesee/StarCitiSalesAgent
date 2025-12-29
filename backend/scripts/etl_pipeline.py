"""
ETL Pipeline - Transform raw ship JSON data into database
Loads all 116 ships from /data/raw_ships/ into PostgreSQL
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from app.models import (
    Manufacturer,
    Ship,
    ShipHardpoint,
    ShipComponent,
    ShipVehicleBay,
)
from sqlalchemy import text

# Paths
DATA_DIR = Path("/Users/jackalmac/Desktop/Code World/StarCitiSalesAgent/data")
RAW_SHIPS_DIR = DATA_DIR / "raw_ships"


def get_or_create_manufacturer(session, name: str, code: Optional[str] = None) -> Manufacturer:
    """Get existing manufacturer or create new one"""
    manufacturer = session.query(Manufacturer).filter_by(name=name).first()

    if not manufacturer:
        manufacturer = Manufacturer(name=name, code=code)
        session.add(manufacturer)
        session.flush()  # Get the ID without committing
        print(f"   📝 Created manufacturer: {name}")

    return manufacturer


def extract_multilingual_text(data: Dict, field: str, lang: str = "en_EN") -> Optional[str]:
    """Extract text from multilingual field"""
    if isinstance(data, dict):
        return data.get(lang, "")
    return data if isinstance(data, str) else None


def extract_focus(foci_list: List) -> Optional[str]:
    """Extract primary focus from foci array"""
    if foci_list and len(foci_list) > 0:
        focus_obj = foci_list[0]
        if isinstance(focus_obj, dict):
            return focus_obj.get("en_EN", "")
    return None


def safe_get(data: Dict, *keys, default=None):
    """Safely get nested dictionary value"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, {})
        else:
            return default
    return data if data != {} else default


def transform_ship_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw API JSON to Ship model fields"""
    data = raw_data.get("data", {})

    # Extract manufacturer info
    manufacturer_data = data.get("manufacturer", {})
    manufacturer_name = manufacturer_data.get("name", "Unknown")
    manufacturer_code = manufacturer_data.get("code", "")

    # Extract descriptions
    description = extract_multilingual_text(data.get("description", {}), "en_EN")
    description_de = extract_multilingual_text(data.get("description", {}), "de_DE")
    description_cn = extract_multilingual_text(data.get("description", {}), "zh_CN")

    # Extract focus and type
    focus = extract_focus(data.get("foci", []))
    ship_type = extract_multilingual_text(data.get("type", {}), "en_EN")

    # Generate UUID if missing (use slug as deterministic seed)
    ship_uuid = data.get("uuid", "")
    if not ship_uuid or ship_uuid.strip() == "":
        slug = data.get("slug", "")
        # Generate deterministic UUID from slug using UUID5 with a namespace
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
        ship_uuid = str(uuid.uuid5(namespace, f"starcitizen-ship-{slug}"))

    # Build ship data dict
    ship_data = {
        # Core identification
        "uuid": ship_uuid,
        "name": data.get("name", ""),
        "slug": data.get("slug", ""),
        "class_name": data.get("class_name", ""),

        # Manufacturer (will be set separately)
        "manufacturer_name": manufacturer_name,

        # Classification
        "focus": focus,
        "type": ship_type,

        # Dimensions
        "length": safe_get(data, "sizes", "length"),
        "beam": safe_get(data, "sizes", "beam"),
        "height": safe_get(data, "sizes", "height"),
        "mass": data.get("mass"),

        # Capacity
        "cargo_capacity": data.get("cargo_capacity", 0),
        "vehicle_inventory": data.get("vehicle_inventory"),
        "personal_inventory": data.get("personal_inventory"),

        # Crew
        "crew_min": safe_get(data, "crew", "min"),
        "crew_max": safe_get(data, "crew", "max"),
        "crew_weapon": safe_get(data, "crew", "weapon"),
        "crew_operation": safe_get(data, "crew", "operation"),

        # Health & Shields
        "health": data.get("health"),
        "shield_hp": data.get("shield_hp"),
        "shield_face_type": data.get("shield_face_type"),

        # Speed
        "speed_scm": safe_get(data, "speed", "scm"),
        "speed_max": safe_get(data, "speed", "max"),
        "speed_zero_to_scm": safe_get(data, "speed", "zero_to_scm"),
        "speed_zero_to_max": safe_get(data, "speed", "zero_to_max"),

        # Agility
        "agility_pitch": safe_get(data, "agility", "pitch"),
        "agility_yaw": safe_get(data, "agility", "yaw"),
        "agility_roll": safe_get(data, "agility", "roll"),

        # Acceleration
        "accel_main": safe_get(data, "agility", "acceleration", "main"),
        "accel_retro": safe_get(data, "agility", "acceleration", "retro"),
        "accel_vtol": safe_get(data, "agility", "acceleration", "vtol"),
        "accel_maneuvering": safe_get(data, "agility", "acceleration", "maneuvering"),

        # Fuel
        "fuel_capacity": safe_get(data, "fuel", "capacity"),
        "fuel_intake_rate": safe_get(data, "fuel", "intake_rate"),
        "fuel_usage_main": safe_get(data, "fuel", "usage", "main"),
        "fuel_usage_maneuvering": safe_get(data, "fuel", "usage", "maneuvering"),

        # Quantum
        "quantum_speed": safe_get(data, "quantum", "quantum_speed"),
        "quantum_spool_time": safe_get(data, "quantum", "quantum_spool_time"),
        "quantum_fuel_capacity": safe_get(data, "quantum", "quantum_fuel_capacity"),
        "quantum_range": safe_get(data, "quantum", "quantum_range"),

        # Emissions
        "emission_ir": safe_get(data, "emission", "ir"),
        "emission_em_idle": safe_get(data, "emission", "em_idle"),
        "emission_em_max": safe_get(data, "emission", "em_max"),

        # Descriptions
        "description": description,
        "description_de": description_de,
        "description_cn": description_cn,

        # Store complete raw data
        "raw_data": raw_data,
    }

    return {
        "ship_data": ship_data,
        "manufacturer_name": manufacturer_name,
        "manufacturer_code": manufacturer_code,
    }


def run_etl():
    """Main ETL process"""
    print("=" * 80)
    print("ETL PIPELINE - Loading Ships into Database")
    print("=" * 80)
    print()

    # Check for JSON files
    json_files = list(RAW_SHIPS_DIR.glob("*.json"))
    if not json_files:
        print(f"❌ No JSON files found in {RAW_SHIPS_DIR}")
        return

    print(f"📂 Found {len(json_files)} ship JSON files")
    print()

    # Stats
    stats = {
        "total": len(json_files),
        "successful": 0,
        "failed": 0,
        "manufacturers_created": 0,
        "manufacturers_existing": 0,
    }

    failed_ships = []

    # Create database session
    session = SessionLocal()

    try:
        # Clear existing ships (for clean re-import during development)
        print("🗑️  Clearing existing ships...")
        session.execute(text("TRUNCATE ships, ship_hardpoints, ship_components, ship_vehicle_bays, ship_embeddings CASCADE"))
        session.commit()
        print("   ✅ Cleared\n")

        # Process each ship
        for i, json_file in enumerate(sorted(json_files), 1):
            slug = json_file.stem
            print(f"[{i}/{len(json_files)}] Processing: {slug:<40}", end=" ")

            try:
                # Load raw JSON
                with open(json_file, 'r') as f:
                    raw_data = json.load(f)

                # Transform data
                transformed = transform_ship_data(raw_data)
                ship_data = transformed["ship_data"]

                # Check if ship already exists by slug (handle duplicates)
                existing_ship = session.query(Ship).filter_by(slug=ship_data["slug"]).first()
                if existing_ship:
                    print(f"⚠️  SKIPPED (duplicate slug: {ship_data['slug']})")
                    stats["failed"] += 1
                    failed_ships.append({"slug": slug, "error": f"Duplicate slug: {ship_data['slug']}"})
                    continue

                # Get or create manufacturer
                manufacturer = get_or_create_manufacturer(
                    session,
                    transformed["manufacturer_name"],
                    transformed["manufacturer_code"]
                )

                # Create ship
                ship = Ship(
                    **ship_data,
                    manufacturer_id=manufacturer.id
                )

                session.add(ship)
                session.flush()  # Get ship.id

                print(f"✅ {ship.name}")
                stats["successful"] += 1

                # Commit every 10 ships to avoid huge transactions
                if i % 10 == 0:
                    session.commit()
                    print(f"   💾 Committed {i} ships\n")

            except Exception as e:
                print(f"❌ ERROR: {e}")
                stats["failed"] += 1
                failed_ships.append({"slug": slug, "error": str(e)})
                session.rollback()

        # Final commit
        session.commit()

        # Summary
        print("\n" + "=" * 80)
        print("ETL COMPLETE")
        print("=" * 80)
        print(f"\n✅ Successfully loaded: {stats['successful']} ships")
        print(f"❌ Failed: {stats['failed']} ships")

        if failed_ships:
            print("\nFailed ships:")
            for ship in failed_ships:
                print(f"  - {ship['slug']}: {ship['error']}")

        # Validate database
        print("\n" + "=" * 80)
        print("DATABASE VALIDATION")
        print("=" * 80)

        ship_count = session.query(Ship).count()
        mfr_count = session.query(Manufacturer).count()

        print(f"\nShips in database: {ship_count}")
        print(f"Manufacturers in database: {mfr_count}")

        # Count by manufacturer
        print("\nShips by manufacturer:")
        manufacturers = session.query(Manufacturer).all()
        for mfr in sorted(manufacturers, key=lambda m: len(m.ships), reverse=True)[:10]:
            count = len(mfr.ships)
            print(f"  {mfr.name:<40} {count:>3} ships")

        # Data completeness
        print("\n" + "=" * 80)
        print("DATA COMPLETENESS CHECK")
        print("=" * 80)

        completeness = {}
        critical_fields = [
            ("name", "Name"),
            ("cargo_capacity", "Cargo Capacity"),
            ("crew_min", "Min Crew"),
            ("length", "Length"),
            ("mass", "Mass"),
            ("speed_scm", "SCM Speed"),
            ("description", "Description"),
            ("focus", "Focus/Role"),
        ]

        for field, label in critical_fields:
            count = session.query(Ship).filter(getattr(Ship, field) != None).count()
            percentage = (count / ship_count * 100) if ship_count > 0 else 0
            completeness[field] = percentage

            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {label:<20} {bar} {percentage:>5.1f}% ({count}/{ship_count})")

        print("\n✨ ETL Pipeline Complete!")
        print(f"🚀 {ship_count} ships ready for AI consultant!")

        return {
            "total": stats["total"],
            "successful": stats["successful"],
            "failed": stats["failed"],
            "ships_in_db": ship_count,
            "manufacturers_in_db": mfr_count,
            "completeness": completeness
        }

    except Exception as e:
        print(f"\n❌ ETL Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    try:
        results = run_etl()
        print(f"\n{'='*80}")
        print("✅ SUCCESS - Database is ready!")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ FAILED: {e}")
        print(f"{'='*80}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
