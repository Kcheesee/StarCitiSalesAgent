"""
Generate embeddings for all ships in database
Uses OpenAI text-embedding-3-small model
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Ship, ShipEmbedding
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # OpenAI allows batching


def generate_search_text(ship: Ship) -> str:
    """
    Generate comprehensive searchable text from ship data
    Combines all relevant fields for semantic search
    """
    parts = []

    # Basic info
    parts.append(f"Ship Name: {ship.name}")
    if ship.manufacturer_name:
        parts.append(f"Manufacturer: {ship.manufacturer_name}")

    # Classification
    if ship.focus:
        parts.append(f"Role: {ship.focus}")
    if ship.type:
        parts.append(f"Type: {ship.type}")

    # Description (primary searchable content)
    if ship.description:
        parts.append(f"Description: {ship.description}")

    # Key specifications (for capability-based search)
    specs = []

    if ship.cargo_capacity:
        specs.append(f"{ship.cargo_capacity} SCU cargo")

    if ship.crew_min is not None:
        if ship.crew_max and ship.crew_max != ship.crew_min:
            specs.append(f"{ship.crew_min}-{ship.crew_max} crew")
        else:
            specs.append(f"{ship.crew_min} crew")

    if ship.length:
        specs.append(f"{ship.length}m length")

    if ship.speed_scm:
        specs.append(f"{ship.speed_scm} m/s SCM speed")

    if ship.speed_max:
        specs.append(f"{ship.speed_max} m/s max speed")

    if ship.shield_hp:
        specs.append(f"{ship.shield_hp} HP shields")

    if ship.quantum_range:
        specs.append(f"{ship.quantum_range} Mm quantum range")

    if specs:
        parts.append(f"Specifications: {', '.join(specs)}")

    # Marketing description if available
    if ship.marketing_description:
        parts.append(f"Marketing: {ship.marketing_description}")

    # Combine all parts
    search_text = " | ".join(parts)

    return search_text


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts using OpenAI API
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )

        # Extract embeddings from response
        embeddings = [item.embedding for item in response.data]
        return embeddings

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        raise


def run_embedding_generation():
    """Main embedding generation process"""
    print("=" * 80)
    print("EMBEDDING GENERATION - Creating Ship Embeddings")
    print("=" * 80)
    print()

    session = SessionLocal()

    try:
        # Get all ships
        ships = session.query(Ship).all()
        total_ships = len(ships)

        print(f"📊 Found {total_ships} ships in database")
        print(f"🤖 Using model: {EMBEDDING_MODEL}")
        print()

        # Clear existing embeddings
        print("🗑️  Clearing existing embeddings...")
        deleted = session.query(ShipEmbedding).delete()
        session.commit()
        print(f"   ✅ Cleared {deleted} existing embeddings\n")

        # Statistics
        stats = {
            "total": total_ships,
            "successful": 0,
            "failed": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }

        failed_ships = []

        # Process in batches
        for i in range(0, total_ships, BATCH_SIZE):
            batch_ships = ships[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_ships + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch_ships)} ships)")

            try:
                # Generate search text for each ship
                search_texts = []
                ship_data = []

                for ship in batch_ships:
                    search_text = generate_search_text(ship)
                    search_texts.append(search_text)
                    ship_data.append({
                        "ship_id": ship.id,
                        "ship_name": ship.name,
                        "search_text": search_text,
                        "text_length": len(search_text)
                    })

                # Generate embeddings via OpenAI
                embeddings = generate_embeddings_batch(search_texts)

                # Save to database
                for j, (data, embedding) in enumerate(zip(ship_data, embeddings)):
                    ship_embedding = ShipEmbedding(
                        ship_id=data["ship_id"],
                        search_text=data["search_text"],
                        embedding=embedding,  # Store as JSONB array
                        embedding_model=EMBEDDING_MODEL
                    )
                    session.add(ship_embedding)

                    # Estimate tokens (rough: ~1 token per 4 chars)
                    tokens = data["text_length"] // 4
                    stats["total_tokens"] += tokens

                    print(f"   [{i+j+1}/{total_ships}] {data['ship_name']:<30} ✅ ({data['text_length']} chars)")

                session.commit()
                stats["successful"] += len(batch_ships)
                print(f"   💾 Batch committed\n")

            except Exception as e:
                print(f"   ❌ Batch failed: {e}\n")
                stats["failed"] += len(batch_ships)
                for ship in batch_ships:
                    failed_ships.append({"name": ship.name, "error": str(e)})
                session.rollback()

        # Calculate costs
        # text-embedding-3-small: $0.020 per 1M tokens
        stats["estimated_cost"] = (stats["total_tokens"] / 1_000_000) * 0.020

        # Summary
        print("\n" + "=" * 80)
        print("EMBEDDING GENERATION COMPLETE")
        print("=" * 80)
        print(f"\n✅ Successfully embedded: {stats['successful']} ships")
        print(f"❌ Failed: {stats['failed']} ships")
        print(f"📊 Total tokens: {stats['total_tokens']:,}")
        print(f"💰 Estimated cost: ${stats['estimated_cost']:.4f}")

        if failed_ships:
            print("\nFailed ships:")
            for ship in failed_ships:
                print(f"  - {ship['name']}: {ship['error']}")

        # Validation
        print("\n" + "=" * 80)
        print("DATABASE VALIDATION")
        print("=" * 80)

        embedding_count = session.query(ShipEmbedding).count()
        ship_count = session.query(Ship).count()

        print(f"\nShips in database: {ship_count}")
        print(f"Embeddings in database: {embedding_count}")

        coverage = (embedding_count / ship_count * 100) if ship_count > 0 else 0
        print(f"Coverage: {coverage:.1f}%")

        # Sample embedding
        sample = session.query(ShipEmbedding).first()
        if sample:
            embedding_dim = len(sample.embedding) if isinstance(sample.embedding, list) else 0
            print(f"\nEmbedding dimensions: {embedding_dim}")
            print(f"Sample ship: {sample.ship.name if sample.ship else 'N/A'}")
            print(f"Search text preview: {sample.search_text[:200]}...")

        print("\n✨ Embedding Generation Complete!")
        print(f"🔍 {embedding_count} ships ready for semantic search!")

        return stats

    except Exception as e:
        print(f"\n❌ Embedding Generation Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        print("Please add OPENAI_API_KEY to /backend/.env file")
        sys.exit(1)

    try:
        results = run_embedding_generation()
        print(f"\n{'='*80}")
        print("✅ SUCCESS - Embeddings ready for RAG!")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ FAILED: {e}")
        print(f"{'='*80}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
