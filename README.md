# Python bindings for relic

`python-relic` (`pyrelic` for short) provides Python bindings for
[relic](https://github.com/relic-toolkit/relic). Note though, that the bindings are driven by my
personal needs and they do not cover the full `relic` API.

## Dependencies

* `Cython >= 0.28` (optional, only for building). If Cython is not available, the C files are not
  regenerated from their source.
* `relic >= 0.5.0`
* `pkgconfig` (optional, only for building)

## Quick installation guide

If you are running Ubuntu 20.04, the easiest way to install `pyrelic` is via my PPA:
```sh
sudo add-apt-repository -u ppa:s-ramacher/ait
sudo apt install python3-pyrelic
```
It comes with a prebuilt version of `relic` configured for the pairing-friendly BLS12-381 curve.

Otherwise, pyrelic` can be installed via `pip`:
```sh
pip install python-relic
```
or by running:
```sh
python3 setup.py install
```
Note though that these two approaches require a pairing-enabled build of `relic` to be available.

## Examples

`pyrelic` includes some examples that demonstrate the use of the module and also showcases some
pairing-based schemes:
* `examples/bls.py`: Implements the Boneh-Lynn-Shacham signature scheme.
* `examples/bfibe.py`: Implements the Boneh-Franklin identity-based encryption scheme (BasicIdent).
* `examples/hpra.py`: Implements homomorphic proxy re-authenticators for linear functions.
* `examples/bfe.py`: Imeplemnts Bloom Filter KEM based on the BF IBE.

## License

The code is licensed under the MIT license.
