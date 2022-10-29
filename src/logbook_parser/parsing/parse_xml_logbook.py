"""
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import logbook_parser.models.raw_logbook as model
from logbook_parser.parsing.context import Context
from logbook_parser.util.safe_strip import safe_strip

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
            aa_number=find_value(root, header_field_path.format("EmpNum1")),
            sum_of_actual_block=find_value(
                root, footer_field_path.format("SumofActualBlock4")
            ),
            sum_of_leg_greater=find_value(
                root, footer_field_path.format("SumofLegGtr4")
            ),
            sum_of_fly=find_value(root, footer_field_path.format("SumofFly4")),
        )
        for item in root.findall("crystal_reports:Group", ns):
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
        year=find_value(element, text_path.format("Text34")),
        sum_of_actual_block=find_value(element, field_path.format("SumofActualBlock6")),
        sum_of_leg_greater=find_value(element, field_path.format("SumofLegGtr6")),
        sum_of_fly=find_value(element, field_path.format("SumofFly6")),
    )
    for item in element.findall("crystal_reports:Group", ns):
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
        month_year=find_value(element, text_path.format("Text35")),
        sum_of_actual_block=find_value(element, field_path.format("SumofActualBlock2")),
        sum_of_leg_greater=find_value(element, field_path.format("SumofLegGtr2")),
        sum_of_fly=find_value(element, field_path.format("SumofFly2")),
    )
    for item in element.findall("crystal_reports:Group", ns):
        month.trips.append(parse_trip(item, ctx))
    return month


def find_value(element: ET.Element, xpath: str) -> str:
    if element is not None:
        value = safe_strip(
            element.find(  # type: ignore
                xpath,
                ns,
            ).text
        )
        return value or ""
    return ""


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
        trip_info=find_value(element, text_path.format("Text10")),
        sum_of_actual_block=find_value(element, field_path.format("SumofActualBlock3")),
        sum_of_leg_greater=find_value(element, field_path.format("SumofLegGtr3")),
        sum_of_fly=find_value(element, field_path.format("SumofFly3")),
    )
    for index, item in enumerate(element.findall("crystal_reports:Group", ns)):
        ctx.extra["dutyperiod_index"] = str(index + 1)
        trip.dutyperiods.append(parse_dutyperiod(item, ctx))
    return trip


def parse_dutyperiod(element: ET.Element, ctx: Context) -> model.DutyPeriod:

    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports"
        ':Field[@Name="{}"]/crystal_reports:Value'
    )
    dutyperiod = model.DutyPeriod(
        index=ctx.extra["dutyperiod_index"],
        sum_of_actual_block=find_value(element, field_path.format("SumofActualBlock1")),
        sum_of_leg_greater=find_value(element, field_path.format("SumofLegGtr1")),
        sum_of_fly=find_value(element, field_path.format("SumofFly1")),
    )
    for index, item in enumerate(element.findall("crystal_reports:Details", ns)):
        ctx.extra["flight_index"] = str(index + 1)
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
        flight_number=find_value(element, field_path.format("Flt1")),
        departure_iata=find_value(element, field_path.format("DepSta1")),
        departure_local=find_value(element, field_path.format("OutDtTime1")),
        arrival_iata=find_value(element, field_path.format("ArrSta1")),
        fly=find_value(element, field_path.format("Fly1")),
        leg_greater=find_value(element, field_path.format("LegGtr1")),
        eq_model=find_value(element, field_path.format("Model1")),
        eq_number=find_value(element, field_path.format("AcNum1")),
        eq_type=find_value(element, field_path.format("EQType1")),
        eq_code=find_value(element, field_path.format("LeqEq1")),
        ground_time=find_value(element, field_path.format("Grd1")),
        overnight_duration=find_value(element, field_path.format("DpActOdl1")),
        fuel_performance=find_value(element, field_path.format("FuelPerf1")),
        departure_performance=find_value(element, field_path.format("DepPerf1")),
        arrival_performance=find_value(element, field_path.format("ArrPerf1")),
        actual_block=find_value(element, field_path.format("ActualBlock1")),
        position=find_value(element, field_path.format("ActulaPos1")),
        delay_code=find_value(element, field_path.format("DlyCode1")),
        arrival_local=find_value(element, field_path.format("InDateTimeOrMins1")),
    )
    return flight
