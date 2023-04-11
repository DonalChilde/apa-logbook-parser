from pathlib import Path

from apa_logbook_parser.snippets.file.validate_file_out import validate_file_out


class PydanticJsonMixin:
    def json(self, *args, **kwargs):
        raise NotImplementedError

    def to_json(self, file_path: Path, overwrite: bool, indent: int = 2, **kwargs):
        validate_file_out(file_path=file_path, overwrite=overwrite)
        file_path.write_text(data=self.json(indent=indent, **kwargs), encoding="utf-8")
