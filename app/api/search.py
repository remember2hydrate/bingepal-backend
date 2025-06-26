# Route handler

from fastapi import APIRouter, Query, HTTPException, Request
from app.models import SearchResult
from app.services import tmdb, anilist, rawg, mangadex, openlibrary
from app.utils.limiter import limiter
from app.utils.request_log import log_request

router = APIRouter()


@router.get("/search", response_model=list[SearchResult])
@limiter.limit("10/minute")
async def search(
    request: Request, 
    query: str = Query(...), 
    type: str = Query(...)
):
    type = type.lower()
    await log_request(request)

    if type == "movie" or type == "series":
        return await tmdb.search(query, type)
    elif type == "anime":
        return await anilist.search(query)
    elif type == "game":
        return await rawg.search(query)
    elif type == "manga":
        return await mangadex.search(query)
    elif type == "book":
        return await openlibrary.search(query)
    else:
        raise HTTPException(status_code=400, detail="Invalid media type")
