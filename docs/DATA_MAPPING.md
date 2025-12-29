# Star Citizen Wiki API - Data Mapping Documentation

**Generated:** 2025-12-27
**API Base:** `https://api.star-citizen.wiki/api/v2`
**Ships Analyzed:** 24 ships across 8 categories

---

## Executive Summary

The Star Citizen Wiki API provides comprehensive technical data for ships, including performance metrics, dimensions, and equipment. However, several key fields needed for a sales consultant are **missing** and will require scraping from external sources.

### ✅ Available from API (90%+ completion)
- Technical specifications (dimensions, mass, cargo)
- Performance metrics (speed, acceleration, handling)
- Equipment details (weapons, shields, components)
- Basic descriptions (multi-language)
- Ship focus/role categorization

### ❌ Missing from API (Need External Sources)
- **USD Pricing** (need RSI store scrape)
- **aUEC In-game pricing** (need in-game data or community sources)
- **Marketing descriptions** (need RSI ship pages)
- **High-resolution images** (need RSI media kit)
- **Detailed weapon loadouts** (need erkul.games or similar)
- **Vehicle bay specifics** (partially missing)

---

## API Endpoint Structure

### Individual Ship Data
```
GET https://api.star-citizen.wiki/api/v2/vehicles/{ship-slug}
```

**Example:** `https://api.star-citizen.wiki/api/v2/vehicles/gladius`

**Response Format:**
```json
{
  "data": {
    "uuid": "string",
    "name": "string",
    "slug": "string",
    "class_name": "string",
    ...
  }
}
```

### Ship List Endpoint
**Status:** ⚠️ The `/vehicles/ships` endpoint returns HTML, not JSON

**Solutions:**
1. Scrape the HTML page for ship slugs
2. Use the UEX Corporation API (community-maintained)
3. Manually curate a list of popular ships (50-150)
4. Build incrementally from known ship families

---

## Complete Field Reference

### Core Identification Fields

| Field | Type | Availability | Description | Example |
|-------|------|--------------|-------------|---------|
| `uuid` | string | 100% | Unique identifier | `"b6b59889-7226-458e-a6b0-1c9392128a3c"` |
| `name` | string | 100% | Display name | `"Gladius"` |
| `slug` | string | 100% | URL-safe identifier | `"gladius"` |
| `class_name` | string | 100% | Internal game class | `"AEGS_Gladius"` |

### Dimensions & Physical Properties

| Field | Type | Availability | Description | Unit |
|-------|------|--------------|-------------|------|
| `sizes.length` | number | 100% | Ship length | meters |
| `sizes.beam` | number | 100% | Ship width | meters |
| `sizes.height` | number | 100% | Ship height | meters |
| `mass` | number | 100% | Total mass | kg |
| `health` | number | 100% | Hull hit points | HP |
| `shield_hp` | number | 100% | Total shield HP | HP |
| `shield_face_type` | string | 100% | Shield type | `"Bubble"` or `"Quadrant"` |

### Cargo & Storage

| Field | Type | Availability | Description | Unit |
|-------|------|--------------|-------------|------|
| `cargo_capacity` | number | 100% | Total cargo capacity | SCU |
| `cargo_grids` | array | 100% | Cargo grid details | - |
| `vehicle_inventory` | number | 100% | Vehicle storage | SCU |
| `personal_inventory` | number | 100% | Personal item storage | SCU |

### Crew Requirements

| Field | Type | Availability | Description |
|-------|------|--------------|-------------|
| `crew.min` | number | 100% | Minimum crew size |
| `crew.max` | number | ~60% | Maximum crew size |
| `crew.weapon` | number | 100% | Weapon operators needed |
| `crew.operation` | number | ~40% | Other operational crew |

### Performance Metrics

#### Speed
| Field | Type | Availability | Unit | Description |
|-------|------|--------------|------|-------------|
| `speed.scm` | number | 100% | m/s | Standard Combat Maneuver speed |
| `speed.max` | number | 100% | m/s | Maximum speed (afterburner) |
| `speed.scm_boost_forward` | number | 90% | m/s | SCM boost forward |
| `speed.scm_boost_backward` | number | 90% | m/s | SCM boost backward |
| `speed.zero_to_scm` | number | 100% | seconds | Time to reach SCM from 0 |
| `speed.zero_to_max` | number | 100% | seconds | Time to reach max from 0 |
| `speed.scm_to_zero` | number | 100% | seconds | Deceleration time |

#### Agility
| Field | Type | Availability | Unit | Description |
|-------|------|--------------|------|-------------|
| `agility.pitch` | number | 90% | deg/s | Pitch rate |
| `agility.yaw` | number | 90% | deg/s | Yaw rate |
| `agility.roll` | number | 90% | deg/s | Roll rate |
| `agility.acceleration.main` | number | 100% | m/s² | Forward acceleration |
| `agility.acceleration.retro` | number | 100% | m/s² | Reverse acceleration |
| `agility.acceleration.maneuvering` | number | 100% | m/s² | Strafe acceleration |
| `agility.acceleration.main_g` | number | 100% | G | Forward G-force |

#### Afterburner
| Field | Type | Availability | Description |
|-------|------|--------------|-------------|
| `afterburner.capacitor` | number | 100% | Afterburner fuel capacity |
| `afterburner.regen_per_sec` | number | 100% | Regeneration rate |
| `afterburner.pitch_boost_multiplier` | number | 100% | Pitch boost when AB active |
| `afterburner.roll_boost_multiplier` | number | 100% | Roll boost when AB active |
| `afterburner.yaw_boost_multiplier` | number | 100% | Yaw boost when AB active |

### Fuel & Quantum Travel

#### Fuel
| Field | Type | Availability | Unit | Description |
|-------|------|--------------|------|-------------|
| `fuel.capacity` | number | 100% | liters | Hydrogen fuel capacity |
| `fuel.intake_rate` | number | 100% | L/s | Fuel scoop rate (if equipped) |
| `fuel.usage.main` | number | 100% | L/s | Main thruster consumption |
| `fuel.usage.maneuvering` | number | 100% | L/s | Maneuvering thruster consumption |

#### Quantum Drive
| Field | Type | Availability | Unit | Description |
|-------|------|--------------|------|-------------|
| `quantum.quantum_speed` | number | 100% | m/s | Quantum travel speed |
| `quantum.quantum_spool_time` | number | 100% | seconds | Time to spool up |
| `quantum.quantum_fuel_capacity` | number | 100% | units | Quantum fuel capacity |
| `quantum.quantum_range` | number | 100% | meters | Maximum jump range |

### Emissions & Signatures

| Field | Type | Availability | Description |
|-------|------|--------------|-------------|
| `emission.ir` | number | 100% | Infrared signature |
| `emission.em_idle` | number | 100% | EM signature (idle) |
| `emission.em_max` | number | 100% | EM signature (max) |
| `armor.signal_infrared` | number | 100% | IR signature multiplier |
| `armor.signal_electromagnetic` | number | 100% | EM signature multiplier |
| `armor.signal_cross_section` | number | 100% | Cross-section multiplier |

### Armor & Damage Modifiers

| Field | Type | Availability | Description |
|-------|------|--------------|-------------|
| `armor.damage_physical` | number | 100% | Physical damage modifier |
| `armor.damage_energy` | number | 100% | Energy damage modifier |
| `armor.damage_distortion` | number | 100% | Distortion damage modifier |
| `armor.damage_thermal` | number | 100% | Thermal damage modifier |
| `armor.damage_biochemical` | number | 100% | Biochemical damage modifier |
| `armor.damage_stun` | number | 100% | Stun damage modifier |

### Classification & Description

| Field | Type | Availability | Description |
|-------|------|--------------|-------------|
| `foci` | array | 100% | Ship roles (multi-language) |
| `type` | object | 100% | Ship type (multi-language) |
| `description` | object | 100% | Ship description (multi-language) |
| `manufacturer.name` | string | 100% | Manufacturer name |
| `manufacturer.code` | string | 100% | Manufacturer code (e.g., "AEGS") |

**Foci Examples:** "Light Fighter", "Heavy Cargo", "Exploration", "Mining", "Multi-role"

**Type Examples:** "combat", "industrial", "exploration", "transport"

**Languages Available:** `en_EN` (English), `de_DE` (German), `zh_CN` (Chinese)

---

## Equipment & Hardpoints

### Available Data
- ✅ Component types (shields, power plants, coolers, quantum drives)
- ✅ Component sizes
- ✅ Component quantities
- ⚠️ Hardpoint data (partially available, inconsistent)
- ❌ Default weapon loadouts (missing)
- ❌ Maximum weapon sizes per hardpoint (inconsistent)

**Note:** Detailed hardpoint/weapon data is **sparse** in the API. Recommend using:
- erkul.games API for detailed loadouts
- Manual curation for popular ships
- Community databases (UEX Corporation, FleetYards)

---

## Data Quality Assessment

### Test Results Summary
- **Ships Tested:** 26
- **Successful:** 24 (92.3%)
- **Failed:** 2 (7.7%)
  - `hornet` - returns 404 (use `f7c-hornet` instead)
  - `origin-85x` - returns 404 (use `85x` instead)

### Field Completion Rates

**Excellent (90-100%)**
- Core identification (uuid, name, slug)
- Dimensions (length, beam, height, mass)
- Cargo capacity
- Crew requirements (min)
- Performance metrics (speed, acceleration)
- Fuel and quantum data
- Armor and damage modifiers
- Descriptions and classifications

**Good (70-90%)**
- Crew.max (60% - many ships have null)
- Speed boost metrics (90%)
- Agility metrics (90%)

**Poor (<50%)**
- Hardpoint details
- Component lists
- Vehicle bay specifics
- Pricing (0% - not in API)

---

## Data Gaps & External Source Strategy

### 1. Pricing Data

**Gap:** No USD or aUEC pricing in API

**Solution:**
```
Source 1: RSI Store (USD pricing)
  URL: https://robertsspaceindustries.com/pledge/ships/{ship-name}
  Method: Web scraping with BeautifulSoup
  Frequency: Weekly (prices rarely change)

Source 2: In-game shops (aUEC pricing)
  URL: Community databases (UEX, FleetYards)
  Method: API or manual curation
  Frequency: Per patch (prices change with updates)
```

### 2. Marketing Descriptions

**Gap:** API descriptions are technical, not sales-focused

**Solution:**
```
Source: RSI Ship Pages
  URL: https://robertsspaceindustries.com/pledge/ships/{ship-name}
  Extract: Hero description, manufacturer lore, use cases
  Method: Scrape <meta description> or main content div
```

### 3. High-Resolution Images

**Gap:** API doesn't provide image URLs

**Solution:**
```
Source 1: RSI Media Kit
  URL: https://robertsspaceindustries.com/media/images
  Quality: Official 4K renders

Source 2: Wiki Images
  URL: https://starcitizen.tools/
  Quality: Good quality screenshots

Storage: Download to /data/ship_images/{slug}.jpg
  Optimize to 800x600, <200KB for PDFs
```

### 4. Detailed Loadouts

**Gap:** Hardpoint data is incomplete

**Solution:**
```
Source: erkul.games
  URL: https://www.erkul.games/loadout
  Method: API if available, or manual curation
  Priority: Top 50 most popular ships first
```

---

## Recommended Database Schema

Based on API analysis, we recommend this schema structure:

### Core Tables

**ships** (main table)
- All core identification fields
- All dimension fields
- All performance metrics
- Cargo and crew data
- Foreign key to manufacturers

**ship_performance** (detailed metrics)
- Afterburner specs
- Fuel consumption
- Quantum drive specs
- Agility metrics

**ship_descriptions** (multi-language)
- API technical description
- RSI marketing description
- Manufacturer lore

**ship_pricing** (external data)
- USD price (from RSI)
- aUEC price (from community sources)
- On-sale flag
- Last updated timestamp

**ship_images** (external data)
- Image URLs
- Local file paths
- Image types (hero, profile, interior)

**ship_hardpoints** (sparse, best effort)
- Hardpoint name
- Size
- Type (weapon, utility, turret)
- Default equipment

### For RAG System

**ship_embeddings**
- ship_id (foreign key)
- Combined searchable text:
  - Name + Manufacturer
  - Focus + Type
  - Technical description
  - Marketing description
  - Key specs (cargo, crew, role)
- embedding vector (1536 dimensions for OpenAI)

---

## Ship Slug Patterns

From testing, we identified these slug patterns:

**Manufacturer Prefixes (sometimes used):**
- `aegs-` (Aegis)
- `anvl-` (Anvil)
- `orig-` (Origin)
- `misc-` (MISC)

**Common Patterns:**
- Simple: `gladius`, `carrack`, `prospector`
- With number: `300i`, `400i`, `890-jump`
- Multi-word: `cutlass-black`, `vanguard-warden`
- Variant suffix: `aurora-mr`, `mustang-alpha`
- Full name: `constellation-andromeda`, `c2-hercules`

**Failed Attempts (wrong slugs):**
- ❌ `hornet` → ✅ `f7c-hornet`
- ❌ `origin-85x` → ✅ `85x`

**Recommendation:** Build a curated list of ship slugs rather than trying to guess

---

## Getting the Complete Ship List

Since `/vehicles/ships` returns HTML, we have these options:

### Option 1: Scrape the HTML Page
```python
import requests
from bs4 import BeautifulSoup

url = "https://api.star-citizen.wiki/starcitizen/vehicles/ships"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find ship links/slugs in the HTML
ship_links = soup.find_all('a', href=True)
ship_slugs = [link['href'].split('/')[-1] for link in ship_links if '/vehicles/' in link['href']]
```

### Option 2: Community APIs
- **UEX Corporation API:** `https://uexcorp.space/api/`
- **FleetYards.net API:** `https://api.fleetyards.net/v1/`
- Both provide comprehensive ship lists with slugs

### Option 3: Manual Curation (Recommended for MVP)
Start with 50-100 most popular ships:
- All starters (Aurora, Mustang, Avenger, etc.)
- Popular fighters (Gladius, Arrow, Sabre, Hornet, etc.)
- Common cargo ships (Freelancer, Cutlass, Caterpillar, etc.)
- Top exploration ships (Carrack, Constellation, 400i, etc.)
- Key mining/industrial (Prospector, MOLE, Vulture, etc.)

Can expand to full 150+ list later without architecture changes.

---

## Next Steps

1. ✅ **API Exploration** - Complete!
2. ⏭️ **Create Database Schema** - Use this mapping as reference
3. ⏭️ **Build Ship Data Collector** - Fetch from API + scrape RSI
4. ⏭️ **Set Up ETL Pipeline** - Transform and load into PostgreSQL
5. ⏭️ **Generate Embeddings** - For RAG system
6. ⏭️ **Build AI Consultant** - Use structured data for recommendations

---

## Sample Ship Data Structure (Gladius)

```json
{
  "uuid": "b6b59889-7226-458e-a6b0-1c9392128a3c",
  "name": "Gladius",
  "slug": "gladius",
  "manufacturer": "Aegis Dynamics",
  "cargo": 0,
  "crew": {"min": 1, "max": null},
  "dimensions": {"length": 21, "beam": 17.5, "height": 5.5},
  "mass": 48552,
  "speed": {"scm": 226, "max": 1193},
  "agility": {"pitch": 68, "yaw": 52, "roll": 200},
  "focus": "Light Fighter",
  "type": "combat",
  "description": "A fast, light fighter with a laser-focus on dogfighting...",
  "health": 6110,
  "shields": 3460
}
```

---

**Documentation Complete ✅**
Ready to proceed with database design and data collection!
