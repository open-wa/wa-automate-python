# Regression tests

Install the project dependencies and setuptools in your development environment:

```sh
python -m pip install -r requirements.txt setuptools
```

Run from the repository root:

```sh
python -m unittest discover -s tests -v
```

The tests exercise package version extraction through the setup CLI and unread-message
conversion with a mocked WAPI response. They run without starting a browser or connecting
to WhatsApp. Run them on Python 3.14 to check the compatibility regressions.
