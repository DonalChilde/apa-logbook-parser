import logging
from pathlib import Path
from time import perf_counter_ns

import click

from apa_logbook_parser.cli.parse import parse

PROJECT_SLUG = "unique_name_for_project"
APP_DIR = click.get_app_dir(PROJECT_SLUG)
LOG_DIR = Path(APP_DIR).expanduser() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# If logging to file, ensure a log file handler is attatched.
logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("--verbose", "-v", count=True)
@click.pass_context
def main(ctx: click.Context, debug: bool, verbose: int):
    """A stub with verbose and debug flag capabilities."""
    # ensure that ctx.obj exists and is a dict (in case `main()` is called
    # by means other than the `if __name__` block below)
    click.echo(f"logging at {LOG_DIR}")
    ctx.ensure_object(dict)
    ctx.obj["START_TIME"] = perf_counter_ns()
    ctx.obj["DEBUG"] = debug
    click.echo(f"Verbosity: {verbose}")
    ctx.obj["VERBOSE"] = verbose


main.add_command(parse)
