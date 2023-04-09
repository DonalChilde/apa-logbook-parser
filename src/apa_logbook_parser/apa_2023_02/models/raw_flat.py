from datetime import datetime
from operator import attrgetter
from pathlib import Path
from typing import Iterator, Tuple
from uuid import UUID

from pydantic import BaseModel

from apa_logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from apa_logbook_parser.snippets.file.dicts_to_csv import DictToCsvMixin
from apa_logbook_parser.snippets.file.json_mixin import JsonMixin


class RawFlightRow(BaseModel):
    """Represents a flattened model of Logbook."""

    row_idx: int
    aa_number: str
    year: str
    month_year: str
    trip_info: str
    dp_idx: int
    flight_idx: int
    eq_number: str
    eq_model: str
    eq_type: str
    eq_code: str
    position: str
    departure_iata: str
    departure_local: str
    departure_performance: str
    arrival_iata: str
    arrival_local: str
    arrival_performance: str
    fly: str
    leg_greater: str
    actual_block: str
    ground_time: str
    overnight_duration: str
    delay_code: str
    fuel_performance: str
    uuid: str
    metadata: str = ""

    def is_deadhead(self) -> bool:
        if self.position == "DH":
            return True
        return False


class FlatLogbook(BaseModel, DictToCsvMixin, JsonMixin):
    metadata: ParsedMetadata | None
    rows: list[RawFlightRow]

    def as_dicts(self, *args, **kwargs) -> Iterator[dict]:
        self.rows.sort(key=attrgetter("row_idx"))
        for idx, row in enumerate(self.rows):
            if idx == 0:
                if self.metadata is not None:
                    row.metadata = self.metadata.json()
            yield row.dict()

    def __str__(self) -> str:
        return self.stats()

    def stats(self, location: str = "Undefined") -> str:
        source = ""
        first, last = self.first_and_last_departure()
        deadheads = 0
        for flight in self.rows:
            if flight.is_deadhead():
                deadheads += 1
        if self.metadata is not None:
            source = str(self.metadata.original_source.file_path)
        msg = (
            f"Flattened Raw APA Logbook\n"
            f"\tLocation: {location}\n"
            f"\tParsed from: {source}\n"
            f"\tAA Number: {self.rows[0].aa_number}\n"
            f"\tFirst Departure: {first.isoformat()}L\n"
            f"\tLast Departure: {last.isoformat()}L\n"
            f"\tFlights: {len(self.rows)}\n"
            f"\tDeadheads: {deadheads}\n"
        )
        return msg

    def default_file_name(self) -> str:
        first, last = self.first_and_last_departure()
        start_date = first.date().isoformat()
        end_date = last.date().isoformat()
        return f"{start_date}L-{end_date}L-flattened-raw-logbook.json"

    def first_and_last_departure(self) -> Tuple[datetime, datetime]:
        sorted_rows = sorted(self.rows, key=attrgetter("departure_local"))
        first_departure = datetime.fromisoformat(sorted_rows[0].departure_local)
        last_departure = datetime.fromisoformat(sorted_rows[-1].departure_local)
        return (first_departure, last_departure)
