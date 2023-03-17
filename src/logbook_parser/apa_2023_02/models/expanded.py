from datetime import date, datetime, timedelta
from operator import attrgetter
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

from pydantic import BaseModel as PydanticBaseModel

from logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from logbook_parser.apa_2023_02.models.pydantic_json_mixin import PydanticJsonMixin
from logbook_parser.snippets.datetime.factored_duration import FactoredDuration
from logbook_parser.snippets.file.json_mixin import JsonMixin

# def serialize_timedelta(td: timedelta) -> str:
#     factored = FactoredDuration.from_timedelta(td)
#     result = f"{(factored.days*24)+factored.hours}:{factored.minutes}:00"
#     if factored.is_negative:
#         return f"-{result}"
#     return result


def deserialize_HHMMSS(td) -> timedelta:
    if isinstance(td, timedelta):
        print(td, type(td))
        return td
    split_td = td.split(":")
    negative = False
    hours = int(split_td[0])
    if "-" in split_td[0]:
        negative = True
    seconds = 0
    seconds = seconds + abs(hours) * 60 * 60
    print(seconds)
    seconds = seconds + int(split_td[1]) * 60
    seconds = seconds + int(split_td[2])
    if negative:
        seconds = seconds * -1
    return timedelta(seconds=seconds)


class BaseModel(PydanticBaseModel):
    """
    All the instances of BaseModel should serialize
    those types the same way
    """

    # class Config:
    #     json_encoders = {
    #         timedelta: serialize_timedelta,
    #     }


class Instant(BaseModel):
    utc_date: datetime
    local_tz: str

    def local(self) -> datetime:
        return self.utc_date.astimezone(tz=ZoneInfo(self.local_tz))


class Flight(BaseModel):
    idx: int
    flight_number: str
    departure_iata: str
    departure_time: Instant
    arrival_iata: str
    arrival_time: Instant
    fly: timedelta
    leg_greater: timedelta
    actual_block: timedelta
    eq_model: str
    eq_number: str
    eq_type: str
    eq_code: str
    ground_time: timedelta
    overnight_duration: timedelta
    fuel_performance: str
    departure_performance: timedelta
    arrival_performance: timedelta
    position: str
    delay_code: str
    uuid: str = ""


class DutyPeriod(BaseModel):
    idx: int
    flights: list[Flight]


class Trip(BaseModel):
    start_date: date
    trip_number: str
    base: str
    bid_equipment: str
    duty_periods: list[DutyPeriod]

    def first_start(self) -> datetime:
        flights: list[Flight] = sorted(
            self.duty_periods[0].flights, key=attrgetter("departure_time.utc_date")
        )
        return flights[0].departure_time.utc_date


class Month(BaseModel):
    month: int
    trips: list[Trip]


class Year(BaseModel):
    year: int
    months: dict[int, Month]


class Logbook(BaseModel, JsonMixin):
    metadata: ParsedMetadata | None
    aa_number: str
    years: dict[int, Year]

    def trips(self) -> Iterable[Trip]:
        for year in self.years.values():
            for month in year.months.values():
                for trip in month.trips:
                    yield trip
