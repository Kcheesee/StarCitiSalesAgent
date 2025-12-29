import requests
import json

def test_sc_wiki_api():
    """Test fetching ship data from star-citizen.wiki API"""
    
    # Base URL
    base_url = "https://api.star-citizen.wiki/api/v2/vehicles"
    
    # Test 1: Fetch a specific ship (300i)
    print("=" * 50)
    print("TEST 1: Fetching 300i ship data")
    print("=" * 50)
    
    ship_url = f"{base_url}/300i"
    response = requests.get(ship_url)
    
    if response.status_code == 200:
        ship_data = response.json()
        print(f"✅ Success! Got data for: {ship_data.get('data', {}).get('name', 'Unknown')}")
        print(f"\nSample data structure:")
        print(json.dumps(ship_data, indent=2)[:500])  # First 500 chars
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 2: List all ships
    print("\n" + "=" * 50)
    print("TEST 2: Fetching all ships list")
    print("=" * 50)
    
    ships_list_url = "https://api.star-citizen.wiki/starcitizen/vehicles/ships"
    response = requests.get(ships_list_url)
    
    if response.status_code == 200:
        print(f"✅ Success! Status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        # This might be HTML, not JSON
        print(f"First 200 chars of response:\n{response.text[:200]}")
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    test_sc_wiki_api()