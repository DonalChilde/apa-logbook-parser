####################################################
#                                                  #
#   src/snippets/click/check_file_output_path.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-28T09:36:48-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

from pathlib import Path

import click


def check_file_output_path(output_path: Path, overwrite: bool):
    """
    Check that the output path is not a directory, and check for file overwrite.


    Args:
        output_path: Path to the output file.
        overwrite: Allow overwrite

    Raises:
        click.BadArgumentUsage: _description_
        click.BadParameter: _description_
    """
    if output_path.is_dir():
        # True if output_path is an existing directory
        raise click.BadArgumentUsage(
            f"The file output path is {output_path}, but thats an existing directory."
        )
    if output_path.is_file() and not overwrite:
        raise click.BadParameter(
            f"There is an existing file at {output_path} and overwrite was not selected."
        )
