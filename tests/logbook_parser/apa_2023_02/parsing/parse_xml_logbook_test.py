from pathlib import Path

from logbook_parser.apa_2023_02.models.raw import Logbook
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser


def test_parse_xml(report_data_ctx):
    with report_data_ctx as file_path:
        element_tree = parser.read_logbook_xml_file(file_path=file_path)
        raw_logbook = parser.parse_logbook_xml_tree(element_tree=element_tree)
        assert raw_logbook.aa_number == "420357"


def test_parse_xml_to_json(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        raw_logbook = parser.parse_logbook(file_path=file_path)
        assert raw_logbook.aa_number == "420357"
        output_file = (
            test_app_data_dir / "parse_logbook_xml" / raw_logbook.default_file_name()
        )
        raw_logbook.to_json(output_file, overwrite=True)
        assert output_file.is_file()

        loaded_logbook = Logbook.parse_file(output_file)
        loaded_output_path = Path(str(output_file))
        loaded_output_path = loaded_output_path.with_name("logbook_reloaded.json")
        loaded_logbook.to_json(loaded_output_path, overwrite=True)
        assert raw_logbook == loaded_logbook


def test_parse_xml_to_string(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        raw_logbook = parser.parse_logbook(file_path=file_path)
        assert raw_logbook.aa_number == "420357"
        assert "AA Number: 420357" in str(raw_logbook)
        # print(raw_logbook)
        # assert False
