from pathlib import Path

from logbook_parser.apa_2023_02.models.raw_flat import FlatLogbook
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser
from logbook_parser.apa_2023_02.parser.flatten_raw import flatten_logbook


def test_flatten_logbook(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        raw_logbook = parser.parse_logbook(file_path=file_path)
        flat_raw_logbook = flatten_logbook(raw_logbook)
        assert raw_logbook.aa_number == "420357"
        output_file = (
            test_app_data_dir
            / "flatten_raw_logbook"
            / flat_raw_logbook.default_file_name()
        )
        flat_raw_logbook.to_json(output_file, overwrite=True)

        loaded_logbook = FlatLogbook.parse_file(output_file)
        loaded_output_path = Path(str(output_file))
        loaded_output_path = loaded_output_path.with_name("logbook_reloaded.json")
        loaded_logbook.to_json(loaded_output_path, overwrite=True)
        assert flat_raw_logbook == loaded_logbook


def test_csv_out(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        raw_logbook = parser.parse_logbook(file_path=file_path)
        flat_raw_logbook = flatten_logbook(raw_logbook)
        assert raw_logbook.aa_number == "420357"
        output_file = test_app_data_dir / "flatten_raw_logbook" / "logbook.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        flat_raw_logbook.to_csv(file_path=output_file, overwrite=True)
        assert output_file.is_file()


def test_to_str(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        raw_logbook = parser.parse_logbook(file_path=file_path)
        assert raw_logbook.aa_number == "420357"
        flat_raw_logbook = flatten_logbook(raw_logbook)
        assert "AA Number: 420357" in str(flat_raw_logbook)
        # print(flat_raw_logbook)
        # assert False
