"""
"""


import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List
from zoneinfo import ZoneInfo

import airportsdata

import logbook_parser.models.xml_element_model as xem
from logbook_parser.models.flight_row import FlightRow
from logbook_parser.util.parse_duration_regex import parse_duration, pattern_HHHMM
from logbook_parser.util.safe_strip import safe_strip
from logbook_parser.util.publisher_consumer import MessagePublisher

logger = logging.getLogger(__name__)
ns = {"crystal_reports": "urn:crystal-reports:schemas:report-detail"}
airports = airportsdata.load("IATA")  # key is IATA code


class ParseContext:
    def __init__(self, msg_pub: MessagePublisher | None = None) -> None:
        if msg_pub is None:
            self.msg_pub = MessagePublisher(consumers=[])
        else:
            self.msg_pub = msg_pub
        self.extra: Dict = {}


def parse_XML(path: Path, parse_context: ParseContext) -> xem.LogbookElement:
    # print(path.resolve())
    with open(path, "r", encoding="utf-8") as xml_file:
        tree = ET.parse(xml_file)
        root: ET.Element = tree.getroot()
        logbook = xem.LogbookElement()
        header_field_path = (
            "./crystal_reports:ReportHeader/crystal_reports:Section/crystal_reports"
            ':Field[@Name="{}"]/crystal_reports:Value'
        )
        footer_field_path = (
            "./crystal_reports:ReportFooter/crystal_reports:Section/crystal_reports"
            ':Field[@Name="{}"]/crystal_reports:Value'
        )
        logbook.aa_number = find_value(root, header_field_path.format("EmpNum1"))
        logbook.sum_of_actual_block = find_value(
            root, footer_field_path.format("SumofActualBlock4")
        )
        logbook.sum_of_leg_greater = find_value(
            root, footer_field_path.format("SumofLegGtr4")
        )
        logbook.sum_of_fly = find_value(root, footer_field_path.format("SumofFly4"))

        for item in root.findall("crystal_reports:Group", ns):
            logbook.years.append(handle_year(item, parse_context))
        return logbook


def logbook_stats(logbook: xem.LogbookElement, parse_context: dict):
    """
    Logbook: total times in the 3 duration fields, total months, total dutyperiods
        total flights, total dh flights,total overnights, nights at each station.
    year:
    month:
    dutyperiod:
    flight:
    """
    raise NotImplementedError


def handle_year(element: ET.Element, parse_context: ParseContext) -> xem.YearElement:
    # print('made it to year')
    year = xem.YearElement()
    text_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text"
        '[@Name="Text34"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="SumofActualBlock6"]/crystal_reports:Value'
    )
    year.year = find_value(element, text_path.format("Text34"))

    year.sum_of_actual_block = find_value(
        element, field_path.format("SumofActualBlock6")
    )

    year.sum_of_leg_greater = find_value(element, field_path.format("SumofLegGtr6"))

    year.sum_of_fly = find_value(element, field_path.format("SumofFly6"))

    for item in element.findall("crystal_reports:Group", ns):
        # pylint: disable=no-member
        year.months.append(handle_month(item, parse_context))
    validate_year(year, element, parse_context)

    return year


def handle_month(element: ET.Element, parse_context: ParseContext) -> xem.MonthElement:
    # print('made it to month')
    month = xem.MonthElement()
    text_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text"
        '[@Name="{}"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="{}"]/crystal_reports:Value'
    )
    month.month_year = find_value(element, text_path.format("Text35"))
    month.sum_of_actual_block = find_value(
        element, field_path.format("SumofActualBlock2")
    )

    month.sum_of_leg_greater = find_value(element, field_path.format("SumofLegGtr2"))

    month.sum_of_fly = find_value(element, field_path.format("SumofFly2"))

    for item in element.findall("crystal_reports:Group", ns):
        # pylint: disable=no-member
        month.trips.append(handleTrip(item, parse_context))
    validate_month(month, element, parse_context)
    return month


def find_value(element: ET.Element, xpath: str) -> str:
    if element is not None:
        return safe_strip(
            element.find(
                xpath,
                ns,
            ).text
        )
    raise NotImplementedError("got None element?")


def handleTrip(element: ET.Element, parse_context: ParseContext) -> xem.TripElement:

    trip = xem.TripElement()

    text_path = (
        "./crystal_reports:GroupHeader/crystal_reports:Section/crystal_reports:Text"
        '[@Name="{}"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="SumofActualBlock3"]/crystal_reports:Value'
    )
    trip.trip_info = find_value(
        element,
        text_path.format("Text10"),
    )
    trip.sum_of_actual_block = find_value(
        element,
        field_path.format("SumofActualBlock3"),
    )
    trip.sum_of_leg_greater = find_value(
        element,
        field_path.format("SumofLegGtr3"),
    )
    trip.sum_of_fly = find_value(
        element,
        field_path.format("SumofFly3"),
    )

    for item in element.findall("crystal_reports:Group", ns):
        # pylint: disable=no-member
        trip.duty_periods.append(handle_duty_period(item, parse_context))
    validate_trip(trip, element, parse_context)
    return trip


def handle_duty_period(
    element: ET.Element, parse_context: ParseContext
) -> xem.DutyPeriodElement:
    duty_period = xem.DutyPeriodElement()
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports"
        ':Field[@Name="{}"]/crystal_reports:Value'
    )
    duty_period.sum_of_actual_block = find_value(
        element, field_path.format("SumofActualBlock1")
    )
    duty_period.sum_of_leg_greater = find_value(
        element, field_path.format("SumofLegGtr1")
    )
    duty_period.sum_of_fly = find_value(element, field_path.format("SumofFly1"))
    for item in element.findall("crystal_reports:Details", ns):
        # pylint: disable=no-member
        duty_period.flights.append(handle_flight(item, parse_context))
    validate_duty_period(duty_period, element, parse_context)
    return duty_period


def handle_flight(
    element: ET.Element, parse_context: ParseContext
) -> xem.FlightElement:
    _ = parse_context
    flight = xem.FlightElement()
    field_path = (
        "./crystal_reports:Section/crystal_reports:Field"
        "[@Name='{}']/crystal_reports:Value"
    )
    flight.flight_number = find_value(element, field_path.format("Flt1"))
    flight.departure_iata = find_value(element, field_path.format("DepSta1"))
    flight.departure_local = find_value(element, field_path.format("OutDtTime1"))
    flight.arrival_iata = find_value(element, field_path.format("ArrSta1"))
    flight.fly = find_value(element, field_path.format("Fly1"))
    flight.leg_greater = find_value(element, field_path.format("LegGtr1"))
    flight.eq_model = find_value(element, field_path.format("Model1"))
    flight.eq_number = find_value(element, field_path.format("AcNum1"))
    flight.eq_type = find_value(element, field_path.format("EQType1"))
    flight.eq_code = find_value(element, field_path.format("LeqEq1"))
    flight.ground_time = find_value(element, field_path.format("Grd1"))
    flight.overnight_duration = find_value(element, field_path.format("DpActOdl1"))
    flight.fuel_performance = find_value(element, field_path.format("FuelPerf1"))
    flight.departure_performance = find_value(element, field_path.format("DepPerf1"))
    flight.arrival_performance = find_value(element, field_path.format("ArrPerf1"))
    flight.actual_block = find_value(element, field_path.format("ActualBlock1"))
    flight.position = find_value(element, field_path.format("ActulaPos1"))
    flight.delay_code = find_value(element, field_path.format("DlyCode1"))
    flight.arrival_local = find_value(element, field_path.format("InDateTimeOrMins1"))

    validate_flight(flight, element, parse_context)
    return flight


def validate_year(year, element: ET.Element, parse_context: ParseContext):
    _ = element, year, parse_context


def validate_month(month, element: ET.Element, parse_context: ParseContext):
    _ = element, month, parse_context


def validate_trip(trip, element: ET.Element, parse_context: ParseContext):
    _ = element, parse_context
    split_trip_info(trip)
    # TODO check overnight lengths, some overnights are missing. infer from utc in time?
    # FIXME output validation messages, esp, when data is infered.


def validate_duty_period(duty_period, element: ET.Element, parse_context: ParseContext):
    _ = element, duty_period, parse_context


def validate_flight(
    flight: xem.FlightElement, element: ET.Element, parse_context: ParseContext
):
    # odl has junk data, drop data when flight has a ground time? also junk data has no
    # decimal? invalid time format?
    _ = element, parse_context
    remove_bad_odl(flight)
    if flight.overnight_duration:
        flight.overnight_duration = parse_duration_string(flight.overnight_duration)
    if flight.ground_time:
        flight.ground_time = parse_duration_string(flight.ground_time)
    if flight.actual_block:
        flight.actual_block = parse_duration_string(flight.actual_block)
    if flight.leg_greater:
        flight.leg_greater = parse_duration_string(flight.leg_greater)
    if flight.fly:
        flight.fly = parse_duration_string(flight.fly)
    set_icao(flight)
    make_tz_aware(flight)
    check_times_against_durations(flight)


def check_times_against_durations(flight: xem.FlightElement):
    _ = flight
    # check departure and arrival times against a duration when available.


def set_icao(flight: xem.FlightElement):
    flight.departure_icao = airports[flight.departure_iata]["icao"]
    flight.arrival_icao = airports[flight.arrival_iata]["icao"]


def make_tz_aware(flight: xem.FlightElement):
    dep_local = datetime.fromisoformat(flight.departure_local)
    dep_local = dep_local.replace(
        tzinfo=ZoneInfo(airports[flight.departure_iata]["tz"])
    )
    flight.departure_local = dep_local.isoformat()
    flight.departure_utc = dep_local.astimezone(timezone.utc).isoformat()
    complete_arrival_time(dep_local, flight)
    arr_local = datetime.fromisoformat(flight.arrival_local)
    arr_local = arr_local.replace(tzinfo=ZoneInfo(airports[flight.arrival_iata]["tz"]))
    flight.arrival_local = arr_local.isoformat()
    flight.arrival_utc = arr_local.astimezone(timezone.utc).isoformat()


def complete_arrival_time(departure: datetime, flight: xem.FlightElement):
    # 10/30 11:11
    # 22:57
    dep_no_tz = departure.replace(tzinfo=None)
    year_added = f"{departure.year}/{flight.arrival_local}"
    try:
        partial = datetime.strptime(year_added, "%Y/%m/%d %H:%M")
        # check if overlaps year, eg. 12/31-1/1
        if partial < dep_no_tz:
            partial = partial.replace(year=departure.year + 1)
    except ValueError as err:
        logger.info("Attempt alternate parse: %s", err)
        try:
            partial = datetime.strptime(year_added, "%Y/%H:%M")
            partial = partial.replace(month=departure.month, day=departure.day)
            # check if overlaps day, eg. 2350-0230
            if partial.time() < departure.time():
                partial = partial + timedelta(days=1)
            # check if overlaps year, eg. 12/31-1/1
            if partial < dep_no_tz:
                partial = partial.replace(year=departure.year + 1)
        except ValueError as err_2:
            _ = err_2
            logger.error(
                "Failure to parse %s for flight %s",
                flight.arrival_local,
                flight.uuid,
                exc_info=True,
            )
            return
    if partial < dep_no_tz:
        logger.warning("Failed to parse the arrival time for %s", flight)
        return
    flight.arrival_local = partial.isoformat()


def remove_bad_odl(flight: xem.FlightElement):

    if (
        flight.overnight_duration
        and "." not in flight.overnight_duration
        and flight.ground_time
    ):
        flight.overnight_duration = ""


def split_trip_info(trip_element: xem.TripElement):
    # TODO raise a valdation error.
    split_info = trip_element.trip_info.split()
    if len(split_info) == 4:
        trip_element.starts_on = split_info[0]
        trip_element.trip_number = split_info[1]
        trip_element.base = split_info[2]
        trip_element.equipment = split_info[3]


def parse_duration_string(dur_string: str) -> str:
    pattern = pattern_HHHMM(hm_sep=".")
    dur = parse_duration(pattern=pattern, duration_string=dur_string)
    return f"{dur['hours']}:{dur['minutes']:02}:00"


def flatten_flights(logbook: xem.LogbookElement) -> List[FlightRow]:
    # FIXME move this to separate module
    rows = []
    for year in logbook.years:
        for month in year.months:
            for trip in month.trips:
                for dp_index, duty_period in enumerate(trip.duty_periods, start=1):
                    for flt_index, flight in enumerate(duty_period.flights, start=1):
                        row = FlightRow(
                            aa_number=logbook.aa_number,
                            year=year.year,
                            year_uuid=year.uuid,
                            month_year=month.month_year,
                            month_uuid=month.uuid,
                            trip_info=trip.trip_info,
                            trip_uuid=trip.uuid,
                            duty_period_uuid=duty_period.uuid,
                            flight_uuid=flight.uuid,
                            flight_number=flight.flight_number,
                            dp_flt=f"{dp_index}-{flt_index}",
                            departure_iata=flight.departure_iata,
                            departure_icao=flight.departure_icao,
                            departure_local=flight.departure_local,
                            departure_utc=flight.departure_utc,
                            arrival_iata=flight.arrival_iata,
                            arrival_icao=flight.arrival_icao,
                            arrival_local=flight.arrival_local,
                            arrival_utc=flight.arrival_utc,
                            fly=flight.fly,
                            leg_greater=flight.leg_greater,
                            actual_block=flight.actual_block,
                            ground_time=flight.ground_time,
                            overnight_duration=flight.overnight_duration,
                            eq_model=flight.eq_model,
                            eq_number=flight.eq_number,
                            eq_type=flight.eq_type,
                            eq_code=flight.eq_code,
                            fuel_performance=flight.fuel_performance,
                            departure_performance=flight.departure_performance,
                            arrival_performance=flight.arrival_performance,
                            position=flight.position,
                            delay_code=flight.delay_code,
                            trip_number=trip.trip_number,
                            trip_starts_on=trip.starts_on,
                            bid_eq=trip.equipment,
                            base=trip.base,
                        )

                        rows.append(row)
    return rows


# def buildFlightRows(logbook: xem.LogbookElement) -> List[Dict[str, str]]:
#     flightRows: List[Dict[str, str]] = []
#     logbookFields = {"aaNumber": logbook.aa_number}
#     for year in logbook.years:
#         yearFields = {"year": year.year}
#         for month in year.months:
#             monthFields = {"monthYear": month.monthYear}
#             for trip in month.trips:
#                 tripFields = {"sequenceInfo": trip.sequenceInfo}
#                 for dutyPeriod in trip.dutyPeriods:
#                     for flight in dutyPeriod.flights:
#                         flightFields = dc_asdict(flight)
#                         flightFields.update(logbookFields)
#                         flightFields.update(yearFields)
#                         flightFields.update(monthFields)
#                         flightFields.update(tripFields)
#                         # flightRow = FlightRow(**flightFields)
#                         flightRows.append(flightFields)
#     return flightRows


# def write_flat_to_csv(file_out: Path, flight_rows: List[xem.FlightRow]):
#     fieldnames = list(asdict(flight_rows[0]).keys())
#     with open(file_out, "w", newline="") as csv_file:
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in flight_rows:
#             writer.writerow(asdict(row))


# def dataclass_to_csv(file_out: Path, data: List, skip_fields: str = ""):

#     # TODO use final version from snippets.
#     fieldnames = list(asdict(data[0]).keys())
#     skips = skip_fields.split()
#     for skip in skips:
#         fieldnames.remove(skip)
#     if skips:
#         extras: Literal["raise", "ignore"] = "ignore"
#     else:
#         extras = "raise"
#     with open(file_out, "w", newline="") as csv_file:
#         print("in the open")
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction=extras)
#         writer.writeheader()
#         for row in data:
#             writer.writerow(asdict(row))


# def saveRawJson(xmlPath: Path, savePath: Path, parseContext: dict):

#     logbook = parseXML(xmlPath, parseContext)
#     data = logbook.to_json()  # pylint: disable=no-member
#     data = json.loads(data)
#     json_util.saveJson(data, savePath)


# def saveRawFlatJson(xmlPath: Path, savePath: Path, parseContext: dict):
#     logbook = parseXML(xmlPath, parseContext)
#     flightRows = buildFlightRows(logbook)
#     json_util.saveJson(flightRows, savePath)


# def saveRawCsv(xmlPath: Path, savePath: Path, parseContext: dict):
#     # TODO selectable save fields
#     logbook = parseXML(xmlPath, parseContext)
#     flightRows = buildFlightRows(logbook)
#     fieldList = (
#         "aaNumber",
#         "year",
#         "monthYear",
#         "sequenceInfo",
#         "uuid",
#         "flightNumber",
#         "departureStation",
#         "outDateTime",
#         "arrivalStation",
#         "inDateTime",
#         "fly",
#         "legGreater",
#         "actualBlock",
#         "groundTime",
#         "overnightDuration",
#         "eqModel",
#         "eqNumber",
#         "eqType",
#         "eqCode",
#         "fuelPerformance",
#         "departurePerformance",
#         "arrivalPerformance",
#         "position",
#         "delayCode",
#     )
#     csv_util.writeDictToCsv(savePath, flightRows, fieldList)
