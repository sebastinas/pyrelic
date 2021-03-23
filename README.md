# Python bindings for relic

`python-relic` provides Python bindings for [relic](https://github.com/relic-toolkit/relic). Note
though, that the bindings are driven by my personal needs and they do not cover the full `relic`
API.

## Dependencies

* `Cython >= 0.28` (optional, only for building). If Cython is not available, the C files are not
  regenerated from their source.
* `relic >= 0.5.0`

## Quick installation guide

`python-relic` can be installed via `pip`:
```sh
pip install python-relic
```
or by running:
```sh
python3 setup.py install
```

## License

The code is licensed under the MIT license.
