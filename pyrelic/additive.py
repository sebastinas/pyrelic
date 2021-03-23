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

from typing import Union, Optional, Tuple, Any, Sequence
from . import _relic
from ._relic import BN, neutral_BN, rand_BN_mod, rand_BN_order, BN_from_int
from ._relic import GT, neutral_GT, rand_GT, generator_GT

"""
Helper classes with additive notations for G1 and G2

Sometimes protocols are written using additive notations for the groups G1 and G2. To
have a more convienient way to implement those protocols, G1 and G2 from this module are
implemented as additive groups.
"""


class G1:
    """Represents an element of the group G1 viewed as an additive group."""

    def __init__(self, base: Optional[Union[bytes, _relic.G1]] = None) -> None:
        if isinstance(base, _relic.G1):
            self.element = base
        else:
            self.element = _relic.G1(base)

    def __add__(self, other: "G1") -> "G1":
        return G1(self.element * other.element)

    def __iadd__(self, other: "G1") -> "G1":
        self.element *= other.element
        return self

    def __sub__(self, other: "G1") -> "G1":
        return G1(self.element / other.element)

    def __isub__(self, other: "G1") -> "G1":
        self.element = self.element / other.element
        return self

    def __neg__(self) -> "G1":
        return G1(self.element.invert())

    def __mul__(self, rhs: Union[int, BN]) -> "G1":
        return G1(self.element ** rhs)

    def __imul__(self, rhs: Union[int, BN]) -> "G1":
        self.element = self.element ** rhs
        return self

    def __rmul__(self, lhs: Union[int, BN]) -> "G1":
        return G1(self.element ** lhs)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, G1):
            return NotImplemented
        return self.element == other.element

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, G1):
            return NotImplemented
        return self.element != other.element

    def __hash__(self) -> int:
        return hash(self.element)

    def __bytes__(self) -> bytes:
        return bytes(self.element)

    def __repr__(self) -> bytes:
        return f"G1({bytes(self)!r})"


def neutral_G1() -> G1:
    return G1(_relic.neutral_G1())


def generator_G1(factor: Optional[BN] = None):
    return G1(_relic.generator_G1(factor))


def rand_G1() -> G1:
    return G1(_relic.rand_G1())


def hash_to_G1(data: bytes) -> G1:
    return G1(_relic.hash_to_G1(data))


def mul_sim_G1(
    values: Sequence[G1], scalars: Sequence[BN], base: Optional[G1] = None
) -> G1:
    return G1(
        _relic.mul_sim_G1(
            tuple(g1.element for g1 in values),
            scalars,
            base.element if base is not None else None,
        )
    )


class G2:
    """Represents an element of the group G1 viewed as an additive group."""

    def __init__(self, base: Optional[Union[bytes, _relic.G2]] = None) -> None:
        if isinstance(base, _relic.G2):
            self.element = base
        else:
            self.element = _relic.G2(base)

    def __add__(self, other: "G2") -> "G2":
        return G2(self.element * other.element)

    def __iadd__(self, other: "G2") -> "G2":
        self.element *= other.element
        return self

    def __sub__(self, other: "G2") -> "G2":
        return G2(self.element / other.element)

    def __isub__(self, other: "G2") -> "G2":
        self.element = self.element / other.element
        return self

    def __neg__(self) -> "G2":
        return G2(self.element.invert())

    def __mul__(self, rhs: Union[int, BN]) -> "G2":
        return G2(self.element ** rhs)

    def __imul__(self, rhs: Union[int, BN]) -> "G2":
        self.element = self.element ** rhs
        return self

    def __rmul__(self, lhs: Union[int, BN]) -> "G2":
        return G2(self.element ** lhs)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, G2):
            return NotImplemented
        return self.element == other.element

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, G2):
            return NotImplemented
        return self.element != other.element

    def __hash__(self) -> int:
        return hash(self.element)

    def __bytes__(self) -> bytes:
        return bytes(self.element)

    def __repr__(self) -> bytes:
        return f"G2({bytes(self)!r})"


def neutral_G2() -> G2:
    return G2(_relic.neutral_G2())


def generator_G2(factor: Optional[BN] = None):
    return G2(_relic.generator_G2(factor))


def rand_G2() -> G2:
    return G2(_relic.rand_G2())


def hash_to_G2(data: bytes) -> G2:
    return G2(_relic.hash_to_G2(data))


def mul_sim_G2(
    values: Sequence[G2], scalars: Sequence[BN], base: Optional[G2] = None
) -> G2:
    return G2(
        _relic.mul_sim_G2(
            tuple(g1.element for g1 in values),
            scalars,
            base.element if base is not None else None,
        )
    )


def pair(g1: G1, g2: G2) -> GT:
    return _relic.pair(g1.element, g2.element)


def pair_product(*args: Tuple[G1, G2]) -> GT:
    return _relic.pair_product(*((g1.element, g2.element) for g1, g2 in args))
