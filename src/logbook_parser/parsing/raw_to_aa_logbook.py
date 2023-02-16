import logging
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from uuid import uuid4
from zoneinfo import ZoneInfo
from logbook_parser.airports_db.airport import Airport

import logbook_parser.models.aa_logbook as aa
import logbook_parser.models.raw_logbook as raw
from logbook_parser.airports_db.airports import from_iata
from logbook_parser.parsing.context import Context
from logbook_parser.snippets.datetime.complete_partial_datetime import (
    complete_future_mdt,
    complete_future_time,
)
from logbook_parser.snippets.datetime.factored_duration import FactoredDuration
from logbook_parser.snippets.datetime.parse_duration_regex import (
    parse_duration,
    pattern_HHHMM,
)

logger = logging.getLogger(__name__)


def translate_logbook(raw_logbook: raw.Logbook, ctx: Context) -> aa.Logbook:
    pilot = aa.Pilot(uuid=uuid4(), ident=raw_logbook.aa_number)
    aa_logbook = aa.Logbook(uuid=raw_logbook.uuid, pilot=pilot)
    for year in raw_logbook.years:
        for month in year.months:
            for trip in month.trips:
                aa_logbook.trips.append(translate_trip(trip, ctx))
    return aa_logbook


def translate_trip(trip: raw.Trip, ctx: Context) -> aa.Trip:
    aa_dutyperiods: List[aa.DutyPeriod] = []
    split_info = trip.trip_info.split()
    # starts_on = split_info[0]
    trip_number = split_info[1]
    base = split_info[2]
    equipment = split_info[3]

    for dutyperiod in trip.dutyperiods:
        aa_dutyperiods.append(translate_dutyperiod(dutyperiod, ctx))
    aa_trip = aa.Trip(
        uuid=trip.uuid,
        number=trip_number,
        start=aa_dutyperiods[0].start,
        end=aa_dutyperiods[-1].end,
        base=base,
        bid_equipment=equipment,
        dutyperiods=aa_dutyperiods,
    )
    return aa_trip


def translate_dutyperiod(dutyperiod: raw.DutyPeriod, ctx: Context) -> aa.DutyPeriod:
    aa_flights: List[aa.Flight] = []
    for flight in dutyperiod.flights:
        aa_flights.append(translate_flight(flight, ctx))
    start, end, layover = find_start_end_layover(aa_flights, dutyperiod.flights)
    aa_dutyperiod = aa.DutyPeriod(
        uuid=dutyperiod.uuid,
        index=dutyperiod.index,
        start=start,
        end=end,
        layover=layover,
        flights=aa_flights,
    )
    return aa_dutyperiod


def find_start_end_layover(
    aa_flights: List[aa.Flight], raw_flights: List[raw.Flight]
) -> Tuple[datetime, datetime, aa.Layover | None]:
    # FIXME needs to account for sign in, late departure, late arrival, and debrief
    sign_in = timedelta(hours=1)
    debrief = timedelta(minutes=30)
    if raw_flights[0].departure_performance in (None, ""):
        departure_perf = 0
    else:
        departure_perf = int(raw_flights[0].departure_performance)
    departure_perf_delta = timedelta(minutes=departure_perf)
    start = aa_flights[0].departure_time - (sign_in + departure_perf_delta)
    end = aa_flights[-1].arrival_time + debrief
    layover = check_for_layover(aa_flight=aa_flights[-1], raw_flight=raw_flights[-1])
    return (start, end, layover)


def check_for_layover(
    aa_flight: aa.Flight, raw_flight: raw.Flight
) -> aa.Layover | None:
    if raw_flight.overnight_duration is None:
        return None
    try:
        layover_duration = parse_str_dur(raw_flight.overnight_duration)
        layover = aa.Layover(
            uuid=uuid4(),
            location=aa_flight.departure_airport.city,
            duration=layover_duration.to_timedelta(),
        )
        return layover
    except (ValueError, TypeError):
        return None


def translate_flight(flight: raw.Flight, ctx: Context) -> aa.Flight:
    equipment = aa.Equipment.from_sig(
        number=flight.eq_number,
        model=flight.eq_model,
        code=flight.eq_code,
        type_=flight.eq_type,
    )
    departure_local = datetime.fromisoformat(flight.departure_local)
    departure_airport = from_iata(flight.departure_iata, None)
    departure_local = departure_local.replace(tzinfo=ZoneInfo(departure_airport.tz))
    departure_utc = departure_local.astimezone(tz=timezone.utc)
    arrival_airport = from_iata(flight.arrival_iata, None)
    fly = parse_str_dur(flight.fly).to_timedelta()
    aa_flight = aa.Flight(
        uuid=flight.uuid,
        index=flight.index,
        number=flight.flight_number,
        equipment=equipment,
        position=flight.position,
        departure_airport=departure_airport,
        departure_time=departure_local,
        departure_performance=flight.departure_performance or "0",
        arrival_airport=arrival_airport,
        # FIXME incorrect arrival time when fly is 0 eg DH
        # arrival_time=departure_local + fly,
        arrival_time=parse_arrival_time(
            departure_local, flight.arrival_local, arrival_airport
        ),
        arrival_performance=flight.arrival_performance or "0",
        fly=fly,
        block=parse_str_dur(flight.actual_block).to_timedelta(),
        leg_greater=parse_str_dur(flight.leg_greater).to_timedelta(),
        fuel_performance=flight.fuel_performance,
        ground_time=parse_str_dur(flight.ground_time).to_timedelta(),
        delay_code=flight.delay_code,
    )
    return aa_flight


def parse_arrival_time(
    departure: datetime, arrival_str: str, arrival_airport: Airport
) -> datetime:
    strf = "%m/%d %H:%M"
    try:
        arrival = complete_future_mdt(
            start=departure,
            future=arrival_str,
            tz_info=ZoneInfo(arrival_airport.tz),
            strf=strf,
        )
        return arrival
    except ValueError as error:
        logger.info("Could not match %s as %s, %s", arrival_str, strf, error)
        try:
            strf = "%H:%M"
            arrival = complete_future_time(
                start=departure,
                future=arrival_str,
                tz_info=ZoneInfo(arrival_airport.tz),
                strf=strf,
            )
            return arrival
        except ValueError as error_2:
            logger.error(
                "Could not match %s as %s, %s unable to calculate arrival time.",
                arrival_str,
                strf,
                error_2,
            )
            raise error_2


def parse_str_dur(duration_string: str) -> FactoredDuration:
    pattern = pattern_HHHMM(hm_sep=".")
    if duration_string is None or duration_string == "":
        return FactoredDuration()
    try:
        duration = parse_duration(pattern=pattern, duration_string=duration_string)
    except TypeError:
        return FactoredDuration()
    return duration


# def complete_arrival_time(
#     departure_local: datetime,
#     raw_flight: raw.Flight,
#     aa_flight: aa.Flight,
#     position: str,
#     fly: timedelta,
# ):
#     # 10/30 11:11
#     # 22:57
#     # refactor to not depend on Flight
#     dep_no_tz = departure_local.replace(tzinfo=None)
#     year_added = f"{departure_local.year}/{raw_flight.arrival_local}"
#     try:
#         partial = datetime.strptime(year_added, "%Y/%m/%d %H:%M")
#         # check if overlaps year, eg. 12/31-1/1
#         if partial < dep_no_tz:
#             partial = partial.replace(year=departure_local.year + 1)
#     except ValueError as err:
#         logger.info("Attempt alternate parse: %s", err)
#         try:
#             partial = datetime.strptime(year_added, "%Y/%H:%M")
#             partial = partial.replace(
#                 month=departure_local.month, day=departure_local.day
#             )
#             # check if overlaps day, eg. 2350-0230
#             if partial.time() < departure_local.time():
#                 partial = partial + timedelta(days=1)
#             # check if overlaps year, eg. 12/31-1/1
#             if partial < dep_no_tz:
#                 partial = partial.replace(year=departure_local.year + 1)
#         except ValueError as err_2:
#             _ = err_2
#             logger.error(
#                 "Failure to parse %s for flight %s",
#                 raw_flight.arrival_local,
#                 raw_flight.uuid,
#                 exc_info=True,
#             )
#             return
#     if partial < dep_no_tz:
#         logger.warning("Failed to parse the arrival time for %s", raw_flight)
#         return
#     raw_flight.arrival_local = partial.isoformat()


# def complete_partial_datetime(ref_datetime: datetime, partial_string: str) -> datetime:
#     # 10/30 11:11
#     # 22:57
#     # FIXME move to snippets
#     ref_tz = ref_datetime.tzinfo
#     if ref_tz:
#         ref_no_tz = ref_datetime.replace(tzinfo=None)
#     else:
#         ref_no_tz = ref_datetime
#     year_added = f"{ref_no_tz.year}/{partial_string}"
#     try:
#         partial = datetime.strptime(year_added, "%Y/%m/%d %H:%M")
#         # check if overlaps year, eg. 12/31-1/1
#         if partial < ref_no_tz:
#             partial = partial.replace(year=ref_no_tz.year + 1)
#     except ValueError as err:
#         logger.info("%s", err)
#         try:
#             partial = datetime.strptime(year_added, "%Y/%H:%M")
#             partial = partial.replace(month=ref_no_tz.month, day=ref_no_tz.day)
#             # check if overlaps day, eg. 2350-0230
#             if partial.time() < ref_no_tz.time():
#                 partial = partial + timedelta(days=1)
#             # check if overlaps year, eg. 12/31-1/1
#             if partial < ref_no_tz:
#                 partial = partial.replace(year=ref_no_tz.year + 1)
#         except ValueError as err_2:
#             _ = err_2
#             logger.error(
#                 "Failure to parse %s",
#                 partial_string,
#                 exc_info=True,
#             )
#             raise err_2
#     partial.replace(tzinfo=ref_tz)
#     if partial < ref_datetime:
#         error = ValueError(
#             f"Partial string {partial_string} parsed as {partial.isoformat()} "
#             f"does not come after ref of {ref_datetime.isoformat()}"
#         )
#         logger.error(error)
#         raise error
#     return partial


# def complete_arrival_time_2(departure_local: datetime, flight: raw.Flight):
#     # 10/30 11:11
#     # 22:57
#     # refactor to not depend on Flight
#     dep_no_tz = departure_local.replace(tzinfo=None)
#     year_added = f"{departure_local.year}/{flight.arrival_local}"
#     try:
#         partial = datetime.strptime(year_added, "%Y/%m/%d %H:%M")
#         # check if overlaps year, eg. 12/31-1/1
#         if partial < dep_no_tz:
#             partial = partial.replace(year=departure_local.year + 1)
#     except ValueError as err:
#         logger.info("Attempt alternate parse: %s", err)
#         try:
#             partial = datetime.strptime(year_added, "%Y/%H:%M")
#             partial = partial.replace(
#                 month=departure_local.month, day=departure_local.day
#             )
#             # check if overlaps day, eg. 2350-0230
#             if partial.time() < departure_local.time():
#                 partial = partial + timedelta(days=1)
#             # check if overlaps year, eg. 12/31-1/1
#             if partial < dep_no_tz:
#                 partial = partial.replace(year=departure_local.year + 1)
#         except ValueError as err_2:
#             _ = err_2
#             logger.error(
#                 "Failure to parse %s for flight %s",
#                 flight.arrival_local,
#                 flight.uuid,
#                 exc_info=True,
#             )
#             return
#     if partial < dep_no_tz:
#         logger.warning("Failed to parse the arrival time for %s", flight)
#         return
#     flight.arrival_local = partial.isoformat()


#################################


# def validate_logbook(logbook: model.Logbook, parse_context: ParseContext):
#     logbook.sum_of_actual_block = parse_duration_string(logbook.sum_of_actual_block)
#     logbook.sum_of_fly = parse_duration_string(logbook.sum_of_fly)
#     logbook.sum_of_leg_greater = parse_duration_string(logbook.sum_of_leg_greater)
#     for year in logbook.years:
#         validate_year(year, parse_context)
#         for month in year.months:
#             validate_month(month, parse_context)
#             for trip in month.trips:
#                 validate_trip(trip, parse_context)
#                 for dutyperiod in trip.duty_periods:
#                     validate_dutyperiod(dutyperiod, parse_context)
#                     for flight in dutyperiod.flights:
#                         validate_flight(flight, parse_context)


# def validate_year(year: model.Year, parse_context: ParseContext):
#     year.sum_of_leg_greater = parse_duration_string(year.sum_of_leg_greater)
#     year.sum_of_fly = parse_duration_string(year.sum_of_fly)
#     year.sum_of_actual_block = parse_duration_string(year.sum_of_actual_block)
#     _ = year, parse_context


# def validate_month(month: model.Month, parse_context: ParseContext):
#     month.sum_of_leg_greater = parse_duration_string(month.sum_of_leg_greater)
#     month.sum_of_fly = parse_duration_string(month.sum_of_fly)
#     month.sum_of_actual_block = parse_duration_string(month.sum_of_actual_block)

#     _ = month, parse_context


# def validate_trip(trip: model.Trip, parse_context: ParseContext):
#     _ = parse_context
#     trip.sum_of_leg_greater = parse_duration_string(trip.sum_of_leg_greater)
#     trip.sum_of_fly = parse_duration_string(trip.sum_of_fly)
#     trip.sum_of_actual_block = parse_duration_string(trip.sum_of_actual_block)

#     split_trip_info(trip)
#     # TODO check overnight lengths, some overnights are missing. infer from utc in time?
#     # FIXME output validation messages, esp, when data is infered.


# def validate_dutyperiod(dutyperiod: model.DutyPeriod, parse_context: ParseContext):
#     _ = parse_context
#     dutyperiod.sum_of_leg_greater = parse_duration_string(dutyperiod.sum_of_leg_greater)
#     dutyperiod.sum_of_fly = parse_duration_string(dutyperiod.sum_of_fly)
#     dutyperiod.sum_of_actual_block = parse_duration_string(
#         dutyperiod.sum_of_actual_block
#     )


# def validate_flight(flight: model.Flight, parse_context: ParseContext):
#     # odl has junk data, drop data when flight has a ground time? also junk data has no
#     # decimal? invalid time format?
#     _ = parse_context
#     remove_bad_odl(flight)
#     if flight.overnight_duration:
#         flight.overnight_duration = parse_duration_string(flight.overnight_duration)
#     if flight.ground_time:
#         flight.ground_time = parse_duration_string(flight.ground_time)
#     if flight.actual_block:
#         flight.actual_block = parse_duration_string(flight.actual_block)
#     if flight.leg_greater:
#         flight.leg_greater = parse_duration_string(flight.leg_greater)
#     if flight.fly:
#         flight.fly = parse_duration_string(flight.fly)
#     set_icao(flight)
#     make_tz_aware(flight)
#     check_times_against_durations(flight)


# def check_times_against_durations(flight: model.Flight):
#     _ = flight
#     # check departure and arrival times against a duration when available.


# airports: Dict = {}


# def set_icao(flight: model.Flight):
#     flight.departure_icao = airports[flight.departure_iata]["icao"]
#     flight.arrival_icao = airports[flight.arrival_iata]["icao"]


# def make_tz_aware(flight: model.Flight):
#     dep_local = datetime.fromisoformat(flight.departure_local)
#     dep_local = dep_local.replace(
#         tzinfo=ZoneInfo(airports[flight.departure_iata]["tz"])
#     )
#     flight.departure_local = dep_local.isoformat()
#     flight.departure_utc = dep_local.astimezone(timezone.utc).isoformat()
#     complete_arrival_time(dep_local, flight)
#     arr_local = datetime.fromisoformat(flight.arrival_local)
#     arr_local = arr_local.replace(tzinfo=ZoneInfo(airports[flight.arrival_iata]["tz"]))
#     flight.arrival_local = arr_local.isoformat()
#     flight.arrival_utc = arr_local.astimezone(timezone.utc).isoformat()


# def complete_arrival_time(departure: datetime, flight: model.Flight):
#     # 10/30 11:11
#     # 22:57
#     # refactor to not depend on Flight
#     dep_no_tz = departure.replace(tzinfo=None)
#     year_added = f"{departure.year}/{flight.arrival_local}"
#     try:
#         partial = datetime.strptime(year_added, "%Y/%m/%d %H:%M")
#         # check if overlaps year, eg. 12/31-1/1
#         if partial < dep_no_tz:
#             partial = partial.replace(year=departure.year + 1)
#     except ValueError as err:
#         logger.info("Attempt alternate parse: %s", err)
#         try:
#             partial = datetime.strptime(year_added, "%Y/%H:%M")
#             partial = partial.replace(month=departure.month, day=departure.day)
#             # check if overlaps day, eg. 2350-0230
#             if partial.time() < departure.time():
#                 partial = partial + timedelta(days=1)
#             # check if overlaps year, eg. 12/31-1/1
#             if partial < dep_no_tz:
#                 partial = partial.replace(year=departure.year + 1)
#         except ValueError as err_2:
#             _ = err_2
#             logger.error(
#                 "Failure to parse %s for flight %s",
#                 flight.arrival_local,
#                 flight.uuid,
#                 exc_info=True,
#             )
#             return
#     if partial < dep_no_tz:
#         logger.warning("Failed to parse the arrival time for %s", flight)
#         return
#     flight.arrival_local = partial.isoformat()


# def remove_bad_odl(flight: model.Flight):

#     if (
#         flight.overnight_duration
#         and "." not in flight.overnight_duration
#         and flight.ground_time
#     ):
#         flight.overnight_duration = ""


# def split_trip_info(trip_element: model.Trip):
#     # TODO raise a valdation error.
#     split_info = trip_element.trip_info.split()
#     if len(split_info) == 4:
#         trip_element.starts_on = split_info[0]
#         trip_element.trip_number = split_info[1]
#         trip_element.base = split_info[2]
#         trip_element.equipment = split_info[3]


# def parse_duration_string(dur_string: str) -> str:
#     pattern = pattern_HHHMM(hm_sep=".")
#     dur = parse_duration(pattern=pattern, duration_string=dur_string)
#     return duration_to_HHMMSS(**dur.asdict())


# def flatten_logbook(logbook: model.Logbook) -> List[FlightRow]:
#     rows = []
#     for year in logbook.years:
#         for month in year.months:
#             for trip in month.trips:
#                 for duty_period in trip.duty_periods:
#                     for flight in duty_period.flights:
#                         row = FlightRow(
#                             aa_number=logbook.aa_number,
#                             year=year.year,
#                             year_uuid=year.uuid,
#                             month_year=month.month_year,
#                             month_uuid=month.uuid,
#                             trip_info=trip.trip_info,
#                             trip_uuid=trip.uuid,
#                             duty_period_uuid=duty_period.uuid,
#                             flight_uuid=flight.uuid,
#                             flight_number=flight.flight_number,
#                             dp_flt=f"{duty_period.index}-{flight.index}",
#                             departure_iata=flight.departure_iata,
#                             departure_icao=flight.departure_icao,
#                             departure_local=flight.departure_local,
#                             departure_utc=flight.departure_utc,
#                             arrival_iata=flight.arrival_iata,
#                             arrival_icao=flight.arrival_icao,
#                             arrival_local=flight.arrival_local,
#                             arrival_utc=flight.arrival_utc,
#                             fly=flight.fly,
#                             leg_greater=flight.leg_greater,
#                             actual_block=flight.actual_block,
#                             ground_time=flight.ground_time,
#                             overnight_duration=flight.overnight_duration,
#                             eq_model=flight.eq_model,
#                             eq_number=flight.eq_number,
#                             eq_type=flight.eq_type,
#                             eq_code=flight.eq_code,
#                             fuel_performance=flight.fuel_performance,
#                             departure_performance=flight.departure_performance,
#                             arrival_performance=flight.arrival_performance,
#                             position=flight.position,
#                             delay_code=flight.delay_code,
#                             trip_number=trip.trip_number,
#                             trip_starts_on=trip.starts_on,
#                             bid_eq=trip.equipment,
#                             base=trip.base,
#                         )

#                         rows.append(row)
#     return rows
