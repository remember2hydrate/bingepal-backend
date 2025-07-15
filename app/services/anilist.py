import httpx
from app.models import SearchResult
from app.utils.logger import logger
from app.models import ChapterOut

API_URL = "https://graphql.anilist.co"

search_query = """
query ($search: String) {
  Page(perPage: 10) {
    media(search: $search, type: ANIME) {
      id
      title {
        romaji
        english
      }
      description(asHtml: false)
      coverImage {
        large
      }
      startDate {
        year
      }
      episodes
      duration
      genres
      averageScore
    }
  }
}
"""

detail_query = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    id
    title {
      romaji
      english
    }
    description(asHtml: false)
    coverImage {
      large
    }
    startDate {
      year
    }
    episodes
    duration
    genres
    averageScore
  }
}
"""


async def search(query: str) -> list[SearchResult]:
    logger.info(f"[AniList] Searching '{query}'")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={
                "query": search_query,
                "variables": {"search": query}
            })
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[AniList] API error: {e}")
        return []

    results = []
    for item in data["data"]["Page"]["media"]:
        results.append(SearchResult(
          id=str(item["id"]),
          title=item["title"]["english"] or item["title"]["romaji"],
          type="anime",
          description=item["description"],
          poster_url=item["coverImage"]["large"],
          year=item["startDate"]["year"],
          source="anilist",
          genres=item.get("genres"),
          rating=(item.get("averageScore") or 0) / 10,  # scale to 10
          rating_count=None,  # Not available in AniList search
          total_episodes=item.get("episodes"),
          average_duration=item.get("duration"),
          total_seasons=None
      )
    )

    return results


async def get_detail(id: str) -> SearchResult:
    logger.info(f"[AniList] Fetching detail for anime ID: {id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={
                "query": detail_query,
                "variables": {"id": int(id)}
            })
            response.raise_for_status()
            data = response.json()["data"]["Media"]
    except Exception as e:
        logger.error(f"[AniList] API error: {e}")
        raise

    return SearchResult(
        id=str(data["id"]),
        title=data["title"]["english"] or data["title"]["romaji"],
        type="anime",
        description=data.get("description"),
        poster_url=data["coverImage"]["large"],
        year=data["startDate"]["year"],
        source="anilist",
        genres=data.get("genres"),
        rating=(data.get("averageScore") or 0) / 10,
        rating_count=None,
        total_seasons=None,
        total_episodes=data.get("episodes"),
        average_duration=data.get("duration")
    )


async def get_episodes(id: str) -> list[ChapterOut]:
    logger.info(f"[Jikan] Fetching episodes for anime ID: {id}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.jikan.moe/v4/anime/{id}/episodes")
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"[Jikan] API error for anime {id}: {e}")
        return []

    chapters = []
    for ep in data.get("data", []):
        chapters.append(ChapterOut(
            season=None,
            number=ep["mal_id"],
            title=ep.get("title") or f"Episode {ep['mal_id']}",
            air_date = 
              ep["aired"]
              if "aired" in ep and isinstance(ep["aired"], str)
              else None
        ))

    logger.info(f"[Jikan] Found {len(chapters)} episodes for anime {id}")
    return chapters
