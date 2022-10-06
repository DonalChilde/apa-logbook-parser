from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class FlightRow:
    aa_number: str
    year: str
    year_uuid: str
    month_year: str
    month_uuid: str
    trip_uuid: str
    trip_info: str
    duty_period_uuid: str
    flight_uuid: str
    flight_number: str
    departure_iata: str
    departure_lcl: str
    arrival_iata: str
    arrival_local: str
    fly: str
    leg_greater: str
    actual_block: str
    ground_time: str
    overnight_duration: str
    eq_model: str
    eq_number: str
    eq_type: str
    eq_code: str
    fuel_performance: str
    departure_performance: str
    arrival_performance: str
    position: str
    delay_code: str
    trip_starts_on: str = field(init=False, default="")
    trip_number: str = field(init=False, default="")
    base: str = field(init=False, default="")
    bid_eq: str = field(init=False, default="")
    departure_utc = field(init=False, default="")
    arrival_utc = field(init=False, default="")
    departure_icao = field(init=False, default="")
    arrival_icao = field(init=False, default="")

    def field_order(self, dropped_fields: str) -> List[str]:
        # TODO make a nice order
        # TODO check/update new fields
        field_str = (
            "aa_number year  month_year   "
            "trip_info   flight_number "
            "departure_station out_datetime arrival_station in_datetime "
            "fly leg_greater actual_block ground_time overnight_duration "
            "eq_model eq_number eq_type eq_code fuel_performance departure_performance "
            "arrival_performance position delay_code "
            "trip_starts_on trip_number base bid_eq "
            "year_uuid month_uuid trip_uuid duty_period_uuid flight_uuid "
        )
        fields: List[str] = field_str.split()
        drops = dropped_fields.split()
        for drop in drops:
            fields.remove(drop)
        return fields


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
    departure_station: str = ""
    out_datetime: str = ""
    arrival_station: str = ""
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
    in_datetime: str = ""

    def __post_init__(self):
        if self.uuid == "":
            self.uuid = str(uuid.uuid4())
