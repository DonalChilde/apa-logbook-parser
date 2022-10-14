from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class LogbookElement:
    uuid: str = ""
    aa_number: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    years: List["YearElement"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class YearElement:
    uuid: str = ""
    year: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    months: List["MonthElement"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class MonthElement:
    uuid: str = ""
    month_year: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    trips: List["TripElement"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class TripElement:
    uuid: str = ""
    trip_info: str = ""
    starts_on: str = ""
    trip_number: str = ""
    base: str = ""
    equipment: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    duty_periods: List["DutyPeriodElement"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class DutyPeriodElement:
    uuid: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    flights: List["FlightElement"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class FlightElement:
    uuid: str = ""
    flight_number: str = ""
    departure_iata: str = ""
    departure_icao: str = ""
    departure_local: str = ""
    departure_utc: str = ""
    arrival_iata: str = ""
    arrival_icao: str = ""
    arrival_local: str = ""
    arrival_utc: str = ""
    fly: str = ""
    leg_greater: str = ""
    eq_model: str = ""
    eq_number: str = ""
    eq_type: str = ""
    eq_code: str = ""
    ground_time: str = ""
    overnight_duration: str = ""
    fuel_performance: str = ""
    departure_performance: str = ""
    arrival_performance: str = ""
    actual_block: str = ""
    position: str = ""
    delay_code: str = ""

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())
