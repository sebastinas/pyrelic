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

"""Implementation of the structure preserving signature scheme for equivalence classes

Based on Georg Fuchsbauer, Christian Hanser, Daniel Slamanig: Structure-Preserving
Signatures on Equivalence Classes and Constant-Size Anonymous Credentials. Journal of
Cryptology 2019. https://eprint.iacr.org/2014/944

This example requires Python >= 3.7.
"""

from dataclasses import dataclass
from pyrelic import (
    BN,
    G1,
    G2,
    generator_G1,
    generator_G2,
    order,
    pair_product,
    power_product_G1,
    rand_BN_order,
    rand_G1,
)
from typing import Tuple


@dataclass
class PublicKey:
    """SPS-EQ public key."""

    x: Tuple[G2, ...]


@dataclass
class PrivateKey:
    """SPS-EQ private key."""

    x: Tuple[BN, ...]


@dataclass
class MessageVector:
    """SPS-EQ message vector."""

    m: Tuple[G1, ...]


@dataclass
class Signature:
    """SPS-EQ signature."""

    z: G1
    y: G1
    yhat: G2


def keygen(l: int) -> Tuple[PrivateKey, PublicKey]:
    """Generate a new keypair to sign message vectors of length l >= 2."""
    assert l >= 2

    x = tuple(rand_BN_order() for _ in range(l))

    return PrivateKey(x), PublicKey(tuple(generator_G2(xi) for xi in x))


def sign(sk: PrivateKey, message: MessageVector) -> Signature:
    """Sign a message vector."""

    assert len(sk.x) == len(message.m)

    y = rand_BN_order()
    z = power_product_G1(message.m, sk.x) ** y
    yinv = y.mod_inv(order())

    return Signature(z, generator_G1(yinv), generator_G2(yinv))


def verify(pk: PublicKey, message: MessageVector, sigma: Signature) -> bool:
    """Verify the signature on a message vector."""

    if len(message.m) != len(pk.x):
        return False

    # Instead of checking whether two pairings e(x1, y1) and e(x2, y2) are equal, we check
    # if e(x1, y2) / e(x2, y2) equals one instead. This allows us to make use of the faster
    # pair_product and a more efficient check.
    first = pair_product((sigma.z.invert(), sigma.yhat), *zip(message.m, pk.x))
    second = pair_product(
        (sigma.y, generator_G2()), (generator_G1().invert(), sigma.yhat)
    )

    return first.is_neutral() and second.is_neutral()


def change_representation(
    pk: PublicKey, message: MessageVector, sigma: Signature, mu: BN
) -> Tuple[MessageVector, Signature]:
    """Change representation of a message vector and its signature."""

    if not verify(pk, message, sigma):
        raise ValueError("Signature does not verify.")

    group_order = order()
    psi = rand_BN_order()
    psi_inv = psi.mod_inv(group_order)
    return MessageVector(tuple(m**mu for m in message.m)), Signature(
        sigma.z ** ((psi * mu) % group_order), sigma.y**psi_inv, sigma.yhat**psi_inv
    )


def test_spseq(l: int) -> None:
    # generate a new key pair
    sk, pk = keygen(l)

    # generate a random message vector
    message = MessageVector(tuple(rand_G1() for _ in range(l)))
    # sign and ...
    sigma = sign(sk, message)
    # verify it
    assert verify(pk, message, sigma)

    # change the representation
    new_message, new_sigma = change_representation(pk, message, sigma, rand_BN_order())
    # new signature verifies with the new representation of the message vector
    assert verify(pk, new_message, new_sigma)
    # other combinations fails
    assert not verify(pk, new_message, sigma)
    assert not verify(pk, message, new_sigma)


if __name__ == "__main__":
    for l in range(2, 5):
        test_spseq(l)
