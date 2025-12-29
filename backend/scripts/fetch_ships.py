"""
Comprehensive Ship Data Collector
Fetches full data for all ships in the ship_list.json
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

API_BASE = "https://api.star-citizen.wiki/api/v2"

# Use relative paths that work anywhere (local dev or Render)
# Script is in backend/scripts/, so go up 2 levels to project root, then into data/
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_SHIPS_DIR = DATA_DIR / "raw_ships"

# Create directories
RAW_SHIPS_DIR.mkdir(parents=True, exist_ok=True)

def load_ship_list() -> List[str]:
    """Load the discovered ship list"""
    ship_list_path = DATA_DIR / "ship_list.json"

    if not ship_list_path.exists():
        print("❌ Ship list not found. Run discover_ships.py first!")
        return []

    with open(ship_list_path, 'r') as f:
        data = json.load(f)

    return data.get('valid_ships', [])

def fetch_ship_data(ship_slug: str) -> Dict[str, Any]:
    """Fetch data for a single ship"""
    url = f"{API_BASE}/vehicles/{ship_slug}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def save_ship_data(ship_slug: str, data: Dict):
    """Save ship data to JSON file"""
    filepath = RAW_SHIPS_DIR / f"{ship_slug}.json"
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def analyze_completeness(ships_data: List[Dict]) -> Dict:
    """Analyze data completeness across all ships"""
    field_presence = defaultdict(int)
    total_ships = len(ships_data)

    critical_fields = [
        'name', 'slug', 'cargo_capacity', 'crew.min', 'crew.max',
        'sizes.length', 'sizes.beam', 'sizes.height', 'mass',
        'speed.scm', 'speed.max', 'manufacturer.name', 'foci', 'type', 'description'
    ]

    for ship_data in ships_data:
        if 'data' not in ship_data:
            continue

        data = ship_data['data']

        # Check critical fields
        for field in critical_fields:
            parts = field.split('.')
            value = data
            try:
                for part in parts:
                    value = value.get(part) if isinstance(value, dict) else None
                if value is not None and value != "" and value != []:
                    field_presence[field] += 1
            except:
                pass

    completeness = {}
    for field in critical_fields:
        count = field_presence[field]
        percentage = (count / total_ships * 100) if total_ships > 0 else 0
        completeness[field] = {
            "present": count,
            "total": total_ships,
            "percentage": round(percentage, 1)
        }

    return completeness

def fetch_all_ships():
    """Main function to fetch all ship data"""
    print("=" * 80)
    print("COMPREHENSIVE SHIP DATA COLLECTION")
    print("=" * 80)
    print()

    # Load ship list
    ship_slugs = load_ship_list()

    if not ship_slugs:
        print("❌ No ships to fetch!")
        return

    print(f"📋 Found {len(ship_slugs)} ships to fetch")
    print(f"💾 Saving raw data to: {RAW_SHIPS_DIR}")
    print()

    successful = []
    failed = []
    all_ships_data = []

    # Fetch each ship
    for i, slug in enumerate(ship_slugs, 1):
        print(f"[{i}/{len(ship_slugs)}] Fetching: {slug:<35}", end=" ")

        ship_data = fetch_ship_data(slug)

        if "error" in ship_data:
            print(f"❌ {ship_data['error']}")
            failed.append({
                "slug": slug,
                "error": ship_data['error']
            })
        else:
            # Extract key info for display
            data = ship_data.get('data', {})
            name = data.get('name', 'Unknown')
            manufacturer = data.get('manufacturer', {}).get('name', 'Unknown')
            cargo = data.get('cargo_capacity', 'N/A')

            print(f"✅ {name} ({manufacturer}) - {cargo} SCU")

            # Save individual file
            save_ship_data(slug, ship_data)

            successful.append({
                "slug": slug,
                "name": name,
                "manufacturer": manufacturer,
                "cargo": cargo
            })
            all_ships_data.append(ship_data)

        # Rate limiting - be nice to the API
        time.sleep(0.4)

        # Progress marker every 20 ships
        if i % 20 == 0:
            print(f"\n   Progress: {len(successful)} ✅  |  {len(failed)} ❌\n")

    print("\n" + "=" * 80)
    print("COLLECTION COMPLETE")
    print("=" * 80)
    print(f"\n✅ Successfully fetched: {len(successful)} ships")
    print(f"❌ Failed: {len(failed)} ships")

    if failed:
        print("\nFailed ships:")
        for ship in failed:
            print(f"  - {ship['slug']}: {ship['error']}")

    # Analyze completeness
    print("\n" + "=" * 80)
    print("DATA COMPLETENESS ANALYSIS")
    print("=" * 80)

    completeness = analyze_completeness(all_ships_data)

    print("\nCritical Fields Completeness:")
    for field, stats in completeness.items():
        bar_length = int(stats['percentage'] / 5)  # Scale to 20 chars
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  {field:<25} {bar} {stats['percentage']:>5.1f}% ({stats['present']}/{stats['total']})")

    # Save manifest
    manifest = {
        "total_ships": len(ship_slugs),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": round(len(successful) / len(ship_slugs) * 100, 2),
        "successful_ships": successful,
        "failed_ships": failed,
        "completeness": completeness
    }

    manifest_path = DATA_DIR / "collection_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n💾 Manifest saved to: {manifest_path}")

    # Summary stats
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    if successful:
        # Count by manufacturer
        mfr_counts = defaultdict(int)
        total_cargo = 0
        cargo_ships = 0

        for ship in successful:
            mfr_counts[ship['manufacturer']] += 1
            if isinstance(ship['cargo'], (int, float)) and ship['cargo'] > 0:
                total_cargo += ship['cargo']
                cargo_ships += 1

        print(f"\nShips by Manufacturer:")
        for mfr, count in sorted(mfr_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {mfr:<40} {count:>3} ships")

        if cargo_ships > 0:
            avg_cargo = total_cargo / cargo_ships
            print(f"\nCargo Statistics:")
            print(f"  Ships with cargo: {cargo_ships}")
            print(f"  Average cargo: {avg_cargo:.1f} SCU")

    print(f"\n✨ All data saved to: {RAW_SHIPS_DIR}")
    print(f"📊 {len(successful)} ship JSON files ready for ETL pipeline")

    return manifest

if __name__ == "__main__":
    try:
        manifest = fetch_all_ships()

        print("\n" + "=" * 80)
        print("🎉 SHIP DATA COLLECTION COMPLETE!")
        print("=" * 80)
        print(f"\n📦 Collected: {manifest['successful']} / {manifest['total_ships']} ships")
        print(f"✅ Success rate: {manifest['success_rate']}%")
        print("\n🚀 Ready for Task 1.3: Database Schema & ETL!")

    except Exception as e:
        print(f"\n❌ Error during collection: {e}")
        import traceback
        traceback.print_exc()
