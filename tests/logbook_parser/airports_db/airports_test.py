from datetime import datetime

from logbook_parser.airports_db.airports import from_iata


def test_iata():
    result = from_iata("DFW", datetime.now())
    assert result.iata == "DFW"
    assert result.icao == "KDFW"
