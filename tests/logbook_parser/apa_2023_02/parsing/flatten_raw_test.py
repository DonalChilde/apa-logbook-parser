from pathlib import Path
from logbook_parser.apa_2023_02.parser.parse_context import ParseContext
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser
from csv import DictWriter
from logbook_parser.apa_2023_02.parser.flatten_raw import flatten_logbook


def test_flatten_logbook(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as filepath:
        element_tree = parser.read_logbook_xml_file(file_path=filepath)
        # ctx = ParseContext(source=str(filepath), extra={})
        logbook = parser.parse_logbook_xml_tree(element_tree=element_tree)
        flattened = flatten_logbook(logbook)

        # pp.pprint(asdict(data))
        assert logbook.aa_number == "420357"
        output_file = test_app_data_dir / "flatten_raw_logbook" / "logbook.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            first_row = flattened[0].dict()
            writer = DictWriter(csv_file, first_row.keys())
            writer.writeheader()
            for row in flattened:
                writer.writerow(row.dict())

        # assert False
