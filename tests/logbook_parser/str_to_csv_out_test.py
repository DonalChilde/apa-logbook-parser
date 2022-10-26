# def test_write_raw_to_csv(report_data_ctx, test_app_data_dir: Path):
#     with report_data_ctx as file_path:
#         parse_context = ParseContext()
#         data = parse_logbook(file_path, parse_context)
#     flat_data = flatten_raw_logbook(data)
#     file_out = test_app_data_dir / "raw_csv_out.csv"
#     dataclasses_to_csv(dataclasses=flat_data, output_path=file_out)

from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from logbook_parser.util.dicts_to_csv import dicts_to_csv


class FormattedDatetime(datetime):
    def __init__(self, *args, **kwargs) -> None:
        self.format_string = ""
        super().__init__(*args, **kwargs)

    def __str__(self):
        if not self.format_string:
            return super().__str__()
        if self.format_string.lower() == "iso":
            return self.isoformat()
        return self.strftime(self.format_string)


def test_datetime_to_str():
    utc_time = FormattedDatetime.now(timezone.utc)
    from_now = datetime.now().astimezone(tz=ZoneInfo("America/Los_Angeles"))
    from_utc = utc_time.astimezone(tz=ZoneInfo("America/Los_Angeles"))

    print(utc_time, utc_time.isoformat())
    print(from_now, from_now.isoformat())
    print(from_utc, from_utc.isoformat())
    assert False


def test_write_custom_formatted(test_app_data_dir: Path):
    data = [{"field_1": FormattedDatetime.now(timezone.utc)}]
    foo = FormattedDatetime.now(timezone.utc)
    print(foo)
    foo.format_string = "iso"
    print(foo)
    output = test_app_data_dir / "string_test.csv"
    dicts_to_csv(data, output_path=output)
