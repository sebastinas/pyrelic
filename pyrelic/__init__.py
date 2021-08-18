# Copyright 2021 Sebastian Ramacher <sebastian.ramacher@ait.ac.at>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import warnings
from typing import Optional, Sequence

from ._relic import (
    # BN
    BN,
    BN_from_int,
    neutral_BN,
    rand_BN_mod,
    rand_BN_order,
    # G1
    G1,
    generator_G1,
    hash_to_G1,
    neutral_G1,
    order,
    power_product_G1,
    product_G1,
    rand_G1,
    # G2
    G2,
    generator_G2,
    hash_to_G2,
    neutral_G2,
    power_product_G2,
    product_G2,
    rand_G2,
    # Gt
    GT,
    generator_GT,
    neutral_GT,
    product_GT,
    rand_GT,
    # pairings
    pair,
    pair_product,
)

__version__ = "0.3"
__author__ = "Sebastian Ramacher"
__license__ = "MIT"
__copyright__ = f"(C) 2021 {__author__}"


def _init() -> None:
    """Initialize relic."""

    from . import _relic
    import atexit

    needs_cleanup, core_success, pair_success = _relic._relic_init()
    if needs_cleanup:
        atexit.register(_relic._relic_clean)

    if not core_success:
        raise RuntimeError("Failed to initialize relic (core)!")
    if not pair_success:
        raise RuntimeError("Failed to initialize relic (pairing)!")


class Relic:
    def __init__(self) -> None:
        warnings.warn(
            "Using Relic is deprecated and is no longer needed.", DeprecationWarning
        )

    def __enter__(self) -> "Relic":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass


def mul_sim_G1(
    values: Sequence[G1], scalars: Sequence[BN], base: Optional[G1] = None
) -> G1:
    warnings.warn("Use power_product_G1 instead.", DeprecationWarning)
    return power_product_G1(values, scalars, base)


def mul_sim_G2(
    values: Sequence[G2], scalars: Sequence[BN], base: Optional[G2] = None
) -> G2:
    warnings.warn("Use power_product_G2 instead.", DeprecationWarning)
    return power_product_G2(values, scalars, base)


_init()
