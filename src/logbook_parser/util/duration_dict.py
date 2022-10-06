from typing import TypedDict


class DurationDict(TypedDict):
    years: int
    days: int
    hours: int
    minutes: int
    seconds: int
    fractional_seconds: int
    exponent: int
