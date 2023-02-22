import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from logbook_parser.apa_2023_02.models import raw

logger = logging.getLogger(__name__)
NS = {"crystal_reports": "urn:crystal-reports:schemas:report-detail"}


def read_logbook_xml_file(filepath: Path) -> ET.ElementTree:
    with open(filepath, "r", encoding="utf-8") as xml_file:
        tree = ET.parse(xml_file)
    return tree


def parse_logbook_xml_tree(element_tree: ET.ElementTree) -> raw.Logbook:
    root: ET.Element = element_tree.getroot()
    header_field_path = (
        "./crystal_reports:ReportHeader/crystal_reports:Section/crystal_reports"
        ':Field[@Name="{}"]/crystal_reports:Value'
    )
    footer_field_path = (
        "./crystal_reports:ReportFooter/crystal_reports:Section/crystal_reports"
        ':Field[@Name="{}"]/crystal_reports:Value'
    )
    logbook = raw.Logbook(
        aa_number=find_text_value(
            root, header_field_path.format("EmpNum1"), namespaces=NS
        ),
        sum_of_actual_block=find_text_value(
            root, footer_field_path.format("SumofActualBlock4"), namespaces=NS
        ),
        sum_of_leg_greater=find_text_value(
            root, footer_field_path.format("SumofLegGtr4"), namespaces=NS
        ),
        sum_of_fly=find_text_value(
            root, footer_field_path.format("SumofFly4"), namespaces=NS
        ),
        years=[],
    )
    for item in root.findall("crystal_reports:Group", namespaces=NS):
        logbook.years.append(parse_year(item))
    return logbook


def parse_year(element: ET.Element) -> raw.Year:
    # print('made it to year')

    text_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text"
        '[@Name="Text34"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="SumofActualBlock6"]/crystal_reports:Value'
    )
    year = raw.Year(
        year=find_text_value(element, text_path.format("Text34"), namespaces=NS),
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock6"), namespaces=NS
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr6"), namespaces=NS
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly6"), namespaces=NS
        ),
        months=[],
    )
    for item in element.findall("crystal_reports:Group", namespaces=NS):
        year.months.append(parse_month(item))
    return year


def parse_month(element: ET.Element) -> raw.Month:
    # print('made it to month')

    text_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text"
        '[@Name="{}"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="{}"]/crystal_reports:Value'
    )
    month = raw.Month(
        month_year=find_text_value(element, text_path.format("Text35"), namespaces=NS),
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock2"), namespaces=NS
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr2"), namespaces=NS
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly2"), namespaces=NS
        ),
        trips=[],
    )
    for item in element.findall("crystal_reports:Group", namespaces=NS):
        month.trips.append(parse_trip(item))
    return month


def parse_trip(element: ET.Element) -> raw.Trip:
    text_path = (
        "./crystal_reports:GroupHeader/crystal_reports:Section/crystal_reports:Text"
        '[@Name="{}"]/crystal_reports:TextValue'
    )
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field"
        '[@Name="SumofActualBlock3"]/crystal_reports:Value'
    )
    trip = raw.Trip(
        trip_info=find_text_value(element, text_path.format("Text10"), namespaces=NS),
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock3"), namespaces=NS
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr3"), namespaces=NS
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly3"), namespaces=NS
        ),
        duty_periods=[],
    )
    for idx, item in enumerate(
        element.findall("crystal_reports:Group", namespaces=NS), start=1
    ):
        trip.duty_periods.append(parse_dutyperiod(item, str(idx)))
    return trip


def parse_dutyperiod(element: ET.Element, dutyperiod_idx: str) -> raw.DutyPeriod:
    field_path = (
        "./crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports"
        ':Field[@Name="{}"]/crystal_reports:Value'
    )
    dutyperiod = raw.DutyPeriod(
        dp_idx=dutyperiod_idx,
        sum_of_actual_block=find_text_value(
            element, field_path.format("SumofActualBlock1"), namespaces=NS
        ),
        sum_of_leg_greater=find_text_value(
            element, field_path.format("SumofLegGtr1"), namespaces=NS
        ),
        sum_of_fly=find_text_value(
            element, field_path.format("SumofFly1"), namespaces=NS
        ),
        flights=[],
    )
    for idx, item in enumerate(
        element.findall("crystal_reports:Details", namespaces=NS), start=1
    ):
        dutyperiod.flights.append(parse_flight(item, str(idx)))
    return dutyperiod


def parse_flight(element: ET.Element, flight_idx: str) -> raw.Flight:
    field_path = (
        "./crystal_reports:Section/crystal_reports:Field"
        "[@Name='{}']/crystal_reports:Value"
    )
    flight = raw.Flight(
        flight_idx=flight_idx,
        flight_number=find_text_value(
            element, field_path.format("Flt1"), namespaces=NS
        ),
        departure_iata=find_text_value(
            element, field_path.format("DepSta1"), namespaces=NS
        ),
        departure_local=find_text_value(
            element, field_path.format("OutDtTime1"), namespaces=NS
        ),
        arrival_iata=find_text_value(
            element, field_path.format("ArrSta1"), namespaces=NS
        ),
        fly=find_text_value(element, field_path.format("Fly1"), namespaces=NS),
        leg_greater=find_text_value(
            element, field_path.format("LegGtr1"), namespaces=NS
        ),
        eq_model=find_text_value(element, field_path.format("Model1"), namespaces=NS),
        eq_number=find_text_value(element, field_path.format("AcNum1"), namespaces=NS),
        eq_type=find_text_value(element, field_path.format("EQType1"), namespaces=NS),
        eq_code=find_text_value(element, field_path.format("LeqEq1"), namespaces=NS),
        ground_time=find_text_value(element, field_path.format("Grd1"), namespaces=NS),
        overnight_duration=find_text_value(
            element, field_path.format("DpActOdl1"), namespaces=NS
        ),
        fuel_performance=find_text_value(
            element, field_path.format("FuelPerf1"), namespaces=NS
        ),
        departure_performance=find_text_value(
            element, field_path.format("DepPerf1"), namespaces=NS
        ),
        arrival_performance=find_text_value(
            element, field_path.format("ArrPerf1"), namespaces=NS
        ),
        actual_block=find_text_value(
            element, field_path.format("ActualBlock1"), namespaces=NS
        ),
        position=find_text_value(
            element, field_path.format("ActulaPos1"), namespaces=NS
        ),
        delay_code=find_text_value(
            element, field_path.format("DlyCode1"), namespaces=NS
        ),
        arrival_local=find_text_value(
            element, field_path.format("InDateTimeOrMins1"), namespaces=NS
        ),
    )
    return flight


def find_text_value(
    element: ET.Element, xpath: str, namespaces: dict[str, str] | None = None
) -> str:
    """
    Get the text value from an element.

    Returns an empty string if element not found, or element does not have text.

    Args:
        element: _description_
        xpath: _description_
        namespaces: _description_. Defaults to None.

    Returns:
        The text value with whitespace stripped.
    """
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
