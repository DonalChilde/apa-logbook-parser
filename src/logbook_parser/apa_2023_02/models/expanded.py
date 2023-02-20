from pydantic import BaseModel


from datetime import date, datetime, timedelta


class Instant(BaseModel):
    utc_date: datetime
    local_tz: str


class Flight(BaseModel):
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


class DutyPeriod(BaseModel):
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
    months: list[Month]


class Logbook(BaseModel):
    aa_number: str
    years: list[Year]
