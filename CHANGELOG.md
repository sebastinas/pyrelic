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
