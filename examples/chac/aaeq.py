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
import secrets
from functools import partial
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, List

from pyrelic import (
    BN,
    G2,
    generator_G1,
    generator_G2,
    hash_to_G2,
    product_G1,
    product_G2,
    rand_BN_order,
    rand_G1,
    pair_product,
)

from . import tbeq
from .tbeq import Signature, MessageVector


@dataclass
class Attribute:
    """Named attributed with the associated value."""

    name: str
    value: str


@dataclass
class PublicKey:
    """AAEQ public key (for an attribute)."""

    x: tbeq.PublicKey
    attrName: str


@dataclass
class PrivateKey:
    """AAEQ private key (for an attribute)."""

    x: tbeq.PrivateKey
    k: BN
    attrName: str
    pk: PublicKey


@dataclass
class MainPublicKey:
    """AAEQ main public key."""

    x: Tuple[PublicKey, ...]


@dataclass
class MainPrivateKey:
    """AAEQ main private key"""

    x: Tuple[PrivateKey, ...]


def setup(
    attributes: Sequence[str], l: int, k_bytes: int = 32
) -> Tuple[MainPrivateKey, MainPublicKey]:
    """Generate main private and public key for AAEQ."""

    assert l >= 2

    k = secrets.token_bytes(k_bytes)
    msk_list = []
    mpk_list = []
    for attribute in attributes:
        sk, pk = tbeq.keygen(l)

        pk = PublicKey(pk, attribute)
        mpk_list.append(pk)
        sk = PrivateKey(sk, k, attribute, pk)
        msk_list.append(sk)

    return MainPrivateKey(tuple(msk_list)), MainPublicKey(tuple(mpk_list))


def gen(msk: MainPrivateKey, attribute_name: str) -> PrivateKey:
    """Access attribute-specific private key."""

    return _findsk(msk, attribute_name)


def _H(value: bytes, pk: PublicKey) -> G2:
    data = b"||".join(
        (b"|".join(bytes(pki) for pki in pk.x.x), pk.attrName.encode("utf8"), value)
    )
    return hash_to_G2(data)


def sign(
    sk_attr: PrivateKey, message: MessageVector, attribute_value: str
) -> Signature:
    """Sign a message vector with a specific attribute value."""

    return tbeq.sign(
        sk_attr.x,
        message,
        attribute_value.encode("utf8"),
        k=sk_attr.k,
        H=partial(_H, pk=sk_attr.pk),
    )


def verify(
    mpk: MainPublicKey,
    message: MessageVector,
    attributes: List[Attribute],
    aggr_sigma: Signature,
) -> bool:
    """Verify the signature on a message vector."""

    pks = _pks_for_attr(mpk, attributes)
    if any(pk is None for pk in pks):
        return False

    return (
        pair_product(
            (aggr_sigma.z1.invert(), aggr_sigma.y2),
            *tuple(
                (msg, product_G2(pk.x.x[index] for pk in pks))
                for index, msg in enumerate(message.m)
            ),
        ).is_neutral()
        and pair_product(
            (aggr_sigma.y1.invert(), generator_G2()), (generator_G1(), aggr_sigma.y2)
        ).is_neutral()
        and pair_product(
            (generator_G1(), aggr_sigma.v2),
            (
                aggr_sigma.y1.invert(),
                product_G2(
                    _H(attr.value.encode("utf8"), pk)
                    for attr, pk in zip(attributes, pks)
                ),
            ),
        ).is_neutral()
    )


def change_representation(
    _: MainPublicKey, message: MessageVector, sigma: Signature, mu: BN
) -> Tuple[MessageVector, Signature]:
    """Change representation of a message vector and its signature."""

    return tbeq.change_representation(message, sigma, mu)


def aggregate(_: MainPublicKey, signatures: List[Signature]) -> Optional[Signature]:
    """Aggregate a list of signatures."""

    base_sig = signatures[0]
    for sig in signatures[1:]:
        if sig.y1 != base_sig.y1 or sig.y2 != base_sig.y2:
            return None

    return Signature(
        product_G1(signature.z1 for signature in signatures),
        base_sig.y1,
        base_sig.y2,
        product_G2(signature.v2 for signature in signatures),
    )


def _findpk(mpk: MainPublicKey, attribute: str) -> PublicKey:
    for pk in mpk.x:
        if attribute == pk.attrName:
            return pk
    assert False


def _findsk(msk: MainPrivateKey, attribute: str) -> PrivateKey:
    for sk in msk.x:
        if attribute == sk.attrName:
            return sk
    assert False


def _pks_for_attr(mpk: MainPublicKey, attributes: List[Attribute]) -> List[PublicKey]:
    return tuple(_findpk(mpk, attr.name) for attr in attributes)


def aidgen(attributes: List[Attribute], nonce: bytes) -> bytes:
    """Generate AID from a list of attributes and a nonce."""

    sth = hashlib.shake_256()
    for attr in attributes:
        sth.update(attr.name.encode("utf-8"))
        sth.update(attr.value.encode("utf-8"))
    sth.update(nonce)
    return sth.digest(64)


def test_aaeq(l: int) -> None:
    attributes = ("attr1", "attr2", "attr3")

    msk, mpk = setup(attributes, l)

    message = MessageVector(tuple(rand_G1() for _ in range(l)))

    attr1 = Attribute("attr1", "value1")
    sigma1 = sign(gen(msk, attr1.name), message, attr1.value)
    assert verify(mpk, message, [attr1], sigma1)

    attr3 = Attribute("attr3", "value3")
    sigma3 = sign(gen(msk, attr3.name), message, attr3.value)
    assert verify(mpk, message, [attr3], sigma3)

    sigma = aggregate(mpk, [sigma1, sigma3])
    assert verify(mpk, message, [attr1, attr3], sigma)

    attr2 = Attribute("attr2", "value2")
    assert not verify(mpk, message, [attr1, attr2], sigma)

    message2, sigma2 = change_representation(mpk, message, sigma, rand_BN_order())
    assert verify(mpk, message2, [attr1, attr3], sigma2)


if __name__ == "__main__":
    for l in range(2, 5):
        test_aaeq(l)
