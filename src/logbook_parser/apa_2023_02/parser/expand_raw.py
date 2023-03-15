from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from datetime import time as dt_time
from zoneinfo import ZoneInfo
import time

from logbook_parser.airports_db.airports import from_iata
from logbook_parser.apa_2023_02.models import expanded, raw
from logbook_parser.snippets.datetime.parse_duration_regex import (
    pattern_HHHMM,
    parse_duration,
)

DURATION_PATTERN = pattern_HHHMM(hm_sep=".")


@dataclass
class TripInfo:
    start_date: date
    trip_number: str
    base: str
    bid_equipment: str


DEFAULT_INSTANT = expanded.Instant(
    utc_date=datetime(year=1900, month=1, day=1, tzinfo=timezone.utc), local_tz="UTC"
)


def expand_raw_logbook(raw_log: raw.Logbook) -> expanded.Logbook:
    expanded_log = expanded.Logbook(
        metadata=raw_log.metadata, aa_number=raw_log.aa_number, years={}
    )
    for raw_year in raw_log.years:
        expanded_year = expand_year(raw_year)
        expanded_log.years[expanded_year.year] = expanded_year
    return expanded_log


def expand_year(raw_year: raw.Year) -> expanded.Year:
    result = expanded.Year(year=int(raw_year.year), months={})
    for raw_month in raw_year.months:
        expanded_month = expand_month(raw_month)
        result.months[expanded_month.month] = expanded_month
    return result


def expand_month(raw_month: raw.Month) -> expanded.Month:
    month_index = parse_month_number(raw_month.month_year)
    result = expanded.Month(month=month_index, trips=[])
    for raw_trip in raw_month.trips:
        expanded_trip = expand_trip(raw_trip)
        result.trips.append(expanded_trip)
    return result


def expand_trip(raw_trip: raw.Trip) -> expanded.Trip:
    expanded_dutyperiods: list[expanded.DutyPeriod] = []
    trip_info = parse_trip_info(raw_trip.trip_info)
    for raw_dutyperiod in raw_trip.duty_periods:
        expanded_dutyperiod = expand_dutyperiod(raw_dutyperiod)
        expanded_dutyperiods.append(expanded_dutyperiod)
    result = expanded.Trip(
        start_date=trip_info.start_date,
        trip_number=trip_info.trip_number,
        base=trip_info.base,
        bid_equipment=trip_info.bid_equipment,
        duty_periods=expanded_dutyperiods,
    )
    return result


def expand_dutyperiod(raw_dutyperiod: raw.DutyPeriod) -> expanded.DutyPeriod:
    expanded_flights: list[expanded.Flight] = []
    for raw_flight in raw_dutyperiod.flights:
        expanded_flight = expand_flight(raw_flight=raw_flight)
        expanded_flights.append(expanded_flight)
    result = expanded.DutyPeriod(idx=raw_dutyperiod.dp_idx, flights=expanded_flights)
    return result


def expand_flight(raw_flight: raw.Flight) -> expanded.Flight:
    result = expanded.Flight(
        idx=raw_flight.flight_idx,
        flight_number=raw_flight.flight_number,
        departure_iata=raw_flight.departure_iata,
        departure_time=parse_departure_time(raw_flight),
        arrival_iata=raw_flight.arrival_iata,
        arrival_time=DEFAULT_INSTANT,
        fly=parse_log_duration(raw_flight.fly),
        leg_greater=parse_log_duration(raw_flight.leg_greater),
        actual_block=parse_log_duration(raw_flight.actual_block),
        eq_model=raw_flight.eq_model,
        eq_number=raw_flight.eq_number,
        eq_type=raw_flight.eq_type,
        eq_code=raw_flight.eq_code,
        ground_time=parse_log_duration(raw_flight.ground_time),
        overnight_duration=parse_log_duration(raw_flight.overnight_duration),
        fuel_performance=raw_flight.fuel_performance,
        departure_performance=parse_performance(raw_flight.departure_performance),
        arrival_performance=parse_performance(raw_flight.arrival_performance),
        position=raw_flight.position,
        delay_code=raw_flight.delay_code,
    )
    result.arrival_time = parse_arrival_time(
        expanded_flight=result, raw_flight=raw_flight
    )

    return result


def parse_trip_info(trip_info: str) -> TripInfo:
    split_info = trip_info.split()
    parsed_trip_info = TripInfo(
        start_date=datetime.strptime(split_info[0], "%m/%d/%Y").date(),
        trip_number=split_info[1],
        base=split_info[2],
        bid_equipment=split_info[3],
    )
    return parsed_trip_info


def parse_month_number(month_year: str) -> int:
    parsed_date = datetime.strptime(month_year, "%B %Y")
    return parsed_date.month


def parse_departure_time(raw_flight: raw.Flight) -> expanded.Instant:
    departure = datetime.fromisoformat(raw_flight.departure_local)
    departure_tz_name = from_iata(raw_flight.departure_iata, date=None).tz
    departure_tz_info = ZoneInfo(departure_tz_name)
    departure = departure.replace(tzinfo=departure_tz_info)
    instant = expanded.Instant(
        utc_date=departure.astimezone(timezone.utc), local_tz=departure_tz_name
    )
    return instant


def parse_arrival_time(
    expanded_flight: expanded.Flight, raw_flight: raw.Flight
) -> expanded.Instant:
    tz_name = from_iata(raw_flight.arrival_iata, date=None).tz
    departure_in_arrival_tz = expanded_flight.departure_time.utc_date.astimezone(
        tz=ZoneInfo(tz_name)
    )
    try:
        # 09/17 05:13
        parsed_arrival = time.strptime(raw_flight.arrival_local, "%m/%y %H:%M")
        arrival_time = dt_time(
            hour=parsed_arrival.tm_hour, minute=parsed_arrival.tm_min
        )
        return instant_from_next_time(
            departure_in_arrival_tz, next_time=arrival_time, next_tz=tz_name
        )
    except ValueError:
        # TODO what does this raise?
        # moving on to try alternate data format
        pass
    # 05:13
    parsed_arrival = time.strptime(raw_flight.arrival_local, "%H:%M")
    arrival_time = dt_time(hour=parsed_arrival.tm_hour, minute=parsed_arrival.tm_min)
    return instant_from_next_time(
        departure_in_arrival_tz, next_time=arrival_time, next_tz=tz_name
    )


def instant_from_duration(
    start_utc: datetime, duration: timedelta, end_tz: str
) -> expanded.Instant:
    end = start_utc + duration
    result = expanded.Instant(utc_date=end, local_tz=end_tz)
    return result


def instant_from_next_time(start: datetime, next_time: dt_time, next_tz: str):
    end = start.replace(
        hour=next_time.hour,
        minute=next_time.minute,
        second=next_time.second,
        microsecond=next_time.microsecond,
    )
    if start > end:
        end = end + timedelta(hours=24)

    return expanded.Instant(utc_date=end.astimezone(tz=timezone.utc), local_tz=next_tz)


def parse_performance(dur: str) -> timedelta:
    if not dur:
        return timedelta()
    return timedelta(minutes=int(dur))


def parse_log_duration(dur: str) -> timedelta:
    if not dur:
        return timedelta()
    if "." not in dur:
        return timedelta()
    parsed = parse_duration(pattern=DURATION_PATTERN, duration_string=dur)
    return timedelta(hours=parsed.hours, minutes=parsed.minutes)
