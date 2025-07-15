from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import SearchLog
from app.models import LogEntry

router = APIRouter()


@router.post("/log", status_code=status.HTTP_204_NO_CONTENT)
async def log_entry(entry: LogEntry, db: AsyncSession = Depends(get_db)):
    log = SearchLog(**entry.dict())
    db.add(log)
    await db.commit()
