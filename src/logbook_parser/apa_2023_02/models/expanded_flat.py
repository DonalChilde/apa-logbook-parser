from typing import Iterator
from pydantic import BaseModel

from logbook_parser.apa_2023_02.models.metadata import ParsedMetadata


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
    row_uuid: str
    metadata: str = ""


class ExpandedFlatLogbook(BaseModel):
    metadata: ParsedMetadata | None
    rows: list[ExpandedFlightRow]

    def as_dicts(self) -> Iterator[dict]:
        for idx, row in enumerate(self.rows):
            if idx == 0:
                if self.metadata is not None:
                    row.metadata = self.metadata.json()
            yield row.dict()
