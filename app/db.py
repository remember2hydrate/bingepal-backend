import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.utils.logger import logger

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    Base = declarative_base()
    logger.info("==========================================")
    logger.info("Database engine initialized successfully.")
    logger.info("------------------------------------------")
except Exception as e:
    logger.error(f"Failed to initialize DB engine: {e}")
    raise


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
