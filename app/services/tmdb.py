# movie + series handler

import os
import httpx
from app.utils.logger import logger
from dotenv import load_dotenv
from app.models import SearchResult
from app.models import ChapterOut

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search"


async def search(query: str, type: str) -> list[SearchResult]:
    endpoint = "movie" if type == "movie" else "tv"
    url = f"{BASE_URL}/{endpoint}"
    params = {"api_key": API_KEY, "query": query}

    logger.info(f"[TMDb] Searching '{query}' as type '{type}'")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[TMDb] API error: {e}")
        return []

    results = []
    for item in data.get("results", [])[:10]:
        year_raw = item.get("release_date") or item.get("first_air_date")
        # year = int(year_raw[:4]) if year_raw else None
        genres = [str(g) for g in item.get("genre_ids", [])]
        results.append(SearchResult(
            id=str(item["id"]),
            title=item.get("title") or item.get("name") or "Unknown Title",
            type=type,
            description=item.get("overview") or "No description available.",
            poster_url= f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else None,
            year= int((item.get("release_date") or item.get("first_air_date") or "")[:4]) if (item.get("release_date") or item.get("first_air_date") or "")[:4].isdigit() else None,
            source="tmdb",
            genres=genres,
            rating=item.get("vote_average"),
            rating_count=item.get("vote_count"),
            total_seasons=None,
            total_episodes=None,
            average_duration=None
        ))
    return results


async def get_detail(id: str, type: str) -> SearchResult:
    logger.info(f"[TMDb] Fetching detail for {type} with ID: {id}")

    endpoint = "movie" if type == "movie" else "tv"
    url = f"https://api.themoviedb.org/3/{endpoint}/{id}"
    params = {"api_key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[TMDb] Detail API error: {e}")
        raise

    return SearchResult(
        id=str(data["id"]),
        title=data.get("title") or data.get("name"),
        type=type,
        description=data.get("overview") or "No description available.",
        poster_url= f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None,
        year=(data.get("release_date") or data.get("first_air_date") or "")[:4],
        source="tmdb",
        genres=[g["name"] for g in data.get("genres", [])],
        rating=data.get("vote_average"),
        rating_count=data.get("vote_count"),
        total_seasons= data.get("number_of_seasons") if type == "series" else None,
        total_episodes= data.get("number_of_episodes") if type == "series" else None,
        average_duration=( data.get("runtime") or (data.get("episode_run_time") or [None])[0])
    )


async def get_episodes(id: str) -> list[ChapterOut]:
    url = f"https://api.themoviedb.org/3/tv/{id}"
    params = {"api_key": API_KEY}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
    except Exception as e:
        logger.error(f"[TMDb] Episode fetch failed: {e}")
        return []

    chapters = []
    for season in data.get("seasons", []):
        season_num = season["season_number"]
        try:
            season_url = f"{url}/season/{season_num}"
            season_resp = await client.get(season_url, params=params)
            season_data = season_resp.json()

            for ep in season_data.get("episodes", []):
                chapters.append(ChapterOut(
                    season=season_num,
                    number=ep["episode_number"],
                    title=ep["name"],
                    air_date=ep.get("air_date")
                ))
        except Exception as e:
            logger.error(f"[TMDb] Season fetch failed: {e}")
            continue

    return chapters
