from datetime import timedelta
from logbook_parser.apa_2023_02.models import expanded
from logbook_parser.apa_2023_02.models.expanded_flat import (
    ExpandedFlatLogbook,
    ExpandedFlatRow,
)


from logbook_parser.snippets.datetime.factored_duration import FactoredDuration


def serialize_timedelta(td: timedelta) -> str:
    factored = FactoredDuration.from_timedelta(td)
    result = f"{(factored.days*24)+factored.hours}:{factored.minutes}:00"
    if factored.is_negative:
        return f"-{result}"
    return result


def flatten_logbook(expanded_log: expanded.Logbook) -> ExpandedFlatLogbook:
    flat_log = ExpandedFlatLogbook(metadata=expanded_log.metadata, rows=[])
    return flat_log


def flatten_year(aa_number: str, year: expanded.Year) -> list[ExpandedFlatRow]:
    raise NotImplementedError


def flatten_month(
    aa_number: str, year: int, month: expanded.Month
) -> list[ExpandedFlatRow]:
    raise NotImplementedError


def flatten_trip(aa_number: str, year: int, month: int) -> list[ExpandedFlatRow]:
    raise NotImplementedError


def make_row(
    row_idx: int,
    aa_number: str,
    year: int,
    month: int,
    trip_start: str,
    trip_number: str,
    bid_equipment: str,
    base: str,
    dp_idx: int,
    flight: expanded.Flight,
) -> ExpandedFlatRow:
    row = ExpandedFlatRow(
        row_idx=row_idx,
        aa_number=aa_number,
        year=year,
        month=month,
        trip_start=trip_start,
        trip_number=trip_number,
        bid_equipment=bid_equipment,
        base=base,
        dp_idx=dp_idx,
        flt_idx=flight.idx,
        flight_number=flight.flight_number,
        departure_iata=flight.departure_iata,
        departure_local=flight.departure_time.local().isoformat(),
        departure_utc=flight.departure_time.utc_date.isoformat(),
        departure_tz=flight.departure_time.local_tz,
        arrival_iata=flight.arrival_iata,
        arrival_local=flight.arrival_time.local().isoformat(),
        arrival_utc=flight.arrival_time.utc_date.isoformat(),
        arrival_tz=flight.arrival_time.local_tz,
        fly=serialize_timedelta(flight.fly),
        leg_greater=serialize_timedelta(flight.leg_greater),
        actual_block=serialize_timedelta(flight.actual_block),
        eq_model=flight.eq_model,
        eq_number=flight.eq_number,
        eq_type=flight.eq_type,
        eq_code=flight.eq_code,
        ground_time=serialize_timedelta(flight.ground_time),
        overnight_duration=serialize_timedelta(flight.overnight_duration),
        fuel_performance=flight.fuel_performance,
        departure_performance=serialize_timedelta(flight.departure_performance),
        arrival_performance=serialize_timedelta(flight.arrival_performance),
        position=flight.position,
        delay_code=flight.delay_code,
        row_uuid="",
        metadata="",
    )
    return row


# TODO use a class to maintain state? row_idx?
class LogbookFlattener:
    def __init__(self) -> None:
        self.row_idx = 1

    def flatten_logbook(self, expanded_log: expanded.Logbook) -> ExpandedFlatLogbook:
        flat_log = ExpandedFlatLogbook(metadata=expanded_log.metadata, rows=[])
        return flat_log

    def flatten_year(
        self, aa_number: str, year: expanded.Year
    ) -> list[ExpandedFlatRow]:
        raise NotImplementedError

    def flatten_month(
        self, aa_number: str, year: int, month: expanded.Month
    ) -> list[ExpandedFlatRow]:
        raise NotImplementedError

    def flatten_trip(
        self, aa_number: str, year: int, month: int, trip: expanded.Trip
    ) -> list[ExpandedFlatRow]:
        for dutyperiod in trip:
            pass
        raise NotImplementedError
