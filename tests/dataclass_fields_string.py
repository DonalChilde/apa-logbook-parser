####################################################
#                                                  #
# src/snippets/code_generation/dataclass_fields_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-05T17:42:05-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

from dataclasses import asdict


def fields_string(data_class) -> str:
    """
    Make a string that is a space delimited list of a dataclass's fields.

    This is useful when serializing a dataclass to csv. Can be modified to specify
    field ordering, and skipped fields.

    Args:
        data_class: The dataclass

    Returns:
        A space delimited list of fields.
    """
    fields = asdict(data_class).keys()
    field_string = " ".join(fields)
    return field_string
