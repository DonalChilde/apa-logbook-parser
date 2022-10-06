"""
"""
# TODO change uuid to be the string of entire data field, at least for flight.
#       this is to allow for differential exports for same logbook.
#       maybe make it a function on the FlightElement class, to support removing the
#       default uuid required to support typechecking. or change uuid to be a string type. <- this
# TODO add uuid generator to all Element classes, to be called one time after data parsing.
# TODO data structure to hold parsed info
# TODO data structure to hold parsed info, as well as interpreted info.
# TODO output parsed info to csv
# TODO output interpreted info to csv
# TODO describe data format in readme
# TODO cmdline interface
# TODO flask interface

from __future__ import annotations
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Callable, List, Dict, Literal, Sequence, NamedTuple, Optional, Any
from datetime import timedelta

# from utilities import json_util, csv_util
import logbook_parser.models.xml_element_model as xem
import uuid
import xml.etree.ElementTree as ET
import click
import json
import csv

# from sys import stdout


#### setting up logger ####
logger = logging.getLogger(__name__)

#### Log Level ####
# NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, and CRITICAL=50
log_level = logging.DEBUG
# logLevel = logging.INFO
logger.setLevel(log_level)

#### Log Handler ####
log_formatter = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
# log_handler = logging.StreamHandler(stdout)
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

ns = {"crystal_reports": "urn:crystal-reports:schemas:report-detail"}


def safe_strip(value: Any) -> Any:
    if isinstance(value, str):
        newValue = value.strip()
        return newValue
    else:
        return value


def parse_XML(path, parseContext):
    # print(path.resolve())
    with open(path, "r") as xmlFile:
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        logbook = xem.LogbookElement()
        logbook.aa_number = safe_strip(
            root.find(
                './crystal_reports:ReportHeader/crystal_reports:Section/crystal_reports:Field[@Name="EmpNum1"]/crystal_reports:Value',
                ns,
            ).text
        )
        logbook.sum_of_actual_block = safe_strip(
            root.find(
                './crystal_reports:ReportFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofActualBlock4"]/crystal_reports:Value',
                ns,
            ).text
        )
        logbook.sum_of_leg_greater = safe_strip(
            root.find(
                './crystal_reports:ReportFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofLegGtr4"]/crystal_reports:Value',
                ns,
            ).text
        )
        logbook.sum_of_fly = safe_strip(
            root.find(
                './crystal_reports:ReportFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofFly4"]/crystal_reports:Value',
                ns,
            ).text
        )
        parseContext["xmlparse"] = {}

        for item in root.findall("crystal_reports:Group", ns):
            # pylint: disable=no-member
            logbook.years.append(handleYear(item, parseContext))
        return logbook


def logbookStats(logbook: xem.LogbookElement, parseContext: dict):
    """
    Logbook: total times in the 3 duration fields, total months, total dutyperiods
        total flights, total dh flights,total overnights, nights at each station.
    year:
    month:
    dutyperiod:
    flight:
    """
    pass


def handleYear(yearElement, parseContext):
    # print('made it to year')
    year = xem.YearElement()
    year.year = safe_strip(
        yearElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text[@Name="Text34"]/crystal_reports:TextValue',
            ns,
        ).text
    )
    year.sum_of_actual_block = safe_strip(
        yearElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofActualBlock6"]/crystal_reports:Value',
            ns,
        ).text
    )
    year.sum_of_leg_greater = safe_strip(
        yearElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofLegGtr6"]/crystal_reports:Value',
            ns,
        ).text
    )
    year.sum_of_fly = safe_strip(
        yearElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofFly6"]/crystal_reports:Value',
            ns,
        ).text
    )

    for item in yearElement.findall("crystal_reports:Group", ns):
        # pylint: disable=no-member
        year.months.append(handleMonth(item, parseContext))
    validateYear(year, yearElement)

    return year


def handleMonth(monthElement, parseContext):
    # print('made it to month')
    month = xem.MonthElement()
    month.month_year = safe_strip(
        monthElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Text[@Name="Text35"]/crystal_reports:TextValue',
            ns,
        ).text
    )
    month.sum_of_actual_block = safe_strip(
        monthElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofActualBlock2"]/crystal_reports:Value',
            ns,
        ).text
    )
    month.sum_of_leg_greater = safe_strip(
        monthElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofLegGtr2"]/crystal_reports:Value',
            ns,
        ).text
    )
    month.sum_of_fly = safe_strip(
        monthElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofFly2"]/crystal_reports:Value',
            ns,
        ).text
    )

    for item in monthElement.findall("crystal_reports:Group", ns):
        # pylint: disable=no-member
        month.trips.append(handleTrip(item, parseContext))
    validateMonth(month, monthElement)
    return month


def handleTrip(tripElement, parseContext):
    # print('made it to trip')
    trip = xem.TripElement()
    trip.trip_info = safe_strip(
        tripElement.find(
            './crystal_reports:GroupHeader/crystal_reports:Section/crystal_reports:Text[@Name="Text10"]/crystal_reports:TextValue',
            ns,
        ).text
    )
    trip.sum_of_actual_block = safe_strip(
        tripElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofActualBlock3"]/crystal_reports:Value',
            ns,
        ).text
    )
    trip.sum_of_leg_greater = safe_strip(
        tripElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofLegGtr3"]/crystal_reports:Value',
            ns,
        ).text
    )
    trip.sum_of_fly = safe_strip(
        tripElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofFly3"]/crystal_reports:Value',
            ns,
        ).text
    )

    for item in tripElement.findall("crystal_reports:Group", ns):
        # pylint: disable=no-member
        trip.duty_periods.append(handleDutyPeriod(item, parseContext))
    validateTrip(trip, tripElement)
    return trip


def handleDutyPeriod(dutyPeriodElement, parseContext):
    # print('made it to dp')
    dutyPeriod = xem.DutyPeriodElement()
    dutyPeriod.sum_of_actual_block = safe_strip(
        dutyPeriodElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofActualBlock1"]/crystal_reports:Value',
            ns,
        ).text
    )
    dutyPeriod.sum_of_leg_greater = safe_strip(
        dutyPeriodElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofLegGtr1"]/crystal_reports:Value',
            ns,
        ).text
    )
    dutyPeriod.sum_of_fly = safe_strip(
        dutyPeriodElement.find(
            './crystal_reports:GroupFooter/crystal_reports:Section/crystal_reports:Field[@Name="SumofFly1"]/crystal_reports:Value',
            ns,
        ).text
    )

    for item in dutyPeriodElement.findall("crystal_reports:Details", ns):
        # pylint: disable=no-member
        dutyPeriod.flights.append(handleFlight(item, parseContext))
    # print(dutyPeriod)
    validateDutyPeriod(dutyPeriod, dutyPeriodElement)
    return dutyPeriod


def section_field_value(field_name) -> str:
    xpath_string = f"./crystal_reports:Section/crystal_reports:Field[@Name='{field_name}']/crystal_reports:Value"
    return xpath_string


def get_xpath_value(
    element: ET.ElementTree,
    field_name: str,
    namespace: str,
    xpath_builder: Callable[[str], str],
) -> str:
    value = safe_strip(element.find(xpath_builder(field_name), namespace).text)
    return value


def handleFlight(flt_ele, parse_context: Dict):
    # print('made it to flight')
    # print(flightElement.findall('.'))
    flight = xem.FlightElement()
    # flight.flightNumber = flightElement.find('./{urn:crystal-reports:schemas:report-detail}Section/{urn:crystal-reports:schemas:report-detail}Field/{urn:crystal-reports:schemas:report-detail}Value').text)
    # flight.flight_number = safe_strip(
    #     flightElement.find(
    #         './crystal_reports:Section/crystal_reports:Field[@Name="Flt1"]/crystal_reports:Value',
    #         ns,
    #     ).text
    # )
    xpath_builder = section_field_value
    flight.flight_number = get_xpath_value(flt_ele, "Flt1", ns, xpath_builder)
    flight.departure_station = get_xpath_value(flt_ele, "DepSta1", ns, xpath_builder)
    flight.out_datetime = get_xpath_value(flt_ele, "OutDtTime1", ns, xpath_builder)
    flight.arrival_station = get_xpath_value(flt_ele, "ArrSta1", ns, xpath_builder)
    flight.fly = get_xpath_value(flt_ele, "Fly1", ns, xpath_builder)
    flight.leg_greater = get_xpath_value(flt_ele, "LegGtr1", ns, xpath_builder)
    flight.eq_model = get_xpath_value(flt_ele, "Model1", ns, xpath_builder)
    flight.eq_number = get_xpath_value(flt_ele, "AcNum1", ns, xpath_builder)
    flight.eq_type = get_xpath_value(flt_ele, "EQType1", ns, xpath_builder)
    flight.eq_code = get_xpath_value(flt_ele, "LeqEq1", ns, xpath_builder)
    flight.ground_time = get_xpath_value(flt_ele, "Grd1", ns, xpath_builder)
    flight.overnight_duration = get_xpath_value(flt_ele, "DpActOdl1", ns, xpath_builder)
    flight.fuel_performance = get_xpath_value(flt_ele, "FuelPerf1", ns, xpath_builder)
    flight.departure_performance = get_xpath_value(
        flt_ele, "DepPerf1", ns, xpath_builder
    )
    flight.arrival_performance = get_xpath_value(flt_ele, "ArrPerf1", ns, xpath_builder)
    flight.actual_block = get_xpath_value(flt_ele, "ActualBlock1", ns, xpath_builder)
    flight.position = get_xpath_value(flt_ele, "ActulaPos1", ns, xpath_builder)
    flight.delay_code = get_xpath_value(flt_ele, "DlyCode1", ns, xpath_builder)
    flight.in_datetime = get_xpath_value(
        flt_ele, "InDateTimeOrMins1", ns, xpath_builder
    )

    validateFlight(flight, flt_ele)
    return flight


def validateYear(year, yearElement):
    pass


def validateMonth(month, monthElement):
    pass


def validateTrip(trip, tripElement):
    pass


def validateDutyPeriod(dutyPeriod, dutyPeriodElement):
    pass


def validateFlight(flight, flightElement):
    # odl has junk data, drop data when flight has a ground time? also junk data has no
    # decimal? invalid time format?
    pass


def flatten_flights(logbook: xem.LogbookElement) -> List[xem.FlightRow]:
    rows = []
    for year in logbook.years:
        for month in year.months:
            for trip in month.trips:
                for duty_period in trip.duty_periods:
                    for flight in duty_period.flights:
                        row = xem.FlightRow(
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
                            departure_iata=flight.departure_station,
                            departure_lcl=flight.out_datetime,
                            arrival_iata=flight.arrival_station,
                            arrival_local=flight.in_datetime,
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
                        )
                        split_trip_info = row.trip_info.split()
                        if len(split_trip_info) == 4:
                            row.trip_starts_on = split_trip_info[0]
                            row.trip_number = split_trip_info[1]
                            row.base = split_trip_info[2]
                            row.bid_eq = split_trip_info[3]
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


def dataclass_to_csv(file_out: Path, data: List, skip_fields: str = ""):

    # TODO use final version from snippets.
    fieldnames = list(asdict(data[0]).keys())
    skips = skip_fields.split()
    for skip in skips:
        fieldnames.remove(skip)
    if skips:
        extras: Literal["raise", "ignore"] = "ignore"
    else:
        extras = "raise"
    with open(file_out, "w", newline="") as csv_file:
        print("in the open")
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction=extras)
        writer.writeheader()
        for row in data:
            writer.writerow(asdict(row))


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
