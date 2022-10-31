####################################################
#                                                  #
#    src/snippets/file/validate_file_out.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-29T09:11:28-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from pathlib import Path


def validate_file_out(output_path: Path, overwrite: bool):
    """Ensure that a file path is suitable for output."""
    if output_path.is_dir():
        raise ValueError(
            f"{output_path} is an invalid destination. It is an existing directory."
        )
    if not overwrite and output_path.is_file():
        raise ValueError(
            f"{output_path} is an invalid destination. "
            "It is an existing file and overwrite was not selected."
        )
