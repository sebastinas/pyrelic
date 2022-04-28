# Copyright 2022 Sebastian Ramacher <sebastian.ramacher@ait.ac.at>
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

import hashlib
from dataclasses import dataclass
from typing import Callable, Tuple, Any, Optional

from pyrelic import (
    BN,
    G1,
    G2,
    BN_from_int,
    generator_G1,
    generator_G2,
    hash_to_G2,
    order,
    pair_product,
    power_product_G1,
    rand_BN_order,
    rand_G1,
)


@dataclass
class PublicKey:
    """TBEQ public key."""

    x: Tuple[G2, ...]


@dataclass
class PrivateKey:
    """TBEQ private key."""

    x: Tuple[BN, ...]


@dataclass
class Signature:
    """TBEQ signature."""

    z1: G1
    y1: G1
    y2: G2
    v2: G2


@dataclass
class MessageVector:
    """TBEQ message vector."""

    m: Tuple[G1, ...]


def keygen(l: int) -> Tuple[PrivateKey, PublicKey]:
    """Generate a new keypair to sign message vectors of length l >= 2."""

    x = tuple(rand_BN_order() for _ in range(l))
    return PrivateKey(x), PublicKey(tuple(generator_G2(xi) for xi in x))


def _deterministic_y(k: bytes, message: Tuple[G1, ...]) -> BN:
    """Derive y for sign deterministically from the message and the given k."""

    sth = hashlib.shake_256()
    sth.update(k)
    for i in message:
        sth.update(bytes(i))
    return BN_from_int(int.from_bytes(sth.digest(64), "big") % int(order()))


def sign(
    sk: PrivateKey,
    message: MessageVector,
    tag: bytes,
    k: Optional[bytes] = None,
    H: Callable[[bytes], G2] = hash_to_G2,
) -> Signature:
    """Sign a message vector."""

    assert len(sk.x) == len(message.m)
    if k is None:
        y = rand_BN_order()
    else:
        y = _deterministic_y(k, message.m)

    z1 = power_product_G1(message.m, sk.x) ** y
    yinv = y.mod_inv(order())

    return Signature(z1, generator_G1(yinv), generator_G2(yinv), H(tag) ** yinv)


def verify(pk: PublicKey, message: MessageVector, tag: Any, sigma: Signature) -> bool:
    """Verify the signature on a message vector."""

    if len(message.m) != len(pk.x):
        return False

    # Instead of checking whether two pairings e(x1, y1) and e(x2, y2) are equal, we check
    # if e(x1, y1) / e(x2, y2) equals one instead. This allows us to make use of the faster
    # pair_product and a more efficient check.
    first = pair_product((sigma.z1.invert(), sigma.y2), *zip(message.m, pk.x))
    second = pair_product(
        (sigma.y1, generator_G2()), (generator_G1().invert(), sigma.y2)
    )
    third = pair_product(
        (generator_G1(), sigma.v2), (sigma.y1.invert(), hash_to_G2(tag))
    )

    return first.is_neutral() and second.is_neutral() and third.is_neutral()


def change_representation(
    message: MessageVector, sigma: Signature, mu: BN
) -> Tuple[MessageVector, Signature]:
    """Change representation of a message vector and its signature."""

    group_order = order()
    psi = rand_BN_order()
    psi_inv = psi.mod_inv(group_order)

    return MessageVector(tuple(m**mu for m in message.m)), Signature(
        sigma.z1 ** ((psi * mu) % group_order),
        sigma.y1**psi_inv,
        sigma.y2**psi_inv,
        sigma.v2**psi_inv,
    )


def test_tbeq(l: int) -> None:
    # generate a new key pair
    sk, pk = keygen(l)

    message = MessageVector(tuple(rand_G1() for _ in range(l)))

    tag = b"some random tag"
    # sign and ...
    sigma = sign(sk, message, tag)
    # verify it
    assert verify(pk, message, tag, sigma)

    # change the representation
    mu = rand_BN_order()
    new_message, new_sigma = change_representation(message, sigma, mu)
    # new signature verifies with the new representation of the message vector
    assert verify(pk, new_message, tag, new_sigma)
    # other combinations fails
    assert not verify(pk, new_message, tag, sigma)
    assert not verify(pk, message, tag, new_sigma)


if __name__ == "__main__":
    for l in range(2, 5):
        test_tbeq(l)
