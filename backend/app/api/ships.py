"""
Ships API Routes
Provides ship search endpoints for ElevenLabs agent custom tools
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.rag_system import search_ships, get_ships_in_budget, get_ships_by_manufacturer

router = APIRouter(prefix="/api/ships", tags=["ships"])


class ShipSearchResponse(BaseModel):
    """Response model for ship search"""
    total_results: int
    ships: List[dict]


@router.get("/search", response_model=ShipSearchResponse)
def search_ships_endpoint(
    query: str = Query(..., description="Natural language search query (e.g., 'fast combat ship')"),
    budget_max: Optional[float] = Query(None, description="Maximum budget in USD"),
    budget_min: Optional[float] = Query(None, description="Minimum budget in USD"),
    cargo_min: Optional[int] = Query(None, description="Minimum cargo capacity in SCU"),
    crew_max: Optional[int] = Query(None, description="Maximum crew requirement (for solo players)"),
    manufacturer: Optional[str] = Query(None, description="Manufacturer name (partial match)"),
    top_k: int = Query(5, ge=1, le=10, description="Number of results to return (1-10)"),
    db: Session = Depends(get_db)
):
    """
    Search for Star Citizen ships using natural language queries with optional filters.

    This endpoint uses semantic search (RAG) to find ships matching the query,
    combined with structured filters for price, cargo, crew, etc.

    **Example queries:**
    - "fast combat ship for dogfighting"
    - "cargo hauler with defensive weapons"
    - "solo-friendly exploration ship"
    - "affordable starter ship for beginners"
    - "mining ship with good cargo capacity"

    **Filters help narrow down results:**
    - budget_max: Only show ships under this price (USD)
    - budget_min: Only show ships over this price (USD)
    - cargo_min: Only show ships with at least this much cargo (SCU)
    - crew_max: Only show ships needing this many crew or less (1 = solo)
    - manufacturer: Filter by manufacturer name (e.g., "Anvil", "Drake")

    **Returns:**
    - List of ships with full details including specs, pricing, descriptions
    - Ships are ranked by semantic similarity to the query
    - Each ship includes a similarity score (0-1, higher is better match)
    """

    try:
        # Build filters dictionary
        filters = {}
        if budget_max is not None:
            filters["price_max"] = budget_max
        if budget_min is not None:
            filters["price_min"] = budget_min
        if cargo_min is not None:
            filters["cargo_min"] = cargo_min
        if crew_max is not None:
            filters["crew_max"] = crew_max
        if manufacturer:
            filters["manufacturer"] = manufacturer

        # Perform semantic search
        results = search_ships(
            db=db,
            query=query,
            top_k=top_k,
            filters=filters if filters else None
        )

        # Format results for ElevenLabs agent
        formatted_ships = []
        for ship in results:
            formatted_ship = {
                # Basic info
                "name": ship["name"],
                "manufacturer": ship["manufacturer"],
                "role": ship["focus"],
                "type": ship["type"],

                # Key specs
                "cargo_capacity": ship["cargo_capacity"],
                "crew_requirement": f"{ship['crew_min']}-{ship['crew_max']}",
                "length_meters": ship["length"],
                "max_speed": ship["speed_max"],

                # Pricing
                "price_usd": ship["price_usd"],
                "price_auec": ship["price_auec"],

                # Descriptions
                "description": ship["description"],
                "marketing_pitch": ship["marketing_description"],

                # Search metadata
                "match_score": ship["similarity_score"],

                # Links
                "store_url": ship["store_url"],
            }
            formatted_ships.append(formatted_ship)

        return ShipSearchResponse(
            total_results=len(formatted_ships),
            ships=formatted_ships
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ship search failed: {str(e)}")


@router.get("/budget")
def get_ships_by_budget(
    max_price: float = Query(..., description="Maximum price in USD"),
    min_price: Optional[float] = Query(None, description="Minimum price in USD"),
    limit: int = Query(10, ge=1, le=20, description="Number of results"),
    db: Session = Depends(get_db)
):
    """
    Get ships within a specific budget range.

    **Example:**
    - max_price=100, min_price=45 → Starter ships ($45-$100)
    - max_price=200 → Ships under $200
    """
    try:
        ships = get_ships_in_budget(
            db=db,
            max_price_usd=max_price,
            min_price_usd=min_price,
            limit=limit
        )

        return {
            "total": len(ships),
            "budget_range": {
                "min": min_price or 0,
                "max": max_price
            },
            "ships": [
                {
                    "name": s.name,
                    "manufacturer": s.manufacturer_name,
                    "price_usd": float(s.price_usd) if s.price_usd else None,
                    "role": s.focus,
                    "cargo": s.cargo_capacity,
                }
                for s in ships
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Budget search failed: {str(e)}")


@router.get("/manufacturer/{manufacturer_name}")
def get_ships_by_manufacturer_endpoint(
    manufacturer_name: str,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get all ships from a specific manufacturer.

    **Examples:**
    - "Anvil" → Anvil ships
    - "Drake" → Drake Interplanetary ships
    - "RSI" → Roberts Space Industries ships
    """
    try:
        ships = get_ships_by_manufacturer(
            db=db,
            manufacturer=manufacturer_name,
            limit=limit
        )

        return {
            "manufacturer": manufacturer_name,
            "total": len(ships),
            "ships": [
                {
                    "name": s.name,
                    "price_usd": float(s.price_usd) if s.price_usd else None,
                    "role": s.focus,
                    "cargo": s.cargo_capacity,
                    "crew": f"{s.crew_min}-{s.crew_max}",
                }
                for s in ships
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manufacturer search failed: {str(e)}")
