from pathlib import Path

import click

from logbook_parser.apa_2023_02.parser.parse_xml_logbook import (
    parse_logbook_xml_tree,
    read_logbook_xml_file,
)
from logbook_parser.snippets.click.task_complete import task_complete
from logbook_parser.snippets.click.check_file_output_path import check_file_output_path


@click.command()
@click.argument("file_in", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("path_out", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--default_filename",
    "-d",
    is_flag=True,
    default=True,
    show_default=True,
    help="Use the default file name for the output file.",
)
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
    default_filename: bool,
):
    """"""

    element_tree = read_logbook_xml_file(file_in)
    raw_logbook = parse_logbook_xml_tree(element_tree=element_tree)
    if default_filename:
        file_name = "fix_this_filename.json"
        output_path = path_out / file_name
    else:
        output_path = path_out
    check_file_output_path(output_path=output_path, overwrite=overwrite)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(raw_logbook.json(indent=2))
    click.echo(f"Parsed file written to {output_path}")
    task_complete(ctx=ctx)
