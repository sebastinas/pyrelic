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

from typing import Optional, Union, Any, Sequence, Tuple

def _relic_init() -> Tuple[bool, bool, bool]: ...
def _relic_clean() -> None: ...

class BN:
    def __init__(self, bytes: Optional[bytes] = ...) -> None: ...
    def copy(self) -> BN: ...
    def __iadd__(self, other: Union[BN, int]) -> BN: ...
    def __add__(self, other: Union[BN, int]) -> BN: ...
    def __isub__(self, other: Union[BN, int]) -> BN: ...
    def __sub__(self, other: Union[BN, int]) -> BN: ...
    def __neg__(self) -> BN: ...
    def __imul__(self, other: Union[BN, int]) -> BN: ...
    def __mul__(self, other: Union[BN, int]) -> BN: ...
    def __mod__(self, mod: BN) -> BN: ...
    def mod_inv(self, mod: BN) -> BN: ...
    def mod_neg(self, mod: BN) -> BN: ...
    def __hash__(self) -> int: ...
    def __nonzero__(self) -> bool: ...
    def __bytes__(self) -> bytes: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __int__(self) -> int: ...
    @staticmethod
    def from_str(data: str, radix: int = ...) -> BN: ...

def neutral_BN() -> BN: ...
def rand_BN_mod(mod: BN) -> BN: ...
def rand_BN_order() -> BN: ...
def BN_from_int(data: int) -> BN: ...
def order() -> BN: ...

class G1:
    def __init__(self, bytes: Optional[bytes] = ...) -> None: ...
    def __imul__(self, other: G1) -> G1: ...
    def __mul__(self, other: G1) -> G1: ...
    def __truediv__(self, mod: G1) -> G1: ...
    def __pow__(self, exp: Union[BN, int], mod: None = ...) -> G1: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def __bytes__(self) -> bytes: ...
    def __repr__(self) -> str: ...
    def invert(self) -> G1: ...

def generator_G1(exponent: Optional[BN] = ...) -> G1: ...
def neutral_G1() -> G1: ...
def rand_G1() -> G1: ...
def hash_to_G1(data: bytes) -> G1: ...
def mul_sim_G1(
    values: Sequence[G1], scalars: Sequence[BN], base: Optional[G1] = ...
) -> G1: ...

class G2:
    def __init__(self, bytes: Optional[bytes] = ...) -> None: ...
    def __imul__(self, other: G2) -> G2: ...
    def __mul__(self, other: G2) -> G2: ...
    def __truediv__(self, mod: G2) -> G2: ...
    def __pow__(self, exp: Union[BN, int], mod: None = ...) -> G2: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def __bytes__(self) -> bytes: ...
    def __repr__(self) -> str: ...
    def invert(self) -> G2: ...

def generator_G2(exponent: Optional[BN] = ...) -> G2: ...
def neutral_G2() -> G2: ...
def rand_G2() -> G2: ...
def hash_to_G2(data: bytes) -> G2: ...
def mul_sim_G2(
    values: Sequence[G2], scalars: Sequence[BN], base: Optional[G2] = ...
) -> G2: ...

class GT:
    def __init__(self, bytes: Optional[bytes] = ...) -> None: ...
    def __imul__(self, other: GT) -> GT: ...
    def __mul__(self, other: GT) -> GT: ...
    def __truediv__(self, mod: GT) -> GT: ...
    def __pow__(self, exp: Union[BN, int], mod: None = ...) -> GT: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def is_neutral(self) -> bool: ...
    def __bytes__(self) -> bytes: ...
    def __repr__(self) -> str: ...

def generator_GT(exponent: Optional[BN] = ...) -> GT: ...
def neutral_GT() -> GT: ...
def rand_GT() -> GT: ...
def pair(g1: G1, g2: G2) -> GT: ...
def pair_product(*args: Tuple[G1, G2]) -> GT: ...
