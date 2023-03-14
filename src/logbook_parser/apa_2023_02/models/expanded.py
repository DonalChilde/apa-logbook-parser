from pydantic import BaseModel as PydanticBaseModel
from pydantic import validator
from pydantic.json import timedelta_isoformat
from zoneinfo import ZoneInfo

from datetime import date, datetime, timedelta

from logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from logbook_parser.snippets.datetime.factored_duration import FactoredDuration


def serialize_timedelta(td: timedelta) -> str:
    factored = FactoredDuration.from_timedelta(td)
    result = f"{(factored.days*24)+factored.hours}:{factored.minutes}:00"
    if factored.is_negative:
        return f"-{result}"
    return result


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

    # _deserialize_fly = validator("fly", allow_reuse=True)(deserialize_HHMMSS)
    # _deserialize_leg_greater = validator("leg_greater", allow_reuse=True)(
    #     deserialize_HHMMSS
    # )
    # _deserialize_actual_block = validator("actual_block", allow_reuse=True)(
    #     deserialize_HHMMSS
    # )
    # _deserialize_ground_time = validator("ground_time", allow_reuse=True)(
    #     deserialize_HHMMSS
    # )
    # _deserialize_overnight_duration = validator("overnight_duration", allow_reuse=True)(
    #     deserialize_HHMMSS
    # )
    # _deserialize_HHMMSS_departure_performance = validator(
    #     "departure_performance", allow_reuse=True
    # )(deserialize_HHMMSS)
    # _deserialize_arrival_performance = validator(
    #     "arrival_performance", allow_reuse=True
    # )(deserialize_HHMMSS)


class DutyPeriod(BaseModel):
    idx: int
    flights: list[Flight]


class Trip(BaseModel):
    start_date: date
    trip_number: str
    base: str
    bid_equipment: str
    duty_periods: list[DutyPeriod]


class Month(BaseModel):
    month: int
    trips: list[Trip]


class Year(BaseModel):
    year: int
    months: dict[int, Month]


class Logbook(BaseModel):
    metadata: ParsedMetadata | None
    aa_number: str
    years: dict[int, Year]
