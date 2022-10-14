####################################################
#                                                  #
#  src/snippets/datetime/parse_duration_regex.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-09-28T17:11:31-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

"""
Various duration parsing strategies using regex.
"""

import re

from .duration_dict import DurationDict

# from .duration import IsoDuration

HHH = r"(?P<hours>[0-9]+([,.][0-9]+)?)"
MM = r"(?P<minutes>[0-5][0-9])"
SS = r"(?P<seconds>[0-5][0-9])"
FS = r"(?P<fractional_seconds>([0-9]+))"

# FIXME get a dict of times first, refactor to allow timedelta or duration creation.


# def parse_iso_duration(duration_string: str) -> IsoDuration:
#     pass


def parse_duration(pattern: re.Pattern, duration_string: str) -> DurationDict:
    """
    Parse a duration string

    Supports hours minutes seconds and fractional seconds.

    Args:
        pattern: the re pattern used to parse the duration
        duration_string: The duration string to be parsed.

    Raises:
        ValueError: Exception if pattern does not match

    Returns:
        a timedelta for the duration string.
    """
    result = pattern.match(duration_string)
    if not result:
        raise ValueError(f"{duration_string} does not match pattern {pattern.pattern}")
    match_dict = result.groupdict()
    possible_groups = [
        "years",
        "days",
        "hours",
        "minutes",
        "seconds",
        "fractional_seconds",
    ]
    for unit in possible_groups:
        if unit not in match_dict or match_dict[unit] is None:
            match_dict[unit] = "0"
    dur: DurationDict = {
        "years": int(match_dict["years"]),
        "days": int(match_dict["days"]),
        "hours": int(match_dict["hours"]),
        "minutes": int(match_dict["minutes"]),
        "seconds": int(match_dict["seconds"]),
        "fractional_seconds": int(match_dict["fractional_seconds"]),
        "exponent": len(match_dict["fractional_seconds"]) * -1,
    }
    # match_dict["hours"] = match_dict["hours"].replace(",", "")
    # match_dict["hours"] = match_dict["hours"].replace(".", "")
    # match_dict["hours"] = int(match_dict["hours"])
    # match_dict["minutes"] = int(match_dict["minutes"])
    # match_dict[
    #     "seconds"
    # ] = f"{match_dict['seconds']}.{match_dict['fractional_seconds']}"
    # match_dict["seconds"] = float(match_dict["seconds"])
    # match_dict.pop("fractional_seconds")

    # print(match_dict)
    # return timedelta(**match_dict)  # type: ignore
    return dur


def pattern_HHHMMSSFS(
    hm_sep: str = ":", ms_sep: str = ":", fs_sep: str = "."
) -> re.Pattern:
    """
    Parse a string duration of the pattern HHHMMSSFS.

    Some valid formats:
    0:00:01
    123:14:35
    123:15:34.456

    _extended_summary_

    Args:
        hm_sep: _description_. Defaults to ":".
        ms_sep: _description_. Defaults to ":".
        fs_sep: _description_. Defaults to ".".

    Returns:
        _description_
    """
    pattern_string = rf"{HHH}{hm_sep}{MM}{ms_sep}{SS}({fs_sep}{FS})?"
    return re.compile(pattern_string)


def pattern_HHHMM(hm_sep: str = ":") -> re.Pattern:
    pattern_string = rf"{HHH}{hm_sep}{MM}"
    return re.compile(pattern_string)
