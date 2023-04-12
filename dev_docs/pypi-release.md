# PyPI Releases

1. Create a [PyPI](https://pypi,org) account if you don't have one.
2. When your project is ready for its first release, deploy it to pypi using [twine](https://twine.readthedocs.io/en/stable/).

```bash
pip install build twine
python -m build --sdist --wheel .
twine check ./dist/*
# ensure no errors
twine upload ./dist/*
```

## Deploy via github action

1. _After at least one project release to PyPI,_ make a scoped api token for your project on the PyPI website under account settings. Save the token in a safe place, it will only be shown once.
2. Add your project specific PyPI api token to your github project's secrets with the name `PYPI_API_TOKEN`.
3. Add the following [github action](https://github.com/features/actions) to your project's .github/workflows:

```yaml
# .github/workflows/pypi-on-release.yaml
# ref: https://www.seanh.cc/2022/05/21/publishing-python-packages-from-github-actions/#the-publish-workflow
name: Publish to PyPI.org
on:
  release:
    types: [published]
jobs:
  pypi:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"
      - run: python3 -m pip install --upgrade build && python3 -m build
      - name: Publish package
        uses: pypa/gh-action-pypi-publish@release/v1.8
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

Your project will now automatically deploy to PyPI with each release.
