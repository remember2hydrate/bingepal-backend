import os

from slowapi import _rate_limit_exceeded_handler
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import Base, engine
from app.utils.limiter import limiter

from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.search import router as search_router
from app.api.detail import router as detail_router
from app.api.chapter import router as chapter_router
from app.api.trending import router as trending_router
from app.api.history import router as history_router
from app.api.log import router as log_router
from app.api.devlogs import router as devlog_router

from fastapi.exceptions import RequestValidationError
from app.utils.logger import logger 

logger.info("Backend started and logger initialized.")

app = FastAPI(
    title="BingePal API",
    description="API for movies, anime, tv series, games, manga and books",
    version="0.1.0"
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# https://www.youtube.com/watch?v=lFTNS_QStTs
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    # Later sth like allow_origins=["https://admin.bingepal.com", "https://app.bingepal.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

app.include_router(search_router, prefix="/api")
app.include_router(detail_router, prefix="/api")
app.include_router(chapter_router, prefix="/api")
app.include_router(trending_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(log_router, prefix="/api")
app.include_router(devlog_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "BingePal API is alive"}

# DB startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

