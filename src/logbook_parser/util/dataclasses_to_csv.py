####################################################
#                                                  #
#    src/snippets/file/dataclass_to_csv.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-04T11:11:32-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, Optional, Sequence

from .dicts_to_csv import dicts_to_csv


def dataclasses_to_csv(
    dataclasses: Iterable,
    output_path: Path,
    parents: bool = True,
    overwrite_ok: bool = False,
    write_header: bool = True,
    fields: Optional[Sequence] = None,
    restval: Any = "",
):
    """
    Save an iterable of dataclasses to a csv file.

    If a list of fields is not provided, all fields will be output, in the order
    they are defined in the dataclass.

    Args:
        dataclasses: The dataclasses to be saved.
        output_path: Output path to the csv file.
        parents: Create missing parent directories. Defaults to True.
        overwrite_ok: Overwrite an existing file. Defaults to False.
        write_header: First line of the csv file contains column headers. Defaults to True.
        fields: Ordered list of fields to be output. Defaults to None.
        restval: Default value for missing field. Defaults to "".
    """
    dict_gen: Generator[Dict, None, None] = (asdict(x) for x in dataclasses)
    dicts_to_csv(
        dicts=dict_gen,
        output_path=output_path,
        parents=parents,
        overwrite_ok=overwrite_ok,
        write_header=write_header,
        fields=fields,
        restval=restval,
    )
