####################################################
#                                                  #
#       src/snippets/string/safe_strip.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-14T09:03:59-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import TypeVar

T = TypeVar("T")


def safe_strip(value: T) -> T | str:
    """
    Strip white space from strings, return non-strings unchanged.

    Useful when working with varied data, and you only care that the
    strings get stripped.

    Args:
        value: The string to be stripped, or the non string to return.

    Returns:
        A stripped string, or the unchanged non-string value.
    """
    if isinstance(value, str):
        new_value = value.strip()
        return new_value
    return value
