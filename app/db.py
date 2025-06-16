import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import Depends
from app.utils.logger import logger  

DATABASE_URL = "postgresql+asyncpg://postgresql_bingepal_db_user:2WYQGIX7VEfka46ETQujHDuZtEVzSWJd@dpg-d0do94juibrs73d0e9m0-a.oregon-postgres.render.com/postgresql_bingepal_db"

try:
    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    Base = declarative_base()
    logger.info("Database engine initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize DB engine: {e}")
    raise

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session