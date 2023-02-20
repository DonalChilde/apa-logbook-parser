from logbook_parser.apa_2023_02.models.raw import (
    DutyPeriod,
    Flight,
    FlightRow,
    Logbook,
    Month,
    Trip,
    Year,
)

# FIXME dp_index and row_idx are not in order.


def flatten_logbook(logbook: Logbook) -> list[FlightRow]:
    rows = []
    last_row_index = 1
    for year in logbook.years:
        flat = flatten_year(
            year=year,
            last_row_idx=last_row_index,
            aa_number=logbook.aa_number,
        )
        last_row_index = flat[-1].row_idx
        rows.extend(flat)
    return rows


def flatten_year(
    year: Year,
    last_row_idx: int,
    aa_number: str,
) -> list[FlightRow]:
    rows = []
    for month in year.months:
        flat = flatten_month(
            month=month,
            last_row_idx=last_row_idx,
            aa_number=aa_number,
            year=year.year,
        )
        last_row_idx = flat[-1].row_idx
        rows.extend(flat)
    return rows


def flatten_month(
    month: Month,
    last_row_idx: int,
    aa_number: str,
    year: str,
) -> list[FlightRow]:
    rows = []
    for trip in month.trips:
        flat = flatten_trip(
            trip=trip,
            last_row_idx=last_row_idx,
            aa_number=aa_number,
            year=year,
            month_year=month.month_year,
        )
        last_row_idx = flat[-1].row_idx
        rows.extend(flat)
    return rows


def flatten_trip(
    trip: Trip,
    last_row_idx: int,
    aa_number: str,
    year: str,
    month_year: str,
) -> list[FlightRow]:
    rows = []
    for dutyperiod in trip.duty_periods:
        flat = flatten_dutyperiod(
            dutyperiod=dutyperiod,
            last_row_idx=last_row_idx,
            aa_number=aa_number,
            year=year,
            month_year=month_year,
            trip_info=trip.trip_info,
        )
        # TODO what if no flights in a dutyperiod
        last_row_idx = flat[-1].row_idx
        rows.extend(flat)
    return rows


def flatten_dutyperiod(
    dutyperiod: DutyPeriod,
    last_row_idx: int,
    aa_number: str,
    year: str,
    month_year: str,
    trip_info: str,
) -> list[FlightRow]:
    rows = []
    for row_idx, flight in enumerate(dutyperiod.flights, start=last_row_idx + 1):
        row = make_row(
            flight=flight,
            row_idx=row_idx,
            aa_number=aa_number,
            year=year,
            month_year=month_year,
            trip_info=trip_info,
            dp_idx=dutyperiod.dp_idx,
        )
        rows.append(row)
    return rows


def make_row(
    flight: Flight,
    row_idx: int,
    aa_number: str,
    year: str,
    month_year: str,
    trip_info: str,
    dp_idx: int,
):
    flight_row = FlightRow(
        row_idx=row_idx,
        aa_number=aa_number,
        year=year,
        month_year=month_year,
        trip_info=trip_info,
        dp_idx=dp_idx,
        flight_idx=flight.flight_idx,
        eq_number=flight.eq_number,
        eq_model=flight.eq_model,
        eq_type=flight.eq_type,
        eq_code=flight.eq_code,
        position=flight.position,
        departure_iata=flight.departure_iata,
        departure_local=flight.departure_local,
        departure_performance=flight.departure_performance,
        arrival_iata=flight.arrival_iata,
        arrival_local=flight.arrival_local,
        arrival_performance=flight.arrival_performance,
        fly=flight.fly,
        leg_greater=flight.leg_greater,
        actual_block=flight.actual_block,
        ground_time=flight.ground_time,
        overnight_duration=flight.overnight_duration,
        delay_code=flight.delay_code,
        fuel_performance=flight.fuel_performance,
        row_uuid="",
    )
    return flight_row
