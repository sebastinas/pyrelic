0.3.1
-----

* Test with Python 3.10.
* Drop support for Python 3.6 and 3.7.
* Add an implementation of core/helper anonymous credentials as example.
* Link with `advapi32` on Windows. This is required when linking to `relic`.

0.3
---

* Add `power_product_*` and `product_sum_*` functions in favor of `mul_sim_*`. The deprecated
  `mul_sim_*` functions will be removed in version 0.4.
* Add `product_*` and `sum_*` helper functions.
* Handle some relic error cases (reading of invalid data, BN growing larger than an internal limit)
  more gracefully.

0.2.1
-----

* Add methods `is_neutral` and `set_neutral` to group elements.
* Add implementation of structure preserving signatures on equivalence classes as example.
* Extend documentation of examples.

0.2
---

* Initialize relic automatically. `with Relic(): ...` is no longer necessary and the `Relic` context
  manager will be removed in a future release.
* Add more examples including BLS signatures, Bloom Filter KEM, Boneh-Franklin IBE
* Release the GIL for some of the expensive operations.

0.1.1
-----

* Include missing pyrelic/relic.pxd in sdist

0.1
---

* Initial release
