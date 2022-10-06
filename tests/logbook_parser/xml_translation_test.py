from pathlib import Path
from logbook_parser.xml_translation import (
    dataclass_to_csv,
    flatten_flights,
    parse_XML,
)
from logbook_parser.models.xml_element_model import LogbookElement


def test_parse_xml(report_data_ctx):
    with report_data_ctx as file_path:
        data = parse_XML(file_path, {})
        print(data)
        assert data.aa_number == "420357"


def test_write_flat_to_csv(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parse_XML(file_path, {})
    flat_data = flatten_flights(data)
    file_out = test_app_data_dir / "csv_out.csv"
    dataclass_to_csv(file_out, flat_data)


def test_flatten_flights(report_data_ctx):
    with report_data_ctx as file_path:
        data = parse_XML(file_path, {})
    flat_data = flatten_flights(data)
    assert len(flat_data) > 100


def test_dataclass_to_csv(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parse_XML(file_path, {})
    flat_data = flatten_flights(data)
    file_out = test_app_data_dir / "csv_out.csv"
    skips = "year_uuid"
    dataclass_to_csv(file_out, flat_data, skips)
    # assert False


def test_dataclass_to_csv_skip_uuid(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parse_XML(file_path, {})
    flat_data = flatten_flights(data)
    file_out = test_app_data_dir / "csv_out_no_uuid.csv"
    skips = "year_uuid month_uuid trip_uuid duty_period_uuid flight_uuid"
    dataclass_to_csv(file_out, flat_data, skips)
    # assert False
