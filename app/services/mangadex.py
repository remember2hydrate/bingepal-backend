# manga handler

import httpx
from app.models import SearchResult
from app.utils.logger import logger
from app.models import ChapterOut

BASE_URL = "https://api.mangadex.org"


async def search(query: str) -> list[SearchResult]:
    logger.info(f"[MangaDex] Searching '{query}'")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/manga", params={
                "title": query,
                "limit": 10,
                "includes[]": "cover_art"
            })
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[MangaDex] API error: {e}")
        return []

    results = []
    for item in data.get("data", []):
        attr = item["attributes"]
        title = attr["title"].get("en") or list(attr["title"].values())[0]
        description = attr.get("description", {}).get("en") or "No description."
        genres = [
            t["attributes"]["name"].get("en") 
            for t in attr.get("tags", []) 
            if "attributes" in t]

        # Find cover filename
        cover = None
        for rel in item["relationships"]:
            if rel["type"] == "cover_art":
                cover = rel["attributes"].get("fileName")

        poster_url = f"https://uploads.mangadex.org/covers/{item['id']}/{cover}" if cover else None

        results.append(SearchResult(
            id=item["id"],
            title=title,
            type="manga",
            description=description,
            poster_url=poster_url,
            year=None,  # MangaDex does not give publish year in search
            source="mangadex",
            genres=genres or None,
            rating=None,
            rating_count=None,
            total_seasons=None,
            total_episodes=None,
            average_duration=None
        ))

    return results


async def get_detail(id: str) -> SearchResult:
    logger.info(f"[MangaDex] Fetching detail for manga ID: {id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.mangadex.org/manga/{id}", params={"includes[]": "cover_art"})
            response.raise_for_status()
            data = response.json()["data"]
    except Exception as e:
        logger.error(f"[MangaDex] API error: {e}")
        raise

    attr = data["attributes"]
    title = attr["title"].get("en") or list(attr["title"].values())[0]
    description = attr.get("description", {}).get("en") or "No description."
    genres = [t["attributes"]["name"]["en"] for t in attr.get("tags", [])]

    cover = None
    for rel in data["relationships"]:
        if rel["type"] == "cover_art":
            cover = rel["attributes"].get("fileName")

    poster_url = f"https://uploads.mangadex.org/covers/{data['id']}/{cover}" if cover else None

    return SearchResult(
        id=id,
        title=title,
        type="manga",
        description=description,
        poster_url=poster_url,
        year=None,
        source="mangadex",
        genres=genres,
        rating=None,
        rating_count=None,
        total_seasons=None,
        total_episodes=None,
        average_duration=None
    )


async def get_chapters(id: str) -> list[ChapterOut]:
    url = "https://api.mangadex.org/chapter"
    params = {
        "manga": id,
        "translatedLanguage[]": "en",
        "limit": 100,
        "order[chapter]": "asc"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[MangaDex] Chapter fetch failed: {e}")
        return []

    chapters = []
    for ch in data.get("data", []):
        attr = ch["attributes"]
        chapters.append(ChapterOut(
            season=None,
            number= int(attr["chapter"]) if attr.get("chapter", "").isdigit() else 0,
            title=attr.get("title") or "Untitled",
            air_date=attr.get("publishAt")
        ))

    return chapters
