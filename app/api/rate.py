from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.models import SessionLocal, Rating
from pydantic import BaseModel
from typing import Optional, List
import datetime
from sqlalchemy import and_
from fastapi import status
from app.utils.request_log import log_request

router = APIRouter()


class RatingIn(BaseModel):
    source: str
    source_id: str
    username: str
    rate_score: float
    rate_descr: Optional[str]


class RatingOut(RatingIn):
    timestamp: datetime.datetime


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/rate", response_model=RatingOut)
async def add_or_update_rating(payload: RatingIn, db=Depends(get_db)):
    await log_request()
    
    query = select(Rating).where(
        Rating.username == payload.username,
        Rating.source == payload.source,
        Rating.source_id == payload.source_id
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.rate_score = payload.rate_score
        existing.rate_descr = payload.rate_descr
        existing.timestamp = datetime.datetime.utcnow()
    else:
        new_rating = Rating(**payload.dict())
        db.add(new_rating)

    await db.commit()
    return payload


@router.get("/rate", response_model=List[RatingOut])
async def get_ratings(source: str, source_id: str, db=Depends(get_db)):
    query = select(Rating).where(
        and_(
            Rating.source == source,
            Rating.source_id == source_id
        )
    )
    result = await db.execute(query)
    ratings = result.scalars().all()
    return ratings


@router.delete("/rate", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    source: str, 
    source_id: str, 
    username: str, 
    db=Depends(get_db)
):
    query = select(Rating).where(
        and_(
            Rating.source == source,
            Rating.source_id == source_id,
            Rating.username == username
        )
    )
    result = await db.execute(query)
    rating = result.scalar_one_or_none()

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    await db.delete(rating)
    await db.commit()
    return
