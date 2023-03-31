from pathlib import Path

import click

from logbook_parser.apa_2023_02.models import expanded, raw
from logbook_parser.apa_2023_02.parser.expand_raw import expand_raw_logbook
from logbook_parser.apa_2023_02.parser.flatten_expanded import LogbookFlattener
from logbook_parser.apa_2023_02.parser.flatten_raw import flatten_logbook
from logbook_parser.apa_2023_02.parser.parse_xml_logbook import (
    parse_logbook,
    parse_logbook_xml_tree,
    read_logbook_xml_file,
)
from logbook_parser.snippets.click.task_complete import task_complete
from logbook_parser.snippets.xml.format_xml_file import format_xml_file


@click.command()
@click.argument("file_in", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("path_out", type=click.Path(file_okay=False, path_type=Path))
# @click.option(
#     "--default_filename",
#     "-d",
#     is_flag=True,
#     default=True,
#     show_default=True,
#     help="Use the default file name for the output file.",
# )
@click.option(
    "--overwrite",
    "-o",
    is_flag=True,
    default=False,
    show_default=True,
    help="Allow an existing file to be overwritten.",
)
@click.pass_context
def parse(
    ctx: click.Context,
    file_in: Path,
    path_out: Path,
    overwrite: bool,
    # default_filename: bool,
):
    """"""

    raw_logbook = parse_logbook(file_path=file_in)
    formatted_source_path = path_out / raw_logbook.default_file_name()
    formatted_source_path = formatted_source_path.with_suffix(".xml")
    write_formatted_xml_source(
        source_file=file_in, output_file=formatted_source_path, overwrite=overwrite
    )
    write_raw_logbook(raw_logbook, path_out, overwrite)
    write_flat_raw_logbook(raw_logbook, path_out, overwrite)
    expanded_logbook = expand_raw_logbook(raw_logbook)
    write_expanded_logbook(expanded_logbook, path_out, overwrite)
    write_flat_expanded_logbook(expanded_logbook, path_out, overwrite)

    task_complete(ctx=ctx)


def write_formatted_xml_source(source_file: Path, output_file: Path, overwrite: bool):
    format_xml_file(
        input_path=source_file, output_path=output_file, overwrite=overwrite
    )
    click.echo(f"Formatted source .xml written to {output_file}")


def write_raw_logbook(logbook: raw.Logbook, path_out: Path, overwrite: bool):
    file_path = path_out / logbook.default_file_name()
    logbook.to_json(file_path=file_path, overwrite=overwrite)
    click.echo(logbook.stats(str(file_path)))


def write_flat_raw_logbook(logbook: raw.Logbook, path_out: Path, overwrite: bool):
    flat_raw = flatten_logbook(logbook)
    file_path = path_out / flat_raw.default_file_name()
    flat_raw.to_json(file_path=file_path, overwrite=overwrite)
    click.echo(flat_raw.stats(str(file_path)))
    csv_file_path = file_path.with_suffix(".csv")
    flat_raw.to_csv(file_path=csv_file_path, overwrite=overwrite)
    click.echo(f"Flattened Raw logbook .csv written to {csv_file_path}\n")


def write_expanded_logbook(logbook: expanded.Logbook, path_out: Path, overwrite: bool):
    file_path = path_out / logbook.default_file_name()
    logbook.to_json(file_path=file_path, overwrite=overwrite)
    click.echo(logbook.stats(str(file_path)))


def write_flat_expanded_logbook(
    logbook: expanded.Logbook, path_out: Path, overwrite: bool
):
    flattener = LogbookFlattener()
    flat_expanded = flattener.flatten_logbook(logbook)
    file_path = path_out / flat_expanded.default_file_name()
    flat_expanded.to_json(file_path=file_path, overwrite=overwrite)
    click.echo(flat_expanded.stats(str(file_path)))
    csv_file_path = file_path.with_suffix(".csv")
    flat_expanded.to_csv(file_path=csv_file_path, overwrite=overwrite)
    click.echo(f"Flattened Expanded logbook .csv written to {csv_file_path}")
