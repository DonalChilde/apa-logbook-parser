####################################################
#                                                  #
#         src/snippets/file/json_mixin.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-03-17T15:41:59-07:00            #
# Last Modified: 2023-03-17T22:47:05.165753+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

from pathlib import Path

from logbook_parser.snippets.file.validate_file_out import validate_file_out


class JsonMixin:
    def json(self, *args, **kwargs):
        raise NotImplementedError

    def to_json(self, file_path: Path, overwrite: bool, indent: int = 2, **kwargs):
        validate_file_out(file_path=file_path, overwrite=overwrite)
        kwargs["indent"] = indent
        file_path.write_text(data=self.json(**kwargs), encoding="utf-8")
