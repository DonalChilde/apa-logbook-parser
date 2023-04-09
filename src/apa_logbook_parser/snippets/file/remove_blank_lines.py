####################################################
#                                                  #
#     src/snippets/file/strip_blank_lines.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-29T08:58:58-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from pathlib import Path

from apa_logbook_parser.snippets.file.validate_file_out import validate_file_out


def remove_blank_lines(input_path: Path, output_path: Path, overwrite: bool = False):
    """Make a copy of a file, removing blank lines"""
    validate_file_out(output_path, overwrite)
    with open(input_path, encoding="utf-8") as file_in, open(
        output_path, "w", encoding="utf-8"
    ) as file_out:
        for line in file_in:
            if line.strip():
                file_out.write(line)
