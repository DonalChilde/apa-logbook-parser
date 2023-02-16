"""
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import logbook_parser.models.raw_logbook as model
from logbook_parser.parsing.context import Context

logger = logging.getLogger(__name__)
ns = {"crystal_reports": "urn:crystal-reports:schemas:report-detail"}


def parse_logbook(path: Path, ctx: Context) -> model.Logbook:
    # print(path.resolve())
    with open(path, "r", encoding="utf-8") as xml_file:
        tree = ET.parse(xml_file)
        root: ET.Element = tree.getroot()

        header_field_path = (
            "./crystal_reports:ReportHeader/crystal_reports:Section/crystal_reports"
            ':Field[@Name="{}"]/crystal_reports:Value'
        )
        footer_field_path = (
            "./crystal_reports:ReportFooter/crystal_reports:Section/crystal_reports"
            ':Field[@Name="{}"]/crystal_reports:Value'
        )
        logbook = model.Logbook(
            aa_number=find_text_value(
                root, header_field_path.format("EmpNum1"), namespaces=ns
            ),
            sum_of_actual_block=find_text_value(
                root, footer_field_path.format("SumofActualBlock4"), namespaces=ns
            ),
            sum_of_leg_greater=find_text_value(
                root, footer_field_path.format("SumofLegGtr4"), namespaces=ns
            ),
            sum_of_fly=find_text_value(
                root, footer_field_path.format("SumofFly4"), namespaces=ns
            ),
        )
        for item in root.findall("crystal_reports:Group", namespaces=ns):
            logbook.years.append(parse_year(item, ctx))
        return logbook


def logbook_stats(logbook: model.Logbook, ctx: dict):
    """
    Logbook: total times in the 3 duration fields, total months, total dutyperiods
        total flights, total dh flights,total overnights, nights at each station.
    year:
    month:
    dutyperiod:
    flight:
    """
    raise NotImplementedError


def parse_year(element: ET.Element, ctx: Context) -> model.Year:
    # print('made it to year')

    text_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text"
        '[@Name="Text34"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="SumofActualBlock6"]/crystal_reports:Value'
    )
    year = model.Year(
        year=find_text_value(element, text_path.format("Text34"), namespaces=ns),
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock6"), namespaces=ns
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr6"), namespaces=ns
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly6"), namespaces=ns
        ),
    )
    for item in element.findall("crystal_reports:Group", namespaces=ns):
        year.months.append(parse_month(item, ctx))
    return year


def parse_month(element: ET.Element, ctx: Context) -> model.Month:
    # print('made it to month')

    text_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text"
        '[@Name="{}"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="{}"]/crystal_reports:Value'
    )
    month = model.Month(
        month_year=find_text_value(element, text_path.format("Text35"), namespaces=ns),
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock2"), namespaces=ns
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr2"), namespaces=ns
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly2"), namespaces=ns
        ),
    )
    for item in element.findall("crystal_reports:Group", namespaces=ns):
        month.trips.append(parse_trip(item, ctx))
    return month


def find_text_value(
    element: ET.Element, xpath: str, namespaces: dict[str, str] | None = None
) -> str:
    # TODO make a snippet
    found_element = element.find(xpath, namespaces)
    if found_element is None:
        logger.debug("Got None from element.find. element=%s, xpath=%s", element, xpath)
        return ""
    found_text = found_element.text
    if found_text is None:
        logger.debug("Got None as text value from %s", found_element)
        return ""
    if found_text == "":
        logger.debug("Got empty string as text value from %s", found_element)
    return found_text.strip()


def parse_trip(element: ET.Element, ctx: Context) -> model.Trip:
    text_path = (
        "./crystal_reports:GroupHeader/crystal_reports:Section/crystal_reports:Text"
        '[@Name="{}"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="SumofActualBlock3"]/crystal_reports:Value'
    )
    trip = model.Trip(
        trip_info=find_text_value(element, text_path.format("Text10"), namespaces=ns),
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock3"), namespaces=ns
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr3"), namespaces=ns
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly3"), namespaces=ns
        ),
    )
    for index, item in enumerate(
        element.findall("crystal_reports:Group", namespaces=ns), start=1
    ):
        ctx.extra["dutyperiod_index"] = str(index)
        trip.dutyperiods.append(parse_dutyperiod(item, ctx))
    return trip


def parse_dutyperiod(element: ET.Element, ctx: Context) -> model.DutyPeriod:
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports"
        ':Field[@Name="{}"]/crystal_reports:Value'
    )
    dutyperiod = model.DutyPeriod(
        index=ctx.extra["dutyperiod_index"],
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock1"), namespaces=ns
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr1"), namespaces=ns
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly1"), namespaces=ns
        ),
    )
    for index, item in enumerate(
        element.findall("crystal_reports:Details", namespaces=ns), start=1
    ):
        ctx.extra["flight_index"] = str(index)
        dutyperiod.flights.append(parse_flight(item, ctx))
    return dutyperiod


def parse_flight(element: ET.Element, ctx: Context) -> model.Flight:
    _ = ctx
    field_path = (
        "./crystal_reports:Section/crystal_reports:Field"
        "[@Name='{}']/crystal_reports:Value"
    )
    flight = model.Flight(
        index=ctx.extra["flight_index"],
        flight_number=find_text_value(
            element, field_path.format("Flt1"), namespaces=ns
        ),
        departure_iata=find_text_value(
            element, field_path.format("DepSta1"), namespaces=ns
        ),
        departure_local=find_text_value(
            element, field_path.format("OutDtTime1"), namespaces=ns
        ),
        arrival_iata=find_text_value(
            element, field_path.format("ArrSta1"), namespaces=ns
        ),
        fly=find_text_value(element, field_path.format("Fly1"), namespaces=ns),
        leg_greater=find_text_value(
            element, field_path.format("LegGtr1"), namespaces=ns
        ),
        eq_model=find_text_value(element, field_path.format("Model1"), namespaces=ns),
        eq_number=find_text_value(element, field_path.format("AcNum1"), namespaces=ns),
        eq_type=find_text_value(element, field_path.format("EQType1"), namespaces=ns),
        eq_code=find_text_value(element, field_path.format("LeqEq1"), namespaces=ns),
        ground_time=find_text_value(element, field_path.format("Grd1"), namespaces=ns),
        overnight_duration=find_text_value(
            element, field_path.format("DpActOdl1"), namespaces=ns
        ),
        fuel_performance=find_text_value(
            element, field_path.format("FuelPerf1"), namespaces=ns
        ),
        departure_performance=find_text_value(
            element, field_path.format("DepPerf1"), namespaces=ns
        ),
        arrival_performance=find_text_value(
            element, field_path.format("ArrPerf1"), namespaces=ns
        ),
        actual_block=find_text_value(
            element, field_path.format("ActualBlock1"), namespaces=ns
        ),
        position=find_text_value(
            element, field_path.format("ActulaPos1"), namespaces=ns
        ),
        delay_code=find_text_value(
            element, field_path.format("DlyCode1"), namespaces=ns
        ),
        arrival_local=find_text_value(
            element, field_path.format("InDateTimeOrMins1"), namespaces=ns
        ),
    )
    return flight
