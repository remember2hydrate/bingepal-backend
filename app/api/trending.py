from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta

from app.db import get_db
from app.models import SearchLog

router = APIRouter()


@router.get("/trending")
async def get_trending(
    type: str = Query(
        ..., 
        description="Type of media (e.g., movie, series, anime)"
    ),
    days: int = Query(
        7, 
        description="Time range in days. Use 0 for all time."
    ),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(SearchLog.title, func.count().label("count")).where(SearchLog.type == type)

    if days > 0:
        since = datetime.utcnow() - timedelta(days=days)
        stmt = stmt.where(SearchLog.timestamp >= since)

    stmt = stmt.group_by(SearchLog.title).order_by(func.count().desc()).limit(10)
    result = await session.execute(stmt)

    trending = [{"title": row[0], "count": row[1]} for row in result.all()]
    return {"type": type, "days": days, "trending": trending}
