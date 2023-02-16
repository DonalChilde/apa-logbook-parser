from dataclasses import asdict
from datetime import datetime, timedelta
from typing import List
import logbook_parser.models.raw_logbook as raw
import logbook_parser.models.aa_logbook as aa
from logbook_parser.parsing.context import Context
from logbook_parser.snippets.datetime.factored_duration import (
    FactoredDuration,
    duration_to_HHMMSS,
)


def flatten_raw_logbook(logbook: raw.Logbook) -> List[raw.FlightRow]:
    rows: List[raw.FlightRow] = []
    for year in logbook.years:
        for month in year.months:
            for trip in month.trips:
                for duty_period in trip.dutyperiods:
                    for flight in duty_period.flights:
                        row = raw.FlightRow(
                            aa_number=logbook.aa_number,
                            year=year.year,
                            year_uuid=str(year.uuid),
                            month_year=month.month_year,
                            month_uuid=str(month.uuid),
                            trip_info=trip.trip_info,
                            trip_uuid=str(trip.uuid),
                            duty_period_uuid=str(duty_period.uuid),
                            flight_uuid=str(flight.uuid),
                            dp_flt=f"{duty_period.index}-{flight.index}",
                            departure_iata=flight.departure_iata,
                            departure_local=flight.departure_local,
                            arrival_iata=flight.arrival_iata,
                            arrival_local=flight.arrival_local,
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
                        )
                        rows.append(row)
    return rows


def flatten_aa_logbook(logbook: aa.Logbook, ctx: Context) -> List[aa.FlightRow]:
    rows: List[aa.FlightRow] = []
    for trip in logbook.trips:
        for dutyperiod in trip.dutyperiods:
            for flight in dutyperiod.flights:
                if flight is dutyperiod.flights[0]:
                    dutyperiod_start = safe_iso(dutyperiod.start)
                else:
                    dutyperiod_start = ""
                if flight is dutyperiod.flights[-1]:
                    if dutyperiod.layover:
                        layover_duration = format_td(dutyperiod.layover.duration, ctx)
                        layover_uuid = str(dutyperiod.layover.uuid)
                    dutyperiod_end = safe_iso(dutyperiod.end)
                    duty_time = format_td(dutyperiod.end - dutyperiod.start, ctx)
                else:
                    dutyperiod_end = ""
                    layover_duration = ""
                    layover_uuid = ""
                    duty_time = ""
                row = aa.FlightRow(
                    aa_number=logbook.pilot.ident,
                    trip_starts=safe_iso(trip.dutyperiods[0].start),
                    trip_number=trip.number,
                    base=trip.base,
                    bid_equipment=trip.bid_equipment,
                    dutyperiod_start=dutyperiod_start,
                    flight_number=flight.number,
                    dp_flt_index=f"{dutyperiod.index}-{flight.index}",
                    eq_number=flight.equipment.number,
                    eq_model=flight.equipment.code,
                    eq_type=flight.equipment.type_,
                    eq_code=flight.equipment.code,
                    position=flight.position,
                    departure_airport=flight.departure_airport.iata,
                    departure_time=safe_iso(flight.departure_time),
                    departure_performance=flight.departure_performance,
                    arrival_airport=flight.arrival_airport.iata,
                    arrival_time=safe_iso(flight.arrival_time),
                    arrival_performance=flight.arrival_performance,
                    fly=format_td(flight.fly, ctx),
                    leg_greater=format_td(flight.leg_greater, ctx),
                    actual_block=format_td(flight.block, ctx),
                    ground_time=format_td(flight.ground_time, ctx),
                    dutyperiod_end=dutyperiod_end,
                    duty_time=duty_time,
                    layover_duration=layover_duration,
                    delay_code=flight.delay_code,
                    fuel_performance=flight.fuel_performance,
                    logbook_uuid=str(logbook.uuid),
                    trip_uuid=str(trip.uuid),
                    dutyperiod_uuid=str(dutyperiod.uuid),
                    flight_uuid=str(flight.uuid),
                    layover_uuid=layover_uuid,
                    equipment_uuid=str(flight.equipment.uuid),
                    departure_airport_uuid=str(flight.departure_airport.uuid),
                    arrival_airport_uuid=str(flight.arrival_airport.uuid),
                )
                rows.append(row)
    return rows


def safe_iso(dt: datetime) -> str:
    try:
        return dt.isoformat()
    except AttributeError:
        return ""


def format_td(delta: timedelta, ctx: Context) -> str:
    if delta == timedelta():
        return ""
    return duration_to_HHMMSS(**asdict(FactoredDuration.from_timedelta(delta)))
