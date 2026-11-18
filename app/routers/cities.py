from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.auth import get_current_user
from app.database import get_db
from app.models import City, Reading

router = APIRouter(prefix="/cities", tags=["cities"])


async def get_city_or_404(city_id: int, db: AsyncSession) -> City:
    city = await db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.get("", response_model=list[schemas.CityOut])
async def list_cities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(City).order_by(City.name))
    return result.scalars().all()


@router.post(
    "",
    response_model=schemas.CityOut,
    status_code=201,
    dependencies=[Depends(get_current_user)],  # needs a valid token
)
async def create_city(data: schemas.CityCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(City).where(City.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="City already exists")

    city = City(name=data.name, country=data.country)
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return city


@router.post(
    "/{city_id}/readings",
    response_model=schemas.ReadingOut,
    status_code=201,
    dependencies=[Depends(get_current_user)],
)
async def add_reading(
    city_id: int, data: schemas.ReadingCreate, db: AsyncSession = Depends(get_db)
):
    await get_city_or_404(city_id, db)

    reading = Reading(
        city_id=city_id,
        temperature=data.temperature,
        recorded_at=data.recorded_at or datetime.utcnow(),
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading


@router.get("/{city_id}/readings", response_model=list[schemas.ReadingOut])
async def list_readings(
    city_id: int,
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
):
    await get_city_or_404(city_id, db)

    query = select(Reading).where(Reading.city_id == city_id)
    if date_from:
        query = query.where(Reading.recorded_at >= date_from)
    if date_to:
        query = query.where(Reading.recorded_at <= date_to)

    result = await db.execute(query.order_by(Reading.recorded_at))
    return result.scalars().all()


@router.get("/{city_id}/stats", response_model=schemas.Stats)
async def city_stats(city_id: int, db: AsyncSession = Depends(get_db)):
    await get_city_or_404(city_id, db)

    result = await db.execute(
        select(
            func.count(Reading.id),
            func.min(Reading.temperature),
            func.max(Reading.temperature),
            func.avg(Reading.temperature),
        ).where(Reading.city_id == city_id)
    )
    count, min_t, max_t, avg_t = result.one()

    return schemas.Stats(
        city_id=city_id,
        count=count,
        min_temp=min_t,
        max_temp=max_t,
        avg_temp=round(avg_t, 2) if avg_t is not None else None,
    )
