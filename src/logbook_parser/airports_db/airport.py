from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


def default_date() -> datetime:
    return datetime(year=1900, month=1, day=1).astimezone(tz=timezone.utc)


@dataclass
class Airport:
    iata: str
    icao: str
    name: str
    city: str
    subd: str
    country: str
    elevation: int
    lat: str
    lon: str
    tz: str
    uuid: UUID = field(default_factory=uuid4)
    valid_from: datetime = field(default_factory=default_date)
