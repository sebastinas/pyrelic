# Python bindings for relic

`python-relic` (`pyrelic` for short) provides Python bindings for
[relic](https://github.com/relic-toolkit/relic). Note though, that the bindings are driven by my
personal needs and they do not cover the full `relic` API.

## Dependencies

`pyrelic` requires the following dependencies to successfully build and install:
* `relic >= 0.5.0` with pairing support enabled.
* `Cython >= 0.28` (optional, only for building). If Cython is not available, the C files are not
  regenerated from their source.
* `pkgconfig` (optional, only for building). If `pkgconfig` is not available, the build system
  assumes that `relic` can be linked as `-lrelic`.

## Quick installation guide

If you are running Ubuntu 20.04, the easiest way to install `pyrelic` is via my
[PPA](https://launchpad.net/~s-ramacher/+archive/ubuntu/ait):
```sh
sudo add-apt-repository -u ppa:s-ramacher/ait
sudo apt install python3-pyrelic
```
It comes with a pre-built version of `relic` configured for the pairing-friendly BLS12-381 curve.

Otherwise, `pyrelic` can be installed via `pip`:
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
* `examples/bls.py`: Implements the [Boneh-Lynn-Shacham signature
  scheme](https://doi.org/10.1007%2Fs00145-004-0314-9).
* `examples/bfibe.py`: Implements the [Boneh-Franklin identity-based encryption
  scheme](https://doi.org/10.1007/3-540-44647-8_13) (BasicIdent).
* `examples/hpra.py`: Implements [homomorphic proxy
  re-authenticators](https://doi.org/10.1007/978-3-319-70972-7_7) for linear functions.
* `examples/bfe.py`: Implements [Bloom Filter KEM](https://doi.org/10.1007/978-3-319-78372-7_14)
  based on the BF IBE.
* `examples/spseq.py`: Implements a [structure-preserving signature
  scheme on equivalence classes](https://doi.org/10.1007/978-3-662-45611-8_26).
* `examples/chac`: Implements [core/helper anonymous
  credentials](https://doi.org/10.1145/3460120.3484582).

## License

The code is licensed under the MIT license and was written by Sebastian Ramacher (AIT Austrian
Institute of Technology).

## Acknowledgements

This work has been partially funded by the European Union’s Horizon 2020
research and innovation programme under grant agreement No 871473
([KRAKEN](https://krakenh2020.eu/)) and by ECSEL Joint Undertaking under grant
agreement No 826610 ([Comp4Drones](https://www.comp4drones.eu/)).
