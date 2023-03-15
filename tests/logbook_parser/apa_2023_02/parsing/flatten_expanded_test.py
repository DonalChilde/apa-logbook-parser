from csv import DictWriter
from itertools import chain
from pathlib import Path

from logbook_parser.apa_2023_02.models.expanded_flat import ExpandedFlatLogbook
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser
from logbook_parser.apa_2023_02.parser.expand_raw import expand_raw_logbook
from logbook_parser.apa_2023_02.parser.flatten_expanded import LogbookFlattener


def test_flatten_expanded(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parser.parse_logbook(file_path=file_path)
        expanded_logbook = expand_raw_logbook(raw_log=data)
        assert data.aa_number == "420357"
        output_file = test_app_data_dir / "flatten_expanded" / "flattened_expanded.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        flattener = LogbookFlattener()
        flattened_log = flattener.flatten_logbook(expanded_logbook)
        output_file.write_text(data=flattened_log.json(indent=2))
        loaded_logbook = ExpandedFlatLogbook.parse_file(output_file)
        output_loaded = Path(str(output_file))
        output_loaded = output_loaded.with_name("logbook_reloaded.json")
        output_loaded.write_text(data=loaded_logbook.json(indent=2), encoding="utf-8")
        assert flattened_log == loaded_logbook


def test_csv_out(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parser.parse_logbook(file_path=file_path)
        expanded_logbook = expand_raw_logbook(raw_log=data)
        assert data.aa_number == "420357"
        output_file = test_app_data_dir / "flatten_expanded" / "flattened_expanded.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        flattener = LogbookFlattener()
        flattened_log = flattener.flatten_logbook(expanded_logbook)
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            data = iter(flattened_log.as_dicts())
            first = next(data)
            field_names = list(first.keys())
            writer = DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            for row in chain([first], data):
                writer.writerow(row)
