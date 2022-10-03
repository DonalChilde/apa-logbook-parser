# links and snippets

## github badges

[Badge examples](https://github.com/Naereen/badges)

rst badge

```text
.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: black

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
   :target: https://pycqa.github.io/isort/
   :alt: isort

.. image:: https://img.shields.io/badge/type%20checked-mypy-blue.svg
   :target: https://github.com/python/mypy
   :alt: mypy
```

markdown badges

```text
[![Code style: black][black-badge]](https://github.com/psf/black)
[![Imports: isort][isort-badge]](https://pycqa.github.io/isort/)
[![Type checked with mypy][mypy-badge]](https://github.com/python/mypy)

[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[isort-badge]: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
[mypy-badge]: https://img.shields.io/badge/type%20checked-mypy-blue.svg
```

## rst

- [rst Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)

### Heading Levels

Normally, there are no heading levels assigned to certain characters as the structure is determined from the succession of headings. However, it is better to stick to the same convention throughout a project. For instance:

```text
# with overline, for parts
* with overline, for chapters
=, for sections
-, for subsections
^, for subsubsections
“, for paragraphs
```

### Napolean for google style doc strings

- [Napolean](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)

## Markdown

- [MyST](https://myst-parser.readthedocs.io/en/latest/index.html)
- [CommonMark](https://spec.commonmark.org/)

## Linting

### pylint

[Pylint disable messages](https://pylint.pycqa.org/en/latest/user_guide/messages/message_control.html#messages-control)

Disable checking for a file

```python
# pylint: disable-all
# OR
# pylint: skip-file
```

Block or line level

```python
# pylint: disable=no-member
# pylint: enable=no-member
```

## Testing

## Python

### Loading package resources

[importlib.resources – Resources](https://docs.python.org/3.11/library/importlib.resources.html#module-importlib.resources)
