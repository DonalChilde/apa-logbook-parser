"""
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import logbook_parser.models.logbook_model as model
from logbook_parser.parse_context import ParseContext
from logbook_parser.util.safe_strip import safe_strip

logger = logging.getLogger(__name__)
ns = {"crystal_reports": "urn:crystal-reports:schemas:report-detail"}


def parse_logbook(path: Path, parse_context: ParseContext) -> model.Logbook:
    # print(path.resolve())
    with open(path, "r", encoding="utf-8") as xml_file:
        tree = ET.parse(xml_file)
        root: ET.Element = tree.getroot()
        logbook = model.Logbook()
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
            logbook.years.append(parse_year(item, parse_context))
        return logbook


def logbook_stats(logbook: model.Logbook, parse_context: dict):
    """
    Logbook: total times in the 3 duration fields, total months, total dutyperiods
        total flights, total dh flights,total overnights, nights at each station.
    year:
    month:
    dutyperiod:
    flight:
    """
    raise NotImplementedError


def parse_year(element: ET.Element, parse_context: ParseContext) -> model.Year:
    # print('made it to year')
    year = model.Year()
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
        year.months.append(parse_month(item, parse_context))
    return year


def parse_month(element: ET.Element, parse_context: ParseContext) -> model.Month:
    # print('made it to month')
    month = model.Month()
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
        month.trips.append(parse_trip(item, parse_context))
    return month


def find_value(element: ET.Element, xpath: str) -> str:
    if element is not None:
        return safe_strip(
            element.find(  # type: ignore
                xpath,
                ns,
            ).text
        )
    raise NotImplementedError("got None element?")


def parse_trip(element: ET.Element, parse_context: ParseContext) -> model.Trip:

    trip = model.Trip()

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

    for index, item in enumerate(element.findall("crystal_reports:Group", ns)):
        parse_context.extra["dutyperiod_index"] = str(index)
        trip.duty_periods.append(parse_dutyperiod(item, parse_context))
    return trip


def parse_dutyperiod(
    element: ET.Element, parse_context: ParseContext
) -> model.DutyPeriod:
    dutyperiod = model.DutyPeriod()
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports"
        ':Field[@Name="{}"]/crystal_reports:Value'
    )
    dutyperiod.index = parse_context.extra["dutyperiod_index"]
    dutyperiod.sum_of_actual_block = find_value(
        element, field_path.format("SumofActualBlock1")
    )
    dutyperiod.sum_of_leg_greater = find_value(
        element, field_path.format("SumofLegGtr1")
    )
    dutyperiod.sum_of_fly = find_value(element, field_path.format("SumofFly1"))
    for index, item in enumerate(element.findall("crystal_reports:Details", ns)):
        parse_context.extra["flight_index"] = str(index)
        dutyperiod.flights.append(parse_flight(item, parse_context))
    return dutyperiod


def parse_flight(element: ET.Element, parse_context: ParseContext) -> model.Flight:
    _ = parse_context
    flight = model.Flight()
    field_path = (
        "./crystal_reports:Section/crystal_reports:Field"
        "[@Name='{}']/crystal_reports:Value"
    )
    flight.index = parse_context.extra["flight_index"]
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
    return flight
