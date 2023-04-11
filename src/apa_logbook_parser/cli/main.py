import logging
from pathlib import Path
from time import perf_counter_ns

import click

from apa_logbook_parser.cli.parse import parse

PROJECT_SLUG = "pfmsoft_apa_logbook_parser"
APP_DIR = click.get_app_dir(PROJECT_SLUG)
LOG_DIR = Path(APP_DIR).expanduser() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# If logging to file, ensure a log file handler is attatched.
logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug/--no-debug", default=False, help="Not currently in use.")
@click.option("--verbose", "-v", count=True, help="Not currently in use.")
@click.pass_context
def main(ctx: click.Context, debug: bool, verbose: int):
    """apa-logbook-parser is a tool to transform the XML version of the APA Logbook to other formats.

    1. Go to https://tasc.alliedpilots.org/LogData/LogView.aspx and export/download your logbook in XML format.

    2. try apa-logbook-parser parse <path to XML file> <output directory>

    This should output a number of files, including:
    \n\t- a formatted version of the original XML data file for easier reference.
    \n\t- a json file containing the raw parsed data.
    \n\t- a json file containing a flattened version of the raw parsed data.
    \n\t- a csv file containing a flattened version of the raw parsed data.
    \n\t- a json file containing an expanded version of the parsed data.
    \n\t- a json file containing a flattened expanded version of the parsed data.
    \n\t- a csv file containing the flattened expanded version of the parsed data.

    Most people will only use the csv version of the expanded logbook for import into a spreadsheet.
    The other formats are included for easier error diagnosis, and future uses.

    The expanded format transforms the original data to include:
    \n\t- departure and arrival times in both local and utc
    \n\t- timezone names for each station
    \n\t- durations in 00:00:00 (HH:MM:SS) format for ease of use in spreadsheets.
    \n\t- a row number based on the order of flights found in the source XML file.
    \n\t- A unique identifier (UUID) based on the original data parsed for each flight.
    \n\t\tThis id -should- remain unique through different downloads of a logbook, so long as APAs data does not change.

    The data available is limited by the source data.
    There is no way to determine actual duty in, duty out, or layover location from the data provided by APA.


    """
    # ensure that ctx.obj exists and is a dict (in case `main()` is called
    # by means other than the `if __name__` block below)
    click.echo(f"logging at {LOG_DIR}")
    ctx.ensure_object(dict)
    ctx.obj["START_TIME"] = perf_counter_ns()
    ctx.obj["DEBUG"] = debug
    click.echo(f"Verbosity: {verbose}")
    ctx.obj["VERBOSE"] = verbose


main.add_command(parse)
