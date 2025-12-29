"""
Ship List Discovery Script
Discovers all available ship slugs from the Star Citizen Wiki
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Set

API_BASE = "https://api.star-citizen.wiki/api/v2"
WIKI_VEHICLES_PAGE = "https://starcitizen.tools/Category:Vehicles"

def discover_from_wiki_html() -> Set[str]:
    """Scrape ship slugs from the Star Citizen Tools wiki"""
    print("🔍 Discovering ships from Star Citizen Tools wiki...")

    ship_slugs = set()

    try:
        # The main vehicles category page
        response = requests.get(WIKI_VEHICLES_PAGE, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all vehicle links in the category
            vehicle_links = soup.find_all('a', href=True)

            for link in vehicle_links:
                href = link.get('href', '')
                # Extract vehicle names from wiki links
                if '/wiki/' in href and not any(x in href for x in ['Category:', 'Special:', 'File:', 'Talk:']):
                    vehicle_name = href.split('/wiki/')[-1]
                    # Convert wiki page name to potential API slug
                    slug = vehicle_name.lower().replace('_', '-').replace(' ', '-')
                    if slug and len(slug) > 2:  # Filter out very short names
                        ship_slugs.add(slug)

            print(f"   Found {len(ship_slugs)} potential ships from wiki")
    except Exception as e:
        print(f"   ⚠️ Error scraping wiki: {e}")

    return ship_slugs

def discover_from_known_manufacturers() -> Set[str]:
    """Generate ship slugs from known manufacturers and naming patterns"""
    print("🔍 Generating ships from known manufacturers...")

    # Known manufacturer codes and their ships
    manufacturers = {
        "AEGS": ["gladius", "sabre", "sabre-comet", "avenger-titan", "avenger-stalker",
                 "avenger-warlock", "hammerhead", "javelin", "reclaimer", "redeemer",
                 "retaliator", "vanguard-harbinger", "vanguard-sentinel", "vanguard-warden",
                 "eclipse", "nautilus"],
        "ANVL": ["arrow", "carrack", "hawk", "hornet-f7a", "f7c-hornet", "f7c-hornet-wildfire",
                 "f7c-m-super-hornet", "f7c-r-hornet-tracker", "hurricane", "lightning",
                 "terrapin", "valkyrie", "crucible", "ballista"],
        "ORIG": ["300i", "315p", "325a", "350r", "85x", "400i", "600i", "600i-explorer",
                 "890-jump", "m50", "x1"],
        "MISC": ["freelancer", "freelancer-dur", "freelancer-max", "freelancer-mis",
                 "hull-a", "hull-b", "hull-c", "hull-d", "hull-e",
                 "prospector", "razor", "razor-ex", "razor-lx", "reliant-kore",
                 "reliant-mako", "reliant-sen", "reliant-tana", "starfarer",
                 "starfarer-gemini", "endeavor", "odyssey"],
        "RSI": ["aurora-cl", "aurora-es", "aurora-ln", "aurora-lx", "aurora-mr",
                "constellation-andromeda", "constellation-aquila", "constellation-phoenix",
                "constellation-taurus", "mantis", "orion", "polaris", "apollo"],
        "DRAK": ["buccaneer", "caterpillar", "corsair", "cutlass-black", "cutlass-blue",
                 "cutlass-red", "dragonfly", "herald", "vulture", "kraken", "kraken-privateer"],
        "CRUS": ["ares-inferno", "ares-ion", "c2-hercules", "m2-hercules", "a2-hercules",
                 "mercury", "mercury-star-runner", "genesis", "starlifter"],
        "ARGO": ["mole", "mpuv-cargo", "mpuv-personnel", "raft", "srv"],
        "CNOU": ["mustang-alpha", "mustang-beta", "mustang-delta", "mustang-gamma",
                 "mustang-omega", "nomad"],
        "ESPR": ["prowler", "talon", "talon-shrike", "blade", "glaive", "scythe"],
        "KRGR": ["p-52-merlin", "p-72-archimedes"],
        "TMBL": ["cyclone", "cyclone-aa", "cyclone-rc", "cyclone-rn", "cyclone-tr",
                 "nova"],
        "BANU": ["defender", "merchantman"],
        "VNCL": ["blade"],
    }

    ship_slugs = set()
    for manufacturer, ships in manufacturers.items():
        ship_slugs.update(ships)

    print(f"   Generated {len(ship_slugs)} ships from manufacturers")
    return ship_slugs

def discover_from_number_series() -> Set[str]:
    """Generate ship slugs from numbered series (100i, 200i, etc.)"""
    ship_slugs = set()

    # Origin series
    for num in [100, 125, 135, 200, 300, 315, 325, 350, 400, 600, 890]:
        ship_slugs.add(f"{num}i")
        if num in [315, 325, 350]:
            ship_slugs.add(f"{num}p")  # Some have variants

    # Add common variants
    variants = ['100i', '125a', '135c']
    ship_slugs.update(variants)

    return ship_slugs

def test_ship_exists(slug: str) -> bool:
    """Test if a ship slug exists in the API"""
    url = f"{API_BASE}/vehicles/{slug}"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def discover_all_ships() -> List[str]:
    """Discover all available ship slugs using multiple methods"""
    print("=" * 80)
    print("SHIP DISCOVERY - Finding All Available Ships")
    print("=" * 80)
    print()

    all_candidates = set()

    # Method 1: Scrape wiki
    wiki_ships = discover_from_wiki_html()
    all_candidates.update(wiki_ships)

    # Method 2: Known manufacturers
    manufacturer_ships = discover_from_known_manufacturers()
    all_candidates.update(manufacturer_ships)

    # Method 3: Number series
    number_series = discover_from_number_series()
    all_candidates.update(number_series)

    print(f"\n📊 Total candidate ships: {len(all_candidates)}")
    print("\n🧪 Testing which ships exist in the API...")
    print("(This may take a few minutes with rate limiting)")
    print()

    valid_ships = []
    invalid_ships = []

    for i, slug in enumerate(sorted(all_candidates), 1):
        print(f"[{i}/{len(all_candidates)}] Testing: {slug:<40}", end=" ")

        if test_ship_exists(slug):
            print("✅")
            valid_ships.append(slug)
        else:
            print("❌")
            invalid_ships.append(slug)

        # Rate limiting
        time.sleep(0.3)

        # Progress update every 20 ships
        if i % 20 == 0:
            print(f"\n   Progress: {len(valid_ships)} valid, {len(invalid_ships)} invalid\n")

    print("\n" + "=" * 80)
    print("DISCOVERY COMPLETE")
    print("=" * 80)
    print(f"\n✅ Valid ships found: {len(valid_ships)}")
    print(f"❌ Invalid slugs: {len(invalid_ships)}")

    # Save results
    results = {
        "valid_ships": sorted(valid_ships),
        "invalid_ships": sorted(invalid_ships),
        "total_candidates": len(all_candidates),
        "total_valid": len(valid_ships),
        "total_invalid": len(invalid_ships)
    }

    output_path = "/Users/jackalmac/Desktop/Code World/StarCitiSalesAgent/data/ship_list.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Ship list saved to: data/ship_list.json")

    return valid_ships

if __name__ == "__main__":
    try:
        ships = discover_all_ships()

        print(f"\n🎉 Discovery complete!")
        print(f"Found {len(ships)} valid ships in the API")
        print("\nReady to fetch full data for all ships!")

    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
        import traceback
        traceback.print_exc()
