from pathlib import Path
from typing import Iterator
from uuid import UUID

from pydantic import BaseModel

from logbook_parser.apa_2023_02.models.metadata import ParsedMetadata
from logbook_parser.snippets.file.dicts_to_csv import DictToCsvMixin
from logbook_parser.snippets.file.json_mixin import JsonMixin


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

    def get_uuid(self) -> UUID:
        raise NotImplementedError


class FlatLogbook(BaseModel, DictToCsvMixin, JsonMixin):
    metadata: ParsedMetadata | None
    rows: list[RawFlightRow]

    def as_dicts(self, *args, **kwargs) -> Iterator[dict]:
        for idx, row in enumerate(self.rows):
            if idx == 0:
                if self.metadata is not None:
                    row.metadata = self.metadata.json()
            yield row.dict()

    # def as_csv(self, file_path: Path, overwrite: bool):
    #     dicts_to_csv(
    #         dicts=self.as_dicts(), output_path=file_path, overwrite_ok=overwrite
    #     )
