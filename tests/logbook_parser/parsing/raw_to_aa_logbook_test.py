from dataclasses import asdict
from pathlib import Path

from logbook_parser.parsing.flatten_logbook import flatten_aa_logbook
from logbook_parser.parsing.raw_to_aa_logbook import translate_logbook
from logbook_parser.parsing.context import Context
from logbook_parser.parsing.parse_xml_logbook import parse_logbook
from logbook_parser.snippets.file.dicts_to_csv import dicts_to_csv


# base
def test_parse_xml(report_data_ctx):
    with report_data_ctx as file_path:
        ctx = Context()
        data = parse_logbook(file_path, ctx)
        assert data.aa_number == "420357"
        translated_data = translate_logbook(data, ctx)
        assert translated_data.trips


def test_flatten_logbook(report_data_ctx):
    with report_data_ctx as file_path:
        parse_context = Context()
        data = parse_logbook(file_path, parse_context)
    translated_data = translate_logbook(data, parse_context)
    flattened_data = flatten_aa_logbook(translated_data, parse_context)
    assert len(flattened_data) > 100


def test_write_flat_to_csv(report_data_ctx, test_app_data_dir: Path, logger):
    with report_data_ctx as file_path:
        ctx = Context()
        data = parse_logbook(file_path, ctx)
    translated_data = translate_logbook(data, ctx)
    flattened_data = flatten_aa_logbook(translated_data, ctx)
    file_out = test_app_data_dir / "aa_csv_out.csv"
    dict_gen = (asdict(x) for x in flattened_data)
    dicts_to_csv(dicts=dict_gen, output_path=file_out)
    assert file_out.exists()
