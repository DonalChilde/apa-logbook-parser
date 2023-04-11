from datetime import datetime
from operator import attrgetter
from typing import Any, Callable, Iterable, Iterator

from pydantic import BaseModel

from apa_logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from apa_logbook_parser.snippets.file.dicts_to_csv import DictToCsvMixin
from apa_logbook_parser.snippets.file.json_mixin import JsonMixin


class ExpandedFlightRow(BaseModel):
    row_idx: int
    aa_number: str
    trip_start_lcl: str
    trip_number: str
    bid_equipment: str
    base: str
    dp_idx: int
    flt_idx: int
    flight_number: str
    departure_iata: str
    departure_local: str
    departure_utc: str
    departure_tz: str
    arrival_iata: str
    arrival_local: str
    arrival_utc: str
    arrival_tz: str
    fly: str
    leg_greater: str
    actual_block: str
    eq_model: str
    eq_number: str
    eq_type: str
    eq_code: str
    ground_time: str
    overnight_duration: str
    fuel_performance: str
    departure_performance: str
    arrival_performance: str
    position: str
    delay_code: str
    uuid: str
    metadata: str = ""

    def is_deadhead(self) -> bool:
        if self.position == "DH":
            return True
        return False


class ExpandedFlatLogbook(BaseModel, DictToCsvMixin, JsonMixin):
    metadata: ParsedMetadata | None
    rows: list[ExpandedFlightRow]

    def as_dicts(self, *args, **kwargs) -> Iterator[dict]:
        for idx, row in enumerate(self.rows):
            if idx == 0:
                if self.metadata is not None:
                    row.metadata = self.metadata.json()
            yield row.dict()

    def default_file_name(self) -> str:
        start_date = end_date = ""
        row = None
        for idx, row in enumerate(self.sorted()):
            if idx == 1:
                start_date = (
                    datetime.fromisoformat(row.departure_utc).date().isoformat()
                )
        if row is not None:
            end_date = datetime.fromisoformat(row.departure_utc).date().isoformat()
        return f"{self.rows[0].aa_number}-{start_date}Z-{end_date}Z-flattened-expanded-logbook.json"

    def sorted(
        self, getter: Callable[[ExpandedFlightRow], Any] = attrgetter("departure_utc")
    ) -> Iterable[ExpandedFlightRow]:
        sorted_rows = sorted(self.rows, key=getter)
        for row in sorted_rows:
            yield row

    def __str__(self) -> str:
        return self.stats()

    def stats(self, location: str = "Undefined") -> str:
        source = ""
        first = last = ""
        deadheads = 0
        row = None
        for idx, row in enumerate(self.sorted(), start=1):
            if idx == 1:
                first = row.departure_utc
            if row.is_deadhead():
                deadheads += 1
        if row is not None:
            last = row.departure_utc
        if self.metadata is not None:
            source = str(self.metadata.original_source.file_path)
        msg = (
            f"Flattened Expanded APA Logbook\n"
            f"\tLocation: {location}\n"
            f"\tParsed from: {source}\n"
            f"\tAA Number: {self.rows[0].aa_number}\n"
            f"\tFirst Departure: {first}Z\n"
            f"\tLast Departure: {last}Z\n"
            f"\tFlights: {len(self.rows)}\n"
            f"\tDeadheads: {deadheads}\n"
        )
        return msg
