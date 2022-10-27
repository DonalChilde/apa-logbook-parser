####################################################
#                                                  #
# src/snippets/datetime/complete_partial_datetime.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-27T10:37:56-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
import time
from calendar import isleap
from datetime import datetime, timedelta, tzinfo

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def complete_fwd_time(
    start: datetime,
    future: str,
    tz_info: tzinfo | None,
    strf: str = "%H:%M:%S",
) -> datetime:
    if start.tzinfo is None and tz_info is not start.tzinfo:
        raise ValueError("tz_info must be None if ref_datetime.tzinfo is None.")
    parsed = time.strptime(future, strf)
    partial = datetime(
        year=start.year,
        month=start.month,
        day=start.day,
        hour=parsed.tm_hour,
        minute=parsed.tm_min,
        second=parsed.tm_sec,
        tzinfo=tz_info,
    )

    if partial < start:
        increment = timedelta(days=1)
        logger.debug("adding %s to %s", increment, partial.isoformat())
        partial = partial + increment
    if partial < start:
        raise ValueError(
            f"fwd time {partial.isoformat()} still shows as "
            f"less than ref {start.isoformat()}"
        )
    return partial


def complete_fwd_mdt(
    start: datetime,
    future: str,
    tz_info: tzinfo | None,
    strf: str = "%m/%d %H:%M",
) -> datetime:
    if start.tzinfo is None and tz_info is not start.tzinfo:
        raise ValueError("tz must be None if ref_datetime.tzinfo is None.")
    # Use time.strptime because datetime.strptime will not parse 02/29 without a valid year
    parsed = time.strptime(future, strf)
    year = start.year
    if parsed.tm_mon == 2 and parsed.tm_mday == 29:
        # if the start year is not a leap year, find the next leap year.
        while not isleap(year):
            year += 1
    partial = datetime(
        year=year,
        month=parsed.tm_mon,
        day=parsed.tm_mday,
        hour=parsed.tm_hour,
        minute=parsed.tm_min,
        second=parsed.tm_sec,
        tzinfo=tz_info,
    )
    # partial = datetime.strptime(partial_string, strf)
    # partial = partial.replace(
    #     year=ref_datetime.year,
    #     tzinfo=tz_info,
    # )
    if partial < start:
        logger.debug("adding one year to %s", partial.isoformat())
        partial = partial.replace(year=partial.year + 1)

    if partial < start:
        raise ValueError(
            f"fwd time {partial.isoformat()} still shows as "
            f"less than ref {start.isoformat()}"
        )
    return partial


# def complete_partial_datetime(ref_datetime: datetime, partial_string: str) -> datetime:
#     # 10/30 11:11
#     # 22:57
#     ref_tz = ref_datetime.tzinfo
#     if ref_tz:
#         ref_no_tz = ref_datetime.replace(tzinfo=None)
#     else:
#         ref_no_tz = ref_datetime
#     year_added = f"{ref_no_tz.year}/{partial_string}"
#     try:
#         partial = datetime.strptime(year_added, "%Y/%m/%d %H:%M")
#         # check if overlaps year, eg. 12/31-1/1
#         if partial < ref_no_tz:
#             partial = partial.replace(year=ref_no_tz.year + 1)
#     except ValueError as err:
#         logger.info("%s", err)
#         try:
#             partial = datetime.strptime(year_added, "%Y/%H:%M")
#             partial = partial.replace(month=ref_no_tz.month, day=ref_no_tz.day)
#             # check if overlaps day, eg. 2350-0230
#             if partial.time() < ref_no_tz.time():
#                 partial = partial + timedelta(days=1)
#             # check if overlaps year, eg. 12/31-1/1
#             if partial < ref_no_tz:
#                 partial = partial.replace(year=ref_no_tz.year + 1)
#         except ValueError as err_2:
#             _ = err_2
#             logger.error(
#                 "Failure to parse %s",
#                 partial_string,
#                 exc_info=True,
#             )
#             raise err_2
#     partial = partial.replace(tzinfo=ref_tz)
#     if partial < ref_datetime:
#         error = ValueError(
#             f"Partial string {partial_string} parsed as {partial.isoformat()} "
#             f"does not come after ref of {ref_datetime.isoformat()}"
#         )
#         logger.error(error)
#         raise error
#     return partial
