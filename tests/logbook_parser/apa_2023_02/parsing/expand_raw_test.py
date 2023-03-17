from pathlib import Path

from logbook_parser.apa_2023_02.models.expanded import Logbook
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser
from logbook_parser.apa_2023_02.parser.expand_raw import expand_raw_logbook


def test_expand_raw_logbook(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parser.parse_logbook(file_path=file_path)
        expanded_logbook = expand_raw_logbook(raw_log=data)
        assert data.aa_number == "420357"
        output_file = test_app_data_dir / "expand_raw" / "logbook_expanded.json"
        expanded_logbook.to_json(output_file, overwrite=True)
        # input = output_file.read_text(encoding="utf-8")
        loaded_logbook = Logbook.parse_file(output_file)
        loaded_output_path = Path(str(output_file))
        loaded_output_path = loaded_output_path.with_name("logbook_reloaded.json")
        loaded_logbook.to_json(loaded_output_path, overwrite=True)
        assert expanded_logbook == loaded_logbook


# def test_json_mixin(report_data_ctx, test_app_data_dir: Path):
#     with report_data_ctx as file_path:
#         data = parser.parse_logbook(file_path=file_path)
#         expanded_logbook = expand_raw_logbook(raw_log=data)
#         assert data.aa_number == "420357"
#         output_file = test_app_data_dir / "expand_raw" / "logbook_expanded_mixin.json"
#         expanded_logbook.to_json(file_path=output_file, overwrite=True)
