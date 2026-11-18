from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)


class CityOut(CityCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ReadingCreate(BaseModel):
    # sanity limits, nothing on earth is outside this range
    temperature: float = Field(ge=-90, le=60)
    recorded_at: datetime | None = None  # defaults to now if not sent


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city_id: int
    temperature: float
    recorded_at: datetime


class Stats(BaseModel):
    city_id: int
    count: int
    min_temp: float | None
    max_temp: float | None
    avg_temp: float | None
