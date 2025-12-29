"""
Test RAG System - Demonstrates semantic ship search
Run AFTER generating embeddings with generate_embeddings.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.rag_system import (
    search_ships,
    hybrid_search,
    get_cargo_haulers,
    get_solo_ships,
    EXAMPLE_QUERIES
)


def test_semantic_search():
    """Test semantic search with example queries"""
    print("=" * 80)
    print("RAG SYSTEM TEST - Semantic Ship Search")
    print("=" * 80)
    print()

    session = SessionLocal()

    try:
        # Test each example query
        for i, query in enumerate(EXAMPLE_QUERIES[:5], 1):  # Test first 5 queries
            print(f"\n[{i}] Query: \"{query}\"")
            print("-" * 80)

            results = search_ships(session, query, top_k=3)

            if not results:
                print("   No results found")
                continue

            for j, result in enumerate(results, 1):
                print(f"\n   {j}. {result['name']} ({result['manufacturer']})")
                print(f"      Role: {result['focus']}")
                print(f"      Similarity: {result['similarity_score']:.3f}")
                print(f"      Cargo: {result['cargo_capacity']} SCU | Crew: {result['crew_min']}")
                if result['price_usd']:
                    print(f"      Price: ${result['price_usd']:.2f}")

        print("\n" + "=" * 80)

    finally:
        session.close()


def test_filtered_search():
    """Test search with filters"""
    print("\n" + "=" * 80)
    print("FILTERED SEARCH TEST")
    print("=" * 80)
    print()

    session = SessionLocal()

    try:
        # Search with budget and cargo filters
        query = "versatile ship for trading and combat"
        filters = {
            "price_max": 500,  # Under $500
            "cargo_min": 50,   # At least 50 SCU
            "crew_max": 2      # Solo or duo
        }

        print(f"Query: \"{query}\"")
        print(f"Filters: Budget < $500, Cargo >= 50 SCU, Crew <= 2")
        print("-" * 80)

        results = search_ships(session, query, top_k=5, filters=filters)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['name']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
                print(f"   Cargo: {result['cargo_capacity']} SCU | Crew: {result['crew_min']}")
                if result['price_usd']:
                    print(f"   Price: ${result['price_usd']:.2f}")
        else:
            print("No results found")

        print("\n" + "=" * 80)

    finally:
        session.close()


def test_utility_functions():
    """Test utility search functions"""
    print("\n" + "=" * 80)
    print("UTILITY FUNCTIONS TEST")
    print("=" * 80)

    session = SessionLocal()

    try:
        # Test cargo haulers
        print("\n📦 Top Cargo Haulers (>100 SCU):")
        print("-" * 80)
        haulers = get_cargo_haulers(session, min_cargo=100, limit=5)
        for i, ship in enumerate(haulers, 1):
            print(f"{i}. {ship.name}: {ship.cargo_capacity} SCU")

        # Test solo ships
        print("\n👤 Solo-Friendly Ships:")
        print("-" * 80)
        solo = get_solo_ships(session, max_crew=1, limit=5)
        for i, ship in enumerate(solo, 1):
            print(f"{i}. {ship.name} ({ship.manufacturer_name})")

        print("\n" + "=" * 80)

    finally:
        session.close()


def test_hybrid_search():
    """Test hybrid search"""
    print("\n" + "=" * 80)
    print("HYBRID SEARCH TEST")
    print("=" * 80)
    print()

    session = SessionLocal()

    try:
        query = "ship for bounty hunting with cargo space"
        results = hybrid_search(
            session,
            query=query,
            role_keywords=["Combat", "Fighter"],
            budget_max=300,
            cargo_min=20,
            top_k=3
        )

        print(f"Query: \"{query}\"")
        print("Boosting: Combat/Fighter roles")
        print("Budget: < $300, Cargo: >= 20 SCU")
        print("-" * 80)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['name']} ({result['manufacturer']})")
            print(f"   Role: {result['focus']}")
            print(f"   Score: {result['similarity_score']:.3f}")
            print(f"   Cargo: {result['cargo_capacity']} SCU")

        print("\n" + "=" * 80)

    finally:
        session.close()


if __name__ == "__main__":
    print("\n🔍 Testing RAG System...")
    print("Make sure you've run generate_embeddings.py first!\n")

    try:
        test_semantic_search()
        test_filtered_search()
        test_utility_functions()
        test_hybrid_search()

        print("\n✅ All RAG tests completed!")
        print("\nNext: Try these queries in your AI consultant:")
        for query in EXAMPLE_QUERIES[5:]:
            print(f"  - {query}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
