"""
RAG (Retrieval Augmented Generation) System
Semantic search over ship embeddings for AI consultant
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import os
from dotenv import load_dotenv
from openai import OpenAI

from ..models import Ship, ShipEmbedding, Manufacturer

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    Returns value between -1 and 1 (1 = identical, 0 = orthogonal, -1 = opposite)
    """
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)

    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def embed_query(query: str) -> List[float]:
    """
    Embed a user query using OpenAI API
    Returns embedding vector
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query
        )
        return response.data[0].embedding

    except Exception as e:
        print(f"❌ Error embedding query: {e}")
        raise


def search_ships(
    db: Session,
    query: str,
    top_k: int = 10,
    min_similarity: float = 0.0,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Semantic search for ships using RAG

    Args:
        db: Database session
        query: Natural language query (e.g., "fast combat ship with cargo")
        top_k: Number of results to return
        min_similarity: Minimum cosine similarity threshold (0-1)
        filters: Optional filters dict:
            - price_max: Maximum USD price
            - price_min: Minimum USD price
            - cargo_min: Minimum cargo capacity (SCU)
            - crew_max: Maximum crew required
            - manufacturer: Manufacturer name
            - focus: Ship focus/role
            - type: Ship type

    Returns:
        List of ship dictionaries with similarity scores
    """

    # Embed the query
    query_embedding = embed_query(query)

    # Build base query with filters
    ship_query = db.query(Ship, ShipEmbedding).join(
        ShipEmbedding,
        Ship.id == ShipEmbedding.ship_id
    )

    # Apply filters if provided
    if filters:
        conditions = []

        if "price_max" in filters and filters["price_max"] is not None:
            conditions.append(Ship.price_usd <= filters["price_max"])

        if "price_min" in filters and filters["price_min"] is not None:
            conditions.append(Ship.price_usd >= filters["price_min"])

        if "cargo_min" in filters and filters["cargo_min"] is not None:
            conditions.append(Ship.cargo_capacity >= filters["cargo_min"])

        if "crew_max" in filters and filters["crew_max"] is not None:
            conditions.append(Ship.crew_min <= filters["crew_max"])

        if "manufacturer" in filters and filters["manufacturer"]:
            conditions.append(Ship.manufacturer_name.ilike(f"%{filters['manufacturer']}%"))

        if "focus" in filters and filters["focus"]:
            conditions.append(Ship.focus.ilike(f"%{filters['focus']}%"))

        if "type" in filters and filters["type"]:
            conditions.append(Ship.type.ilike(f"%{filters['type']}%"))

        if conditions:
            ship_query = ship_query.filter(and_(*conditions))

    # Get all ships with embeddings (after filtering)
    results = ship_query.all()

    # Calculate similarities
    ship_scores = []
    for ship, embedding in results:
        similarity = cosine_similarity(query_embedding, embedding.embedding)

        # Apply similarity threshold
        if similarity >= min_similarity:
            ship_scores.append({
                "ship": ship,
                "similarity": similarity,
                "search_text": embedding.search_text
            })

    # Sort by similarity (highest first)
    ship_scores.sort(key=lambda x: x["similarity"], reverse=True)

    # Return top K results with formatted data
    top_results = []
    for item in ship_scores[:top_k]:
        ship = item["ship"]

        result = {
            # Core info
            "id": ship.id,
            "uuid": ship.uuid,
            "name": ship.name,
            "slug": ship.slug,

            # Classification
            "manufacturer": ship.manufacturer_name,
            "focus": ship.focus,
            "type": ship.type,

            # Key specs
            "cargo_capacity": ship.cargo_capacity,
            "crew_min": ship.crew_min,
            "crew_max": ship.crew_max,
            "length": float(ship.length) if ship.length else None,
            "speed_scm": ship.speed_scm,
            "speed_max": ship.speed_max,

            # Pricing
            "price_usd": float(ship.price_usd) if ship.price_usd else None,
            "price_auec": ship.price_auec,

            # Descriptions
            "description": ship.description,
            "marketing_description": ship.marketing_description,

            # Search metadata
            "similarity_score": round(item["similarity"], 4),
            "search_text": item["search_text"],

            # Images
            "image_url": ship.image_url,
            "store_url": ship.store_url,
        }

        top_results.append(result)

    return top_results


def get_ships_by_role(db: Session, role: str, limit: int = 10) -> List[Ship]:
    """
    Get ships by specific role/focus (non-semantic search)

    Args:
        db: Database session
        role: Ship role (Combat, Exploration, Trading, etc.)
        limit: Maximum results

    Returns:
        List of Ship objects
    """
    return (
        db.query(Ship)
        .filter(Ship.focus.ilike(f"%{role}%"))
        .limit(limit)
        .all()
    )


def get_ships_by_manufacturer(db: Session, manufacturer: str, limit: int = 20) -> List[Ship]:
    """
    Get ships by manufacturer name

    Args:
        db: Database session
        manufacturer: Manufacturer name (partial match)
        limit: Maximum results

    Returns:
        List of Ship objects
    """
    return (
        db.query(Ship)
        .filter(Ship.manufacturer_name.ilike(f"%{manufacturer}%"))
        .order_by(Ship.name)
        .limit(limit)
        .all()
    )


def get_ships_in_budget(
    db: Session,
    max_price_usd: float,
    min_price_usd: Optional[float] = None,
    limit: int = 20
) -> List[Ship]:
    """
    Get ships within a price range

    Args:
        db: Database session
        max_price_usd: Maximum USD price
        min_price_usd: Minimum USD price (optional)
        limit: Maximum results

    Returns:
        List of Ship objects sorted by price
    """
    query = db.query(Ship).filter(Ship.price_usd <= max_price_usd)

    if min_price_usd is not None:
        query = query.filter(Ship.price_usd >= min_price_usd)

    return query.order_by(Ship.price_usd).limit(limit).all()


def get_cargo_haulers(db: Session, min_cargo: int = 100, limit: int = 10) -> List[Ship]:
    """
    Get ships optimized for cargo hauling

    Args:
        db: Database session
        min_cargo: Minimum cargo capacity in SCU
        limit: Maximum results

    Returns:
        List of Ship objects sorted by cargo capacity (descending)
    """
    return (
        db.query(Ship)
        .filter(Ship.cargo_capacity >= min_cargo)
        .order_by(Ship.cargo_capacity.desc())
        .limit(limit)
        .all()
    )


def get_solo_ships(db: Session, max_crew: int = 1, limit: int = 20) -> List[Ship]:
    """
    Get ships suitable for solo players

    Args:
        db: Database session
        max_crew: Maximum crew requirement
        limit: Maximum results

    Returns:
        List of Ship objects
    """
    return (
        db.query(Ship)
        .filter(Ship.crew_min <= max_crew)
        .order_by(Ship.name)
        .limit(limit)
        .all()
    )


def hybrid_search(
    db: Session,
    query: str,
    role_keywords: Optional[List[str]] = None,
    budget_max: Optional[float] = None,
    cargo_min: Optional[int] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Hybrid search combining semantic search with structured filters
    Useful for complex queries like:
    "affordable combat ship that can also haul cargo"

    Args:
        db: Database session
        query: Natural language query
        role_keywords: List of role keywords to boost (e.g., ["Combat", "Fighter"])
        budget_max: Maximum budget in USD
        cargo_min: Minimum cargo capacity
        top_k: Number of results

    Returns:
        List of ship results with scores
    """

    # Build filters
    filters = {}
    if budget_max:
        filters["price_max"] = budget_max
    if cargo_min:
        filters["cargo_min"] = cargo_min

    # Semantic search with filters
    results = search_ships(db, query, top_k=top_k * 2, filters=filters)

    # Boost ships matching role keywords
    if role_keywords:
        for result in results:
            for keyword in role_keywords:
                if result["focus"] and keyword.lower() in result["focus"].lower():
                    result["similarity_score"] += 0.1  # Boost score

        # Re-sort after boosting
        results.sort(key=lambda x: x["similarity_score"], reverse=True)

    return results[:top_k]


# Example queries for testing
EXAMPLE_QUERIES = [
    "fast fighter ship for dogfighting",
    "large cargo hauler for trading",
    "exploration ship with long range",
    "small solo ship for beginners",
    "luxury ship with lots of amenities",
    "capital ship for group gameplay",
    "stealth ship for infiltration",
    "mining ship for resource gathering",
    "medical ship for rescue missions",
    "versatile multi-role ship",
]
