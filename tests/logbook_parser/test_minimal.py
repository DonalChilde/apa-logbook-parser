"""The most basic test."""

from logbook_parser.minimal import hello_world


def test_hello_world():
    assert "Hello World!" == hello_world()
