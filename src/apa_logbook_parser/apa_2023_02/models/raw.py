"""Data model that most directly represents the available raw data from an xml file."""
from datetime import date, datetime
from operator import attrgetter, itemgetter
from typing import Any, Callable, Iterable, Tuple
from uuid import uuid5

from pydantic import BaseModel

from apa_logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from apa_logbook_parser.project_uuid import PROJECT_UUID
from apa_logbook_parser.snippets.file.json_mixin import JsonMixin


class Flight(BaseModel):
    flight_idx: int
    flight_number: str
    departure_iata: str
    departure_local: str
    arrival_iata: str
    arrival_local: str
    fly: str
    leg_greater: str
    actual_block: str
    eq_model: str
    eq_number: str
    eq_type: str
    eq_code: str
    ground_time: str
    overnight_duration: str
    fuel_performance: str
    departure_performance: str
    arrival_performance: str
    position: str
    delay_code: str

    def generate_uuid(self) -> str:
        uuid = uuid5(PROJECT_UUID, repr(self))
        return str(uuid)

    def is_deadhead(self) -> bool:
        if self.position == "DH":
            return True
        return False


class DutyPeriod(BaseModel):
    dp_idx: int
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    flights: list[Flight]


class Trip(BaseModel):
    trip_info: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    duty_periods: list[DutyPeriod]

    def first_departure(self) -> str:
        return self.duty_periods[0].flights[0].departure_local

    def last_departure(self) -> str:
        return self.duty_periods[-1].flights[-1].departure_local

    def flights(self) -> Iterable[Flight]:
        for dutyperiod in self.duty_periods:
            for flight in dutyperiod.flights:
                yield flight


class Month(BaseModel):
    month_year: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    trips: list[Trip]


class Year(BaseModel):
    year: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    months: list[Month]


class Logbook(BaseModel, JsonMixin):
    metadata: ParsedMetadata | None
    aa_number: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    years: list[Year]

    def __str__(self) -> str:
        return self.stats()

    def stats(self, location: str = "Undefined") -> str:
        source = ""
        total_flights = trip_count = flight_count = deadheads = 0
        for trip_count, trip in enumerate(self.trips(), start=1):
            for flight_count, flight in enumerate(trip.flights(), start=1):
                if flight.is_deadhead():
                    deadheads += 1
            total_flights += flight_count

        if self.metadata is not None:
            source = str(self.metadata.original_source.file_path)
        msg = (
            f"Raw APA Logbook\n"
            f"\tLocation: {location}\n"
            f"\tParsed from: {source}\n"
            f"\tAA Number: {self.aa_number}\n"
            f"\tFirst Departure: {self.first_departure_date().isoformat()}L\n"
            f"\tLast Departure: {self.last_departure_date().isoformat()}L\n"
            f"\tTrips: {trip_count}\n"
            f"\tFlights: {total_flights}\n"
            f"\tTotal Fly: {self.sum_of_fly}\n"
            f"\tTotal Block: {self.sum_of_actual_block}\n"
            f"\tTotal Greater: {self.sum_of_leg_greater}\n"
            f"\tDeadheads: {deadheads}\n"
        )
        return msg

    def default_file_name(self) -> str:
        start_date = self.first_departure_date().date().isoformat()
        end_date = self.last_departure_date().date().isoformat()
        return f"{self.aa_number}-{start_date}L-{end_date}L-raw-logbook.json"

    def first_departure_date(self) -> datetime:
        first_departure = (
            self.years[0].months[0].trips[0].duty_periods[0].flights[0].departure_local
        )
        return datetime.fromisoformat(first_departure)

    def last_departure_date(self) -> datetime:
        last_departure = (
            self.years[-1]
            .months[-1]
            .trips[-1]
            .duty_periods[-1]
            .flights[-1]
            .departure_local
        )
        return datetime.fromisoformat(last_departure)

    def trips(self) -> Iterable[Trip]:
        for year in self.years:
            for month in year.months:
                for trip in month.trips:
                    yield trip

    def flights(self) -> Iterable[Flight]:
        for trip in self.trips():
            for flight in trip.flights():
                yield flight
