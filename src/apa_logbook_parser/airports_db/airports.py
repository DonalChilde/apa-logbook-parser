from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import airportsdata

from apa_logbook_parser.airports_db.airport import Airport

airports = airportsdata.load("IATA")  # key is IATA code


@dataclass
class Airports:
    airports: List[Airport]

    def iata_lookup(self, iata: str) -> Dict[str, List[Airport]]:
        pass


# make custom airport db lookup package, make cached lookup function, store past lookups
#   assuming that lookups will be repeated.


def from_iata(iata: str, date: datetime | None) -> Airport:
    _ = date
    temp = airports[iata]
    result = Airport(**temp)
    return result


# iata=temp["iata"],
#         icao=temp["icao"],
#         name=temp["name"],
#         city=temp["city"],
#         country=temp["country"],
#         elevation=temp["elevation"],
#         subd=temp["subd"],lat=temp["lat"],lon=temp[]
