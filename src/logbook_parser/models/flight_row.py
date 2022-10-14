from dataclasses import dataclass
from typing import List


@dataclass
class FlightRow:
    aa_number: str
    year: str
    month_year: str
    base: str
    bid_eq: str
    trip_starts_on: str
    trip_number: str
    dp_flt: str
    flight_number: str
    eq_number: str
    eq_model: str
    position: str
    departure_iata: str
    departure_icao: str
    departure_local: str
    departure_utc: str
    departure_performance: str
    arrival_iata: str
    arrival_icao: str
    arrival_local: str
    arrival_utc: str
    arrival_performance: str
    fly: str
    leg_greater: str
    actual_block: str
    ground_time: str
    overnight_duration: str
    delay_code: str
    eq_type: str
    eq_code: str
    fuel_performance: str
    year_uuid: str
    month_uuid: str
    trip_uuid: str
    duty_period_uuid: str
    flight_uuid: str
    trip_info: str
