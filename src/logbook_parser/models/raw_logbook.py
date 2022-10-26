from dataclasses import asdict, dataclass, field, fields
from typing import List
from uuid import UUID, uuid4, uuid5
from logbook_parser.project_uuid import PROJECT_UUID


@dataclass
class Logbook:

    aa_number: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    uuid: UUID = field(default_factory=uuid4)
    years: List["Year"] = field(default_factory=list)

    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        # NamedTuple version
        # field_names = (field.name for field in self._fields)
        # Class version
        # field_names = (key for key in self.__dict__ if not key.startswith('_'))
        indent = " " * 4
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            rep.append(f"{indent}{field_} = {value!r}")
        rep.append(")")
        return "\n".join(rep)

    def __post_init__(self):
        sig_dict = asdict(self)
        sig_dict.pop("uuid")
        sig_dict.pop("years")
        sig = " ".join(sig_dict.values())
        self.uuid = uuid5(PROJECT_UUID, sig)


@dataclass
class Year:
    year: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    uuid: UUID = field(default_factory=uuid4)
    months: List["Month"] = field(default_factory=list)

    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        # NamedTuple version
        # field_names = (field.name for field in self._fields)
        # Class version
        # field_names = (key for key in self.__dict__ if not key.startswith('_'))
        indent = " " * 4
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            rep.append(f"{indent}{field_} = {value!r}")
        rep.append(")")
        return "\n".join(rep)

    def __post_init__(self):
        sig_dict = asdict(self)
        sig_dict.pop("uuid")
        sig_dict.pop("months")
        sig = " ".join(sig_dict.values())
        self.uuid = uuid5(PROJECT_UUID, sig)


@dataclass
class Month:
    month_year: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    uuid: UUID = field(default_factory=uuid4)
    trips: List["Trip"] = field(default_factory=list)

    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        # NamedTuple version
        # field_names = (field.name for field in self._fields)
        # Class version
        # field_names = (key for key in self.__dict__ if not key.startswith('_'))
        indent = " " * 4
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            rep.append(f"{indent}{field_} = {value!r}")
        rep.append(")")
        return "\n".join(rep)

    def __post_init__(self):
        sig_dict = asdict(self)
        sig_dict.pop("uuid")
        sig_dict.pop("trips")
        sig = " ".join(sig_dict.values())
        self.uuid = uuid5(PROJECT_UUID, sig)


@dataclass
class Trip:
    trip_info: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    uuid: UUID = field(default_factory=uuid4)
    dutyperiods: List["DutyPeriod"] = field(default_factory=list)

    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        # NamedTuple version
        # field_names = (field.name for field in self._fields)
        # Class version
        # field_names = (key for key in self.__dict__ if not key.startswith('_'))
        indent = " " * 4
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            rep.append(f"{indent}{field_} = {value!r}")
        rep.append(")")
        return "\n".join(rep)

    def __post_init__(self):
        sig_dict = asdict(self)
        sig_dict.pop("uuid")
        sig_dict.pop("dutyperiods")
        sig = " ".join(sig_dict.values())
        self.uuid = uuid5(PROJECT_UUID, sig)


@dataclass
class DutyPeriod:
    index: str
    sum_of_actual_block: str
    sum_of_leg_greater: str
    sum_of_fly: str
    uuid: UUID = field(default_factory=uuid4)
    flights: List["Flight"] = field(default_factory=list)

    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        # NamedTuple version
        # field_names = (field.name for field in self._fields)
        # Class version
        # field_names = (key for key in self.__dict__ if not key.startswith('_'))
        indent = " " * 4
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            rep.append(f"{indent}{field_} = {value!r}")
        rep.append(")")
        return "\n".join(rep)

    def __post_init__(self):
        sig_dict = asdict(self)
        sig_dict.pop("uuid")
        sig_dict.pop("flights")
        sig = " ".join(sig_dict.values())
        self.uuid = uuid5(PROJECT_UUID, sig)


@dataclass
class Flight:
    index: str
    flight_number: str
    departure_iata: str
    departure_local: str
    arrival_iata: str
    arrival_local: str
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
    uuid: UUID = field(default_factory=uuid4)

    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        # NamedTuple version
        # field_names = (field.name for field in self._fields)
        # Class version
        # field_names = (key for key in self.__dict__ if not key.startswith('_'))
        indent = " " * 4
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            rep.append(f"{indent}{field_} = {value!r}")
        rep.append(")")
        return "\n".join(rep)

    def __post_init__(self):
        sig_dict = asdict(self)
        sig_dict.pop("uuid")
        sig = " ".join(sig_dict.values())
        self.uuid = uuid5(PROJECT_UUID, sig)


@dataclass
class FlightRow:
    aa_number: str
    year: str
    month_year: str
    trip_info: str
    dp_flt: str
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
    year_uuid: str
    month_uuid: str
    trip_uuid: str
    duty_period_uuid: str
    flight_uuid: str

    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        # NamedTuple version
        # field_names = (field.name for field in self._fields)
        # Class version
        # field_names = (key for key in self.__dict__ if not key.startswith('_'))
        indent = " " * 4
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            rep.append(f"{indent}{field_} = {value!r}")
        rep.append(")")
        return "\n".join(rep)
