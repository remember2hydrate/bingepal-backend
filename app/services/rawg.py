# games handler

from app.utils.logger import logger
import os
import httpx
from dotenv import load_dotenv
from app.models import SearchResult

load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")
BASE_URL = "https://api.rawg.io/api/games"


async def search(query: str) -> list[SearchResult]:
    logger.info(f"[RAWG] Searching '{query}'")

    params = {
        "key": API_KEY,
        "search": query,
        "page_size": 10
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[RAWG] API error: {e}")
        return []

    results = []
    for item in data.get("results", []):
        genres = [g["name"] for g in item.get("genres", [])]
        platforms = [p["platform"]["name"] for p in item.get("platforms", [])]
        results.append(SearchResult(
            id=str(item["id"]),
            title=item.get("name"),
            type="game",
            description=None,
            poster_url=item.get("background_image"),
            year=(item.get("released") or "")[:4],
            source="rawg",
            genres=genres + platforms,
            rating=item.get("rating"),
            rating_count=item.get("ratings_count"),
            total_seasons=None,
            total_episodes=None,
            average_duration= item.get("playtime") * 60 if item.get("playtime") else None 
        ))

    return results


async def get_detail(id: str) -> SearchResult:
    logger.info(f"[RAWG] Fetching detail for game ID: {id}")

    url = f"https://api.rawg.io/api/games/{id}"
    params = {"key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[RAWG] API error: {e}")
        raise

    return SearchResult(
        id=str(data["id"]),
        title=data.get("name"),
        type="game",
        description=data.get("description_raw") or "No description.",
        poster_url=data.get("background_image"),
        year=(data.get("released") or "")[:4],
        source="rawg",
        genres=[g["name"] for g in data.get("genres", [])] + [p["platform"]["name"] for p in data.get("platforms", [])],
        rating=data.get("rating"),
        rating_count=data.get("ratings_count"),
        total_seasons=None,
        total_episodes=None,
        average_duration=(data.get("playtime") or 0) * 60
    )
