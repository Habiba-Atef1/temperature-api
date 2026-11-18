from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, cities


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create the tables on startup (fine for a small project, no migrations needed)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Temperature API",
    description="Store and query city temperature readings.",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(cities.router)


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok"}
