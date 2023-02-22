from pathlib import Path
from logbook_parser.apa_2023_02.parser.parse_context import ParseContext
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser


def test_parse_xml(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as filepath:
        element_tree = parser.read_logbook_xml_file(filepath=filepath)
        # ctx = ParseContext(source=str(filepath), extra={})
        data = parser.parse_logbook_xml_tree(element_tree=element_tree)
        # pp.pprint(asdict(data))
        assert data.aa_number == "420357"
        output_file = test_app_data_dir / "parse_logbook_xml" / "logbook.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(data=data.json(indent=2))
        # assert False
