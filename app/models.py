from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Enum, Text, TIMESTAMP, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import enum
import datetime
import os
# from app.db import Base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)
Base = declarative_base()


class SearchResult(BaseModel):
    id: str
    title: str
    type: str  # movie, series, anime, game, book, manga
    description: Optional[str]
    poster_url: Optional[str]
    year: Optional[int]
    source: str

    # Optional enhancements
    genres: Optional[List[str]] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    total_seasons: Optional[int] = None
    total_episodes: Optional[int] = None
    average_duration: Optional[int] = None


class UserRole(enum.Enum):
    admin = "admin"
    mod = "mod"
    pal = "pal"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    name = Column(String)
    mail = Column(String, unique=True, nullable=True)
    status = Column(Enum(UserRole), default=UserRole.pal)
    # Optional JSON fields or structured watch time stats


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    username = Column(String, ForeignKey("users.username"))
    rate_score = Column(Float, nullable=False)
    rate_descr = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class ChapterOut(BaseModel):
    season: Optional[int] = None  # only for series/anime
    number: int
    title: str
    air_date: Optional[str] = None


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)
    source_id = Column(String, nullable=False)
    type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now(), index=True)


class LogEntry(BaseModel):
    source: str
    source_id: str
    type: str
    title: str
