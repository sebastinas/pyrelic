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

"""Implementation of the BLS signatures scheme

This example requires Python >= 3.7.
"""

from dataclasses import dataclass
from pyrelic import (
    rand_BN_order,
    pair,
    generator_G2,
    hash_to_G1,
    BN,
    G1,
    G2,
    Relic,
)
from typing import Tuple


@dataclass
class PrivateKey:
    """BLS private key"""

    exponent: BN


@dataclass
class PublicKey:
    """BLS public key"""

    pk: G2


@dataclass
class Signature:
    """BLS signature"""

    sigma: G1


def keygen() -> Tuple[PrivateKey, PublicKey]:
    exponent = rand_BN_order()
    return PrivateKey(exponent), PublicKey(generator_G2(exponent))


def sign(sk: PrivateKey, message: bytes) -> Signature:
    return Signature(hash_to_G1(message) ** sk.exponent)


def verify(pk: PublicKey, message: bytes, sig: Signature) -> bool:
    return pair(hash_to_G1(message), pk.pk) == pair(sig.sigma, generator_G2())


def test_bls() -> None:
    sk, pk = keygen()

    sig = sign(sk, b"some message")
    assert verify(pk, b"some message", sig)


if __name__ == "__main__":
    with Relic():
        test_bls()
