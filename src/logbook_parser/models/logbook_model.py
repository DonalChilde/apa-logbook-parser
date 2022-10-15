from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class Logbook:
    uuid: str = ""
    aa_number: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    years: List["Year"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class Year:
    uuid: str = ""
    year: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    months: List["Month"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class Month:
    uuid: str = ""
    month_year: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    trips: List["Trip"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class Trip:
    uuid: str = ""
    trip_info: str = ""
    starts_on: str = ""
    trip_number: str = ""
    base: str = ""
    equipment: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    duty_periods: List["DutyPeriod"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class DutyPeriod:
    uuid: str = ""
    index: str = ""
    sum_of_actual_block: str = ""
    sum_of_leg_greater: str = ""
    sum_of_fly: str = ""
    flights: List["Flight"] = field(default_factory=list)

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())


@dataclass
class Flight:
    uuid: str = ""
    index: str = ""
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
