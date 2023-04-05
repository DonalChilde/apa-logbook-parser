from datetime import date, datetime, timedelta
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, Tuple
from zoneinfo import ZoneInfo

from pydantic import BaseModel as PydanticBaseModel

from logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from logbook_parser.apa_2023_02.models.pydantic_json_mixin import PydanticJsonMixin
from logbook_parser.snippets.datetime.factored_duration import (
    FactoredDuration,
    duration_to_HHMMSS,
)
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

    def is_deadhead(self) -> bool:
        if self.position == "DH":
            return True
        return False


class DutyPeriod(BaseModel):
    idx: int
    flights: list[Flight]


class Trip(BaseModel):
    start_date: date
    trip_number: str
    base: str
    bid_equipment: str
    duty_periods: list[DutyPeriod]

    def first_departure(self, tz_spec: Literal["utc", "local"] = "utc") -> datetime:
        if tz_spec == "utc":
            return self.duty_periods[0].flights[0].departure_time.utc_date
        return self.duty_periods[0].flights[0].departure_time.local()

    def last_departure(self, tz_spec: Literal["utc", "local"] = "utc") -> datetime:
        if tz_spec == "utc":
            return self.duty_periods[-1].flights[-1].departure_time.utc_date
        return self.duty_periods[-1].flights[-1].departure_time.local()

    def flights(self) -> Iterable[Flight]:
        for dutyperiod in self.duty_periods:
            for flight in dutyperiod.flights:
                yield flight

    def flights_sorted(
        self, getter: Callable[[Flight], Any] = attrgetter("departure_time.utc_date")
    ) -> Iterable[Flight]:
        sort_keys: list[Tuple[int, int, Any]] = []
        for idx_dp, dutyperiod in enumerate(self.duty_periods):
            for idx_flt, flight in enumerate(dutyperiod.flights):
                sort_keys.append((idx_dp, idx_flt, getter(flight)))
        sort_keys.sort(key=itemgetter(2))
        for sort_key in sort_keys:
            yield self.duty_periods[sort_key[0]].flights[sort_key[1]]


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

    def default_file_name(self) -> str:
        start_date: str | None = None
        end_date: str | None = None
        trip: Trip | None = None
        for idx, trip in enumerate(self.sorted_trips()):
            if idx == 0:
                start_date = trip.first_departure().date().isoformat()
        if trip is not None:
            end_date = trip.last_departure().date().isoformat()
        return f"{start_date}Z-{end_date}Z-expanded-logbook.json"

    def sorted_trips(self, tz_spec: Literal["utc", "local"] = "utc") -> Iterable[Trip]:
        """Trips sorted based on first departure time"""
        sort_keys: list[Tuple[int, int, int, Any]] = []
        for key_year, year in self.years.items():
            for key_month, month in year.months.items():
                for idx_trip, trip in enumerate(month.trips):
                    sort_keys.append(
                        (
                            key_year,
                            key_month,
                            idx_trip,
                            trip.first_departure(tz_spec=tz_spec),
                        )
                    )
        sort_keys.sort(key=itemgetter(3))
        for sort_key in sort_keys:
            yield self.years[sort_key[0]].months[sort_key[1]].trips[sort_key[2]]

    def __str__(self) -> str:
        return self.stats()

    def stats(self, location: str = "Undefined") -> str:
        total_flights = trip_count = flight_count = 0
        source = first_departure = last_departure = ""
        trip = None
        sum_of_fly = timedelta()
        sum_of_actual_block = timedelta()
        sum_of_leg_greater = timedelta()
        deadheads = 0

        for trip_count, trip in enumerate(self.sorted_trips(), start=1):
            if trip_count == 1:
                first_departure = trip.first_departure(tz_spec="utc").isoformat()
            for flight_count, flight in enumerate(trip.flights(), start=1):
                sum_of_fly += flight.fly
                sum_of_actual_block += flight.actual_block
                sum_of_leg_greater += flight.leg_greater
                if flight.is_deadhead():
                    deadheads += 1
            total_flights += flight_count
        if trip is not None:
            last_departure = trip.last_departure(tz_spec="utc").isoformat()

        if self.metadata is not None:
            source = str(self.metadata.original_source.file_path)
        msg = (
            f"Expanded APA Logbook\n"
            f"\tLocation: {location}\n"
            f"\tParsed from: {source}\n"
            f"\tAA Number: {self.aa_number}\n"
            f"\tFirst Departure: {first_departure}Z\n"
            f"\tLast Departure: {last_departure}Z\n"
            f"\tTrips: {trip_count}\n"
            f"\tFlights: {total_flights}\n"
            f"\tTotal Fly: {format_timedelta(sum_of_fly)}\n"
            f"\tTotal Block: {format_timedelta(sum_of_actual_block)}\n"
            f"\tTotal Greater: {format_timedelta(sum_of_leg_greater)}\n"
            f"\tDeadheads: {deadheads}\n"
        )
        return msg


def format_timedelta(td: timedelta) -> str:
    hours, rem = divmod(td, timedelta(hours=1))
    minutes, rem = divmod(rem, timedelta(seconds=60))
    return f"{hours:,}.{minutes:02d}"
