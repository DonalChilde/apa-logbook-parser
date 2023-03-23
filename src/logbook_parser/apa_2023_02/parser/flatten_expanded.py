from datetime import timedelta
from operator import methodcaller

from logbook_parser.apa_2023_02.models import expanded
from logbook_parser.apa_2023_02.models.expanded_flat import (
    ExpandedFlatLogbook,
    ExpandedFlightRow,
)
from logbook_parser.snippets.datetime.factored_duration import FactoredDuration


def serialize_timedelta(td: timedelta) -> str:
    factored = FactoredDuration.from_timedelta(td)
    result = f"{((factored.days*24)+factored.hours):02d}:{factored.minutes:02d}:00"
    if factored.is_negative:
        return f"-{result}"
    return result


def make_row(
    row_idx: int,
    aa_number: str,
    trip_start_lcl: str,
    trip_number: str,
    bid_equipment: str,
    base: str,
    dp_idx: int,
    flight: expanded.Flight,
) -> ExpandedFlightRow:
    row = ExpandedFlightRow(
        row_idx=row_idx,
        aa_number=aa_number,
        trip_start_lcl=trip_start_lcl,
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
        uuid=flight.uuid,
        metadata="",
    )
    return row


class LogbookFlattener:
    def __init__(self) -> None:
        self.row_idx = 1

    def flatten_logbook(self, expanded_log: expanded.Logbook) -> ExpandedFlatLogbook:
        flat_log = ExpandedFlatLogbook(metadata=expanded_log.metadata, rows=[])
        trips = sorted(expanded_log.trips(), key=methodcaller("first_departure"))
        for trip in trips:
            flat_log.rows.extend(
                self.flatten_trip(aa_number=expanded_log.aa_number, trip=trip)
            )
        return flat_log

    def flatten_trip(
        self, aa_number: str, trip: expanded.Trip
    ) -> list[ExpandedFlightRow]:
        rows: list[ExpandedFlightRow] = []
        for dutyperiod in trip.duty_periods:
            for flight in dutyperiod.flights:
                row = make_row(
                    row_idx=self.row_idx,
                    aa_number=aa_number,
                    trip_start_lcl=trip.start_date.isoformat(),
                    trip_number=trip.trip_number,
                    bid_equipment=trip.bid_equipment,
                    base=trip.base,
                    dp_idx=dutyperiod.idx,
                    flight=flight,
                )
                self.row_idx += 1
                rows.append(row)
        return rows
