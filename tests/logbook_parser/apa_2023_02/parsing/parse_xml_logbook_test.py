from pathlib import Path
from logbook_parser.apa_2023_02.parser.parse_context import ParseContext
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser


def test_parse_xml(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        element_tree = parser.read_logbook_xml_file(file_path=file_path)
        # ctx = ParseContext(source=str(filepath), extra={})
        data = parser.parse_logbook_xml_tree(element_tree=element_tree)
        # pp.pprint(asdict(data))
        assert data.aa_number == "420357"
        output_file = test_app_data_dir / "parse_logbook_xml" / "logbook.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(data=data.json(indent=2))
        # assert False


def test_parse_xml_with_metadata(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parser.parse_logbook(file_path=file_path)
        assert data.aa_number == "420357"
        output_file = test_app_data_dir / "parse_logbook_xml" / "logbook_metadata.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(data=data.json(indent=2))
        # assert False
