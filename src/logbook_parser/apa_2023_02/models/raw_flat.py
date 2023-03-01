from uuid import UUID
from pydantic import BaseModel
from logbook_parser.apa_2023_02.models.metadata import ParsedMetadata


class RawFlightRow(BaseModel):
    """Represents a flattened model of Logbook.

    TODO needs refinement, include all fields, e.g. logten pro
    """

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
    row_uuid: str

    def get_uuid(self) -> UUID:
        raise NotImplementedError
