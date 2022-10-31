####################################################
#                                                  #
#      src/snippets/xml/format_xml_file.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-29T09:19:30-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from pathlib import Path
from xml.dom.minidom import parse

from .remove_blank_lines import remove_blank_lines
from .validate_file_out import validate_file_out


def format_xml_file(
    input_path: Path,
    output_path: Path,
    *,
    indent: str = "  ",
    strip_blank_lines: bool = True,
    overwrite: bool = False,
):
    if strip_blank_lines:
        file_out = Path(f"{output_path.resolve()}.temp")
        validate_file_out(file_out, overwrite)
        validate_file_out(output_path, overwrite)
    else:
        file_out = output_path
        validate_file_out(file_out, overwrite)

    file_in_str = str(input_path)
    dom = parse(file=file_in_str)
    with open(file_out, mode="w", encoding="utf-8") as output:
        output.write(dom.toprettyxml(indent=indent, newl="\n"))
    if strip_blank_lines:
        remove_blank_lines(file_out, output_path, overwrite)
        # remove the temp file
        file_out.unlink()
