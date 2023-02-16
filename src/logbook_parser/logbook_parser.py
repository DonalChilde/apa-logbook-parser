from dataclasses import asdict
from pathlib import Path

import click

from logbook_parser.models import aa_logbook as aa
from logbook_parser.parsing.context import Context
from logbook_parser.parsing.flatten_logbook import (
    flatten_aa_logbook,
    flatten_raw_logbook,
)
from logbook_parser.parsing.parse_xml_logbook import parse_logbook
from logbook_parser.parsing.raw_to_aa_logbook import translate_logbook
from logbook_parser.snippets.file.dicts_to_csv import dicts_to_csv
from logbook_parser.snippets.xml.format_xml_file import format_xml_file


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("--verbose", "-v", count=True)
@click.pass_context
def cli(ctx: click.Context, debug: bool, verbose: int):
    """A stub with verbose and debug flag capabilities."""
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if __name__` block below)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    click.echo(f"Verbosity: {verbose}")
    ctx.obj["VERBOSE"] = verbose


@click.command()
@click.pass_context
@click.argument("file_in", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("path_out", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--overwrite",
    "-o",
    is_flag=True,
    default=False,
    show_default=True,
    help="Allow an existing file to be overwritten.",
)
def parse(ctx: click.Context, file_in: Path, path_out: Path, overwrite: bool):
    """"""
    parse_context = Context()
    # Parse the files
    raw_logbook = parse_logbook(file_in, ctx=parse_context)
    aa_logbook = translate_logbook(raw_logbook, ctx=parse_context)
    # Determine output names
    file_prefix = logbook_effective_date_range(aa_logbook)
    output_dir = path_out / file_prefix
    table_dir = output_dir / "as_tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    ### Output the files ###
    try:
        # Formatted xml file
        format_xml_file(file_in, output_dir / f"{file_prefix}_raw_data.xml")
        # Flattened raw logbook
        flat_raw_logbook = flatten_raw_logbook(raw_logbook)
        raw_gen = (asdict(x) for x in flat_raw_logbook)
        dicts_to_csv(
            dicts=raw_gen, output_path=output_dir / f"{file_prefix}_raw_logbook.csv"
        )
        # Flattened aa logbook
        flat_aa_logbook = flatten_aa_logbook(aa_logbook, ctx=parse_context)
        aa_gen = (asdict(x) for x in flat_aa_logbook)
        dicts_to_csv(
            dicts=aa_gen, output_path=output_dir / f"{file_prefix}_aa_logbook.csv"
        )
    except ValueError as error:
        raise click.UsageError(f"Error writing file. {error}")
    # in subfolder, output as separate flat csvs suitable for db import?
    #   output flattened Trip, Dutyperiod, Flight
    #   output flattened airports
    #   output flattened equipment
    # output stats.txt


def logbook_effective_date_range(aa_logbook: aa.Logbook) -> str:
    return f"{aa_logbook.start().strftime('%Y-%m-%d')}_to_{aa_logbook.end().strftime('%Y-%m-%d')}_{aa_logbook.pilot.ident}"


cli.add_command(parse)

# if __name__ == "__main__":
#     cli(obj={})
