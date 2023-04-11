from pathlib import Path

from apa_logbook_parser.apa_2023_02.models.expanded_flat import ExpandedFlatLogbook
from apa_logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser
from apa_logbook_parser.apa_2023_02.parser.expand_raw import expand_raw_logbook
from apa_logbook_parser.apa_2023_02.parser.flatten_expanded import LogbookFlattener


def test_flatten_expanded(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parser.parse_logbook(file_path=file_path)
        expanded_logbook = expand_raw_logbook(raw_log=data)
        assert data.aa_number == "420357"

        flattener = LogbookFlattener()
        flattened_log = flattener.flatten_logbook(expanded_logbook)
        output_file = (
            test_app_data_dir / "flatten_expanded" / flattened_log.default_file_name()
        )
        flattened_log.to_json(output_file, overwrite=True)
        # Load logbook
        loaded_logbook = ExpandedFlatLogbook.parse_file(output_file)
        loaded_output_path = Path(str(output_file))
        loaded_output_path = loaded_output_path.with_name("logbook_reloaded.json")
        loaded_logbook.to_json(loaded_output_path, overwrite=True)
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
        flattened_log.to_csv(file_path=output_file, overwrite=True)
        assert output_file.is_file()
