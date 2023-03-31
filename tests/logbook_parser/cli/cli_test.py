from pathlib import Path
from click.testing import CliRunner
from logbook_parser.cli.main import main


def test_parse_cli(report_data_ctx, test_app_data_dir: Path):
    runner = CliRunner()
    output_path = test_app_data_dir / "cli_parse"
    with report_data_ctx as file_path:
        result = runner.invoke(main, ["parse", str(file_path), str(output_path)])
    result_msg_path = output_path / "result_msg.txt"
    result_msg_path.write_text(result.output)
    assert result.exit_code == 0
    assert "logbook" in result.output
