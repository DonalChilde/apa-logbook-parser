from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import ClassVar, List, Dict
from uuid import UUID, uuid5, NAMESPACE_DNS

from logbook_parser.airports_db.airport import Airport

logbook_parser_uuid = uuid5(NAMESPACE_DNS, "logbook_parser.pfmsoft.com")


@dataclass(frozen=True)
class Equipment:

    uuid: UUID
    number: str
    model: str
    type_: str
    code: str
    equipment: ClassVar[Dict[str, "Equipment"]] = {}  # type: ignore

    @classmethod
    def from_sig(cls, number: str, model: str, type_: str, code: str) -> "Equipment":

        equip_hash = hash((number, model, type_, code))
        equip_uuid = uuid5(logbook_parser_uuid, str(equip_hash))
        equip = Equipment(
            uuid=equip_uuid, number=number, model=model, type_=type_, code=code
        )
        equip_uuid_str = str(equip_uuid)
        if equip_uuid_str in cls.equipment:
            return cls.equipment[equip_uuid_str]
        cls.equipment[equip_uuid_str] = equip
        return equip


@dataclass
class Layover:
    uuid: UUID
    location: str
    duration: timedelta


# @dataclass
# class EquipmentList:
#     equipment_list: List[Equipment]


@dataclass
class Pilot:
    uuid: UUID
    ident: str


@dataclass
class Flight:
    uuid: UUID
    index: str
    number: str
    equipment: Equipment
    position: str
    departure_airport: Airport
    departure_time: datetime
    departure_performance: str
    arrival_airport: Airport
    arrival_time: datetime
    arrival_performance: str
    fly: timedelta
    block: timedelta
    leg_greater: timedelta
    fuel_performance: str
    ground_time: timedelta
    delay_code: str


@dataclass
class DutyPeriod:
    uuid: UUID
    index: str
    start: datetime
    end: datetime
    layover: Layover | None = None
    flights: List[Flight] = field(default_factory=list)


@dataclass
class Trip:
    uuid: UUID
    number: str
    start: datetime
    end: datetime
    base: str
    bid_equipment: str
    dutyperiods: List[DutyPeriod] = field(default_factory=list)


@dataclass
class Logbook:
    uuid: UUID
    pilot: Pilot
    equipment: List[Equipment] = field(default_factory=list)
    airports: List[Airport] = field(default_factory=list)
    trips: List[Trip] = field(default_factory=list)

    def start(self) -> datetime:
        return self.trips[0].start

    def end(self) -> datetime:
        return self.trips[-1].end


@dataclass
class FlightRow:
    aa_number: str
    trip_starts: str
    trip_number: str
    base: str
    bid_equipment: str
    dp_flt_index: str
    dutyperiod_start: str
    flight_number: str
    eq_number: str
    position: str
    departure_airport: str
    departure_time: str
    departure_performance: str
    arrival_airport: str
    arrival_time: str
    arrival_performance: str
    fly: str
    leg_greater: str
    actual_block: str
    ground_time: str
    dutyperiod_end: str
    duty_time: str
    layover_duration: str
    delay_code: str
    fuel_performance: str
    eq_model: str
    eq_type: str
    eq_code: str
    logbook_uuid: str
    trip_uuid: str
    dutyperiod_uuid: str
    flight_uuid: str
    layover_uuid: str
    equipment_uuid: str
    departure_airport_uuid: str
    arrival_airport_uuid: str
