import logging
from datetime import datetime, timedelta, timezone
from typing import List
from zoneinfo import ZoneInfo

import airportsdata

import logbook_parser.models.logbook_model as model
from logbook_parser.models.flight_row import FlightRow
from logbook_parser.parse_context import ParseContext
from logbook_parser.util.parse_duration_regex import parse_duration, pattern_HHHMM

logger = logging.getLogger(__name__)
airports = airportsdata.load("IATA")  # key is IATA code


def validate_logbook(logbook: model.Logbook, parse_context: ParseContext):
    logbook.sum_of_actual_block = parse_duration_string(logbook.sum_of_actual_block)
    logbook.sum_of_fly = parse_duration_string(logbook.sum_of_fly)
    logbook.sum_of_leg_greater = parse_duration_string(logbook.sum_of_leg_greater)
    for year in logbook.years:
        validate_year(year, parse_context)
        for month in year.months:
            validate_month(month, parse_context)
            for trip in month.trips:
                validate_trip(trip, parse_context)
                for dutyperiod in trip.duty_periods:
                    validate_dutyperiod(dutyperiod, parse_context)
                    for flight in dutyperiod.flights:
                        validate_flight(flight, parse_context)


def validate_year(year: model.Year, parse_context: ParseContext):
    year.sum_of_leg_greater = parse_duration_string(year.sum_of_leg_greater)
    year.sum_of_fly = parse_duration_string(year.sum_of_fly)
    year.sum_of_actual_block = parse_duration_string(year.sum_of_actual_block)
    _ = year, parse_context


def validate_month(month: model.Month, parse_context: ParseContext):
    month.sum_of_leg_greater = parse_duration_string(month.sum_of_leg_greater)
    month.sum_of_fly = parse_duration_string(month.sum_of_fly)
    month.sum_of_actual_block = parse_duration_string(month.sum_of_actual_block)

    _ = month, parse_context


def validate_trip(trip: model.Trip, parse_context: ParseContext):
    _ = parse_context
    trip.sum_of_leg_greater = parse_duration_string(trip.sum_of_leg_greater)
    trip.sum_of_fly = parse_duration_string(trip.sum_of_fly)
    trip.sum_of_actual_block = parse_duration_string(trip.sum_of_actual_block)

    split_trip_info(trip)
    # TODO check overnight lengths, some overnights are missing. infer from utc in time?
    # FIXME output validation messages, esp, when data is infered.


def validate_dutyperiod(dutyperiod: model.DutyPeriod, parse_context: ParseContext):
    _ = parse_context
    dutyperiod.sum_of_leg_greater = parse_duration_string(dutyperiod.sum_of_leg_greater)
    dutyperiod.sum_of_fly = parse_duration_string(dutyperiod.sum_of_fly)
    dutyperiod.sum_of_actual_block = parse_duration_string(
        dutyperiod.sum_of_actual_block
    )


def validate_flight(flight: model.Flight, parse_context: ParseContext):
    # odl has junk data, drop data when flight has a ground time? also junk data has no
    # decimal? invalid time format?
    _ = parse_context
    remove_bad_odl(flight)
    if flight.overnight_duration:
        flight.overnight_duration = parse_duration_string(flight.overnight_duration)
    if flight.ground_time:
        flight.ground_time = parse_duration_string(flight.ground_time)
    if flight.actual_block:
        flight.actual_block = parse_duration_string(flight.actual_block)
    if flight.leg_greater:
        flight.leg_greater = parse_duration_string(flight.leg_greater)
    if flight.fly:
        flight.fly = parse_duration_string(flight.fly)
    set_icao(flight)
    make_tz_aware(flight)
    check_times_against_durations(flight)


def check_times_against_durations(flight: model.Flight):
    _ = flight
    # check departure and arrival times against a duration when available.


def set_icao(flight: model.Flight):
    flight.departure_icao = airports[flight.departure_iata]["icao"]
    flight.arrival_icao = airports[flight.arrival_iata]["icao"]


def make_tz_aware(flight: model.Flight):
    dep_local = datetime.fromisoformat(flight.departure_local)
    dep_local = dep_local.replace(
        tzinfo=ZoneInfo(airports[flight.departure_iata]["tz"])
    )
    flight.departure_local = dep_local.isoformat()
    flight.departure_utc = dep_local.astimezone(timezone.utc).isoformat()
    complete_arrival_time(dep_local, flight)
    arr_local = datetime.fromisoformat(flight.arrival_local)
    arr_local = arr_local.replace(tzinfo=ZoneInfo(airports[flight.arrival_iata]["tz"]))
    flight.arrival_local = arr_local.isoformat()
    flight.arrival_utc = arr_local.astimezone(timezone.utc).isoformat()


def complete_arrival_time(departure: datetime, flight: model.Flight):
    # 10/30 11:11
    # 22:57
    # refactor to not depend on Flight
    dep_no_tz = departure.replace(tzinfo=None)
    year_added = f"{departure.year}/{flight.arrival_local}"
    try:
        partial = datetime.strptime(year_added, "%Y/%m/%d %H:%M")
        # check if overlaps year, eg. 12/31-1/1
        if partial < dep_no_tz:
            partial = partial.replace(year=departure.year + 1)
    except ValueError as err:
        logger.info("Attempt alternate parse: %s", err)
        try:
            partial = datetime.strptime(year_added, "%Y/%H:%M")
            partial = partial.replace(month=departure.month, day=departure.day)
            # check if overlaps day, eg. 2350-0230
            if partial.time() < departure.time():
                partial = partial + timedelta(days=1)
            # check if overlaps year, eg. 12/31-1/1
            if partial < dep_no_tz:
                partial = partial.replace(year=departure.year + 1)
        except ValueError as err_2:
            _ = err_2
            logger.error(
                "Failure to parse %s for flight %s",
                flight.arrival_local,
                flight.uuid,
                exc_info=True,
            )
            return
    if partial < dep_no_tz:
        logger.warning("Failed to parse the arrival time for %s", flight)
        return
    flight.arrival_local = partial.isoformat()


def remove_bad_odl(flight: model.Flight):

    if (
        flight.overnight_duration
        and "." not in flight.overnight_duration
        and flight.ground_time
    ):
        flight.overnight_duration = ""


def split_trip_info(trip_element: model.Trip):
    # TODO raise a valdation error.
    split_info = trip_element.trip_info.split()
    if len(split_info) == 4:
        trip_element.starts_on = split_info[0]
        trip_element.trip_number = split_info[1]
        trip_element.base = split_info[2]
        trip_element.equipment = split_info[3]


def parse_duration_string(dur_string: str) -> str:
    pattern = pattern_HHHMM(hm_sep=".")
    dur = parse_duration(pattern=pattern, duration_string=dur_string)
    return f"{dur['hours']}:{dur['minutes']:02}:00"


def flatten_logbook(logbook: model.Logbook) -> List[FlightRow]:
    rows = []
    for year in logbook.years:
        for month in year.months:
            for trip in month.trips:
                for duty_period in trip.duty_periods:
                    for flight in duty_period.flights:
                        row = FlightRow(
                            aa_number=logbook.aa_number,
                            year=year.year,
                            year_uuid=year.uuid,
                            month_year=month.month_year,
                            month_uuid=month.uuid,
                            trip_info=trip.trip_info,
                            trip_uuid=trip.uuid,
                            duty_period_uuid=duty_period.uuid,
                            flight_uuid=flight.uuid,
                            flight_number=flight.flight_number,
                            dp_flt=f"{duty_period.index}-{flight.index}",
                            departure_iata=flight.departure_iata,
                            departure_icao=flight.departure_icao,
                            departure_local=flight.departure_local,
                            departure_utc=flight.departure_utc,
                            arrival_iata=flight.arrival_iata,
                            arrival_icao=flight.arrival_icao,
                            arrival_local=flight.arrival_local,
                            arrival_utc=flight.arrival_utc,
                            fly=flight.fly,
                            leg_greater=flight.leg_greater,
                            actual_block=flight.actual_block,
                            ground_time=flight.ground_time,
                            overnight_duration=flight.overnight_duration,
                            eq_model=flight.eq_model,
                            eq_number=flight.eq_number,
                            eq_type=flight.eq_type,
                            eq_code=flight.eq_code,
                            fuel_performance=flight.fuel_performance,
                            departure_performance=flight.departure_performance,
                            arrival_performance=flight.arrival_performance,
                            position=flight.position,
                            delay_code=flight.delay_code,
                            trip_number=trip.trip_number,
                            trip_starts_on=trip.starts_on,
                            bid_eq=trip.equipment,
                            base=trip.base,
                        )

                        rows.append(row)
    return rows
