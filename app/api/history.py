from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timezone
from app.db import get_db
from app.models import SearchLog
from typing import Optional

router = APIRouter()


@router.get("/history")
async def get_history(
    limit: int = Query(100, ge=1, le=500),
    type: Optional[str] = Query( None, description="movie, series, anime"),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(SearchLog).order_by(SearchLog.timestamp.desc()).limit(limit)

    if type:
        stmt = stmt.where(SearchLog.type == type)

    result = await session.execute(stmt)
    logs = result.scalars().all()

    return [
        {
            "title": log.title,
            "type": log.type,
            "timestamp": log.timestamp.replace(tzinfo=timezone.utc).isoformat(),
            "source": log.source,
            "source_id": log.source_id
        }
        for log in logs
    ]
