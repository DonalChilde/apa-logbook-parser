from pathlib import Path
from logbook_parser.logbook_parser import parse_logbook
from logbook_parser.logbook_transformations import flatten_logbook, validate_logbook
from logbook_parser.parse_context import ParseContext
from logbook_parser.util.dataclasses_to_csv import dataclasses_to_csv


def test_parse_xml(report_data_ctx):
    with report_data_ctx as file_path:
        parse_context = ParseContext()
        data = parse_logbook(file_path, parse_context)
        print(data)
        assert data.aa_number == "420357"


def test_write_flat_to_csv(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        parse_context = ParseContext()
        data = parse_logbook(file_path, parse_context)
        validate_logbook(data, parse_context)
    flat_data = flatten_logbook(data)
    file_out = test_app_data_dir / "csv_out.csv"
    dataclasses_to_csv(dataclasses=flat_data, output_path=file_out)


def test_flatten_flights(report_data_ctx):
    with report_data_ctx as file_path:
        parse_context = ParseContext()
        data = parse_logbook(file_path, parse_context)
    flat_data = flatten_logbook(data)
    assert len(flat_data) > 100


# TODO implement and test custom ordered fields
# def test_dataclass_to_csv(report_data_ctx, test_app_data_dir: Path):
#     with report_data_ctx as file_path:
#         data = parse_XML(file_path, {})
#     flat_data = flatten_flights(data)
#     file_out = test_app_data_dir / "csv_out.csv"
#     skips = "year_uuid"
#     dataclasses_to_csv(dataclasses=flat_data, output_path=file_out)
#     # assert False


# def test_dataclass_to_csv_skip_uuid(report_data_ctx, test_app_data_dir: Path):
#     with report_data_ctx as file_path:
#         data = parse_XML(file_path, {})
#     flat_data = flatten_flights(data)
#     file_out = test_app_data_dir / "csv_out_no_uuid.csv"
#     skips = "year_uuid month_uuid trip_uuid duty_period_uuid flight_uuid"
#     dataclass_to_csv(file_out, flat_data, skips)
#     # assert False
