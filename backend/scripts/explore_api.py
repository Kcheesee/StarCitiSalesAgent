"""
Star Citizen Wiki API Explorer
Comprehensive exploration of the API to understand data structure and availability
"""

import requests
import json
from typing import Dict, List, Any
from collections import defaultdict
import time

# API Base URL
API_BASE = "https://api.star-citizen.wiki/api/v2"

# Sample ships from different categories for testing
TEST_SHIPS = {
    "Fighter": ["gladius", "hornet", "arrow", "sabre"],
    "Cargo": ["freelancer", "hull-a", "caterpillar", "c2-hercules"],
    "Exploration": ["carrack", "constellation-andromeda", "terrapin", "315p"],
    "Mining": ["prospector", "mole"],
    "Multi-role": ["cutlass-black", "vanguard-warden", "400i"],
    "Starter": ["aurora-mr", "mustang-alpha", "avenger-titan"],
    "Large": ["hammerhead", "890-jump", "reclaimer"],
    "Small": ["origin-85x", "mpuv-cargo", "p-52-merlin"]
}

def fetch_ship_data(ship_slug: str) -> Dict[str, Any]:
    """Fetch data for a single ship"""
    url = f"{API_BASE}/vehicles/{ship_slug}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def analyze_field_availability(ships_data: List[Dict]) -> Dict[str, Dict]:
    """Analyze which fields are available across ships"""
    field_stats = defaultdict(lambda: {"count": 0, "total": 0, "sample_values": []})

    for ship_data in ships_data:
        if "data" not in ship_data:
            continue

        data = ship_data["data"]

        def traverse_dict(d, prefix=""):
            """Recursively traverse nested dictionary"""
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                field_stats[full_key]["total"] += 1

                if value is not None and value != "" and value != [] and value != {}:
                    field_stats[full_key]["count"] += 1
                    if len(field_stats[full_key]["sample_values"]) < 3:
                        if isinstance(value, (dict, list)) and len(str(value)) > 100:
                            field_stats[full_key]["sample_values"].append(f"{type(value).__name__} (complex)")
                        else:
                            field_stats[full_key]["sample_values"].append(value)

                # Recurse into nested dicts
                if isinstance(value, dict):
                    traverse_dict(value, full_key)

        traverse_dict(data)

    return dict(field_stats)

def explore_api():
    """Main exploration function"""
    print("=" * 80)
    print("STAR CITIZEN WIKI API EXPLORATION")
    print("=" * 80)
    print()

    all_ships_data = []
    successful_ships = []
    failed_ships = []

    # Test each ship category
    for category, ships in TEST_SHIPS.items():
        print(f"\n{'='*80}")
        print(f"Testing {category.upper()} Ships")
        print(f"{'='*80}")

        for ship_slug in ships:
            print(f"\nFetching: {ship_slug}...", end=" ")
            ship_data = fetch_ship_data(ship_slug)

            if "error" in ship_data:
                print(f"❌ FAILED: {ship_data['error']}")
                failed_ships.append({"slug": ship_slug, "category": category, "error": ship_data['error']})
            else:
                print(f"✅ SUCCESS")
                all_ships_data.append(ship_data)
                successful_ships.append({"slug": ship_slug, "category": category})

                # Print basic info
                data = ship_data.get("data", {})
                print(f"   Name: {data.get('name', 'N/A')}")
                print(f"   Manufacturer: {data.get('manufacturer', {}).get('name', 'N/A')}")
                print(f"   Cargo: {data.get('cargo_capacity', 'N/A')} SCU")
                print(f"   Crew: {data.get('crew', {}).get('min', 'N/A')}-{data.get('crew', {}).get('max', 'N/A')}")

                # Print price if available
                if 'store_url' in data or 'shops' in data:
                    print(f"   Available in game: Yes")

            # Rate limiting
            time.sleep(0.5)

    # Analysis
    print(f"\n\n{'='*80}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal ships tested: {len(successful_ships) + len(failed_ships)}")
    print(f"Successful: {len(successful_ships)}")
    print(f"Failed: {len(failed_ships)}")

    if failed_ships:
        print("\nFailed ships:")
        for ship in failed_ships:
            print(f"  - {ship['slug']} ({ship['category']}): {ship['error']}")

    # Field availability analysis
    print(f"\n\n{'='*80}")
    print("FIELD AVAILABILITY ANALYSIS")
    print(f"{'='*80}")

    field_stats = analyze_field_availability(all_ships_data)

    # Group fields by completion rate
    critical_fields = []
    common_fields = []
    sparse_fields = []

    for field, stats in sorted(field_stats.items()):
        if stats["total"] == 0:
            continue
        completion_rate = (stats["count"] / stats["total"]) * 100

        field_info = {
            "field": field,
            "completion": completion_rate,
            "present": stats["count"],
            "total": stats["total"],
            "samples": stats["sample_values"]
        }

        if completion_rate >= 90:
            critical_fields.append(field_info)
        elif completion_rate >= 50:
            common_fields.append(field_info)
        else:
            sparse_fields.append(field_info)

    print(f"\n🟢 CRITICAL FIELDS (90%+ availability):")
    for field in critical_fields[:20]:  # Top 20
        print(f"  ✓ {field['field']}: {field['completion']:.1f}% ({field['present']}/{field['total']})")
        if field['samples']:
            print(f"    Sample: {field['samples'][0]}")

    print(f"\n🟡 COMMON FIELDS (50-90% availability):")
    for field in common_fields[:15]:  # Top 15
        print(f"  ~ {field['field']}: {field['completion']:.1f}% ({field['present']}/{field['total']})")

    print(f"\n🔴 SPARSE FIELDS (<50% availability):")
    print(f"  Total sparse fields: {len(sparse_fields)}")
    print(f"  (These may need to be scraped from other sources)")

    # Save detailed results
    print(f"\n\n{'='*80}")
    print("SAVING DETAILED RESULTS")
    print(f"{'='*80}")

    # Save sample data for inspection
    with open('/Users/jackalmac/Desktop/Code World/StarCitiSalesAgent/data/api_exploration_results.json', 'w') as f:
        json.dump({
            "successful_ships": successful_ships,
            "failed_ships": failed_ships,
            "field_statistics": {
                "critical_fields": critical_fields,
                "common_fields": common_fields,
                "sparse_fields": [{"field": f["field"], "completion": f["completion"]} for f in sparse_fields]
            },
            "sample_ships_data": all_ships_data[:3]  # Save first 3 for inspection
        }, f, indent=2)

    print("✅ Results saved to: data/api_exploration_results.json")

    # Key findings
    print(f"\n\n{'='*80}")
    print("KEY FINDINGS & RECOMMENDATIONS")
    print(f"{'='*80}")

    print("\n1. CRITICAL FIELDS FOR DATABASE:")
    for field in critical_fields[:10]:
        print(f"   - {field['field']}")

    print("\n2. DATA GAPS IDENTIFIED:")
    print("   - Marketing descriptions (likely need RSI website scrape)")
    print("   - High-resolution images (need RSI website)")
    print("   - Pricing in USD (need RSI store scrape)")
    print("   - Detailed weapon loadouts (may need erkul.games)")

    print("\n3. NEXT STEPS:")
    print("   - Create database schema based on critical fields")
    print("   - Build RSI website scraper for missing data")
    print("   - Develop method to get full ship list")
    print("   - Set up ETL pipeline for data collection")

    return {
        "successful_count": len(successful_ships),
        "failed_count": len(failed_ships),
        "critical_fields": len(critical_fields),
        "common_fields": len(common_fields),
        "sparse_fields": len(sparse_fields)
    }

if __name__ == "__main__":
    try:
        results = explore_api()
        print(f"\n\n{'='*80}")
        print("✅ API Exploration Complete!")
        print(f"{'='*80}")
        print(f"Successfully analyzed {results['successful_count']} ships")
        print(f"Identified {results['critical_fields']} critical fields")
        print(f"Ready to proceed with database design and data collection!")
    except Exception as e:
        print(f"\n❌ Error during exploration: {e}")
        import traceback
        traceback.print_exc()
