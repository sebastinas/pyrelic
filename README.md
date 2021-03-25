# Python bindings for relic

`python-relic` provides Python bindings for [relic](https://github.com/relic-toolkit/relic). Note
though, that the bindings are driven by my personal needs and they do not cover the full `relic`
API.

## Dependencies

* `Cython >= 0.28` (optional, only for building). If Cython is not available, the C files are not
  regenerated from their source.
* `relic >= 0.5.0`
* `pkgconfig` (optional, only for building)

## Quick installation guide

If you are running Ubuntu 20.04, the easiest way to install `python-relic` is via my PPA:
```sh
sudo add-apt-repository -u ppa:s-ramacher/ait
sudo apt install python3-pyrelic
```
It comes with a prebuilt version of `relic` configured for the pairing-friendly BLS12-381 curve.

Otherwise, python-relic` can be installed via `pip`:
```sh
pip install python-relic
```
or by running:
```sh
python3 setup.py install
```
Note though that these two approaches require a pairing-enabled build of `relic` to be available.

## License

The code is licensed under the MIT license.
