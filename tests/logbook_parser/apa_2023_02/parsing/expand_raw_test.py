from pathlib import Path

from logbook_parser.apa_2023_02.models.expanded import Logbook
from logbook_parser.apa_2023_02.parser import parse_xml_logbook as parser
from logbook_parser.apa_2023_02.parser.expand_raw import expand_raw_logbook
from logbook_parser.apa_2023_02.parser.parse_context import ParseContext


def test_expand_raw_logbook(report_data_ctx, test_app_data_dir: Path):
    with report_data_ctx as file_path:
        data = parser.parse_logbook(file_path=file_path)
        expanded_logbook = expand_raw_logbook(raw_log=data)
        assert data.aa_number == "420357"
        output_file = test_app_data_dir / "expand_raw" / "logbook_expanded.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(data=expanded_logbook.json(indent=2))
        # input = output_file.read_text(encoding="utf-8")
        loaded_logbook = Logbook.parse_file(output_file)
        output_loaded = Path(str(output_file))
        output_loaded = output_loaded.with_name("logbook_reloaded.json")
        output_loaded.write_text(data=loaded_logbook.json(indent=2), encoding="utf-8")
        assert expanded_logbook == loaded_logbook
