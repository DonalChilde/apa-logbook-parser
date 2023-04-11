# APA Logbook Parser

<!-- badges-begin -->
[![PyPI](https://img.shields.io/pypi/v/apa-logbook-parser.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/apa-logbook-parser.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/apa-logbook-parser)][pypi status]
[![License](https://img.shields.io/pypi/l/apa-logbook-parser)][license]

[![Read the documentation at https://apa-logbook-parser.readthedocs.io/](https://img.shields.io/readthedocs/apa-logbook-parser/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/DonalChilde/apa-logbook-parser/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/DonalChilde/apa-logbook-parser/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/apa-logbook-parser/
[read the docs]: https://apa-logbook-parser.readthedocs.io/
[tests]: https://github.com/DonalChilde/apa-logbook-parser/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/DonalChilde/apa-logbook-parser
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

<!-- badges-end -->
apa-logbook-parser is a tool to transform the XML version of the APA Logbook to other formats.

1. Go to <https://tasc.alliedpilots.org/LogData/LogView.aspx> and export/download your logbook in *XML* format.
2. try ```apa-logbook-parser parse [path to XML file] [output directory]```

This should output a number of files, including:

- a formatted version of the original XML data file for easier reference.
- a json file containing the raw parsed data.
- a json file containing a flattened version of the raw parsed data.
- a csv file containing a flattened version of the raw parsed data.
- a json file containing an expanded version of the parsed data.
- a json file containing a flattened expanded version of the parsed data.
- a csv file containing the flattened expanded version of the parsed data.

Most people will only use the csv version of the expanded logbook for import into a spreadsheet.
The other formats are included for easier error diagnosis, and future uses.

The expanded format transforms the original data to include:

- departure and arrival times in both local and utc
- timezone names for each station
- durations in 00:00:00 (HH:MM:SS) format for ease of use in spreadsheets.
- a row number based on the order of flights found in the source XML file.
- A unique identifier (UUID) based on the original data parsed for each flight.
  - This id -should- remain unique through different downloads of a logbook, so long as APAs data does not change.

The data available is limited by the source data.
There is no way to determine actual duty in, duty out, or layover location from the data provided by APA.

## Requirements

This program has been tested with python version 3.10 and later. To check your python version try typing this in a terminal.

```console
python --version

# or

python3 --version
```

You should see something like this:

```console
Python 3.10.6
```

If you do not have at least Python 3.10 installed, follow these instructions to install/update python on your computer: <https://wiki.python.org/moin/BeginnersGuide/Download>

## Quickstart

You can install *apa-logbook-parser* via [pip] from [PyPI]:

```console
pip install apa-logbook-parser
```

## Usage

Please see the [documentation] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
*apa-logbook-parser* is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [DonalChilde]'s [cookiecutter-python-base] template, which was inspired by [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[DonalChilde]: https://github.com/DonalChilde
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[cookiecutter-python-base]: https://github.com/DonalChilde/cookiecutter-python-base
[file an issue]: https://github.com/DonalChilde/apa-logbook-parser/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/DonalChilde/apa-logbook-parser/blob/main/LICENSE
[contributor guide]: https://github.com/DonalChilde/apa-logbook-parser/blob/main/CONTRIBUTING
[documentation]: https://apa-logbook-parser.readthedocs.io/en/latest/
