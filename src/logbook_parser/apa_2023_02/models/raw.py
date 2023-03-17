"""Data model that most directly represents the available raw data from an xml file."""
from uuid import uuid5

from pydantic import BaseModel

from logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from logbook_parser.project_uuid import PROJECT_UUID
from logbook_parser.snippets.file.json_mixin import JsonMixin


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

    def default_file_name(self) -> str:
        return "logbook"
