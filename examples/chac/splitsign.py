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

from dataclasses import dataclass
from typing import Tuple

from pyrelic import (
    BN,
    G1,
    G2,
    generator_G1,
    generator_G2,
    order,
    pair_product,
    rand_BN_order,
    hash_to_G1,
    power_product_G1,
    power_product_G2,
)


@dataclass
class Parameters:
    """SFPK public parameters."""

    y1: G1
    y2: G2


@dataclass
class PublicKey:
    """SFPK public key."""

    a: G1
    b: G1
    params: Parameters

    def is_canonical(self) -> bool:
        """Checks if the public key is canonical."""

        return self.a == generator_G1()


@dataclass
class PrivateKey:
    """SFPK private key."""

    y: G1
    pk: PublicKey


@dataclass
class PublicState:
    """Public state during the split-signing procedure."""

    u1: G1
    u2: G2


@dataclass
class SecretState:
    """Private state during the spit-signing procedure."""

    k: BN


@dataclass
class Signature:
    """SFPK signature."""

    sig1: G1
    sig2: G1
    sig3: G2


@dataclass
class PreSignature:
    """Intermediate signature during the split-signing procedure."""

    x: G1
    r: BN


@dataclass
class _Trapdoor:
    g2: G2


def crsgen() -> Parameters:
    """ "Generate public parameters for SFPK."""

    y = rand_BN_order()
    y1 = generator_G1(y)
    y2 = generator_G2(y)

    return Parameters(y1, y2)


def keygen(params: Parameters) -> Tuple[PrivateKey, PublicKey]:
    """Generate SFPK private and public key."""

    x = rand_BN_order()
    pk = PublicKey(generator_G1(), generator_G1(x), params)
    return PrivateKey(params.y1**x, pk), pk


def _tkgen(params: Parameters) -> Tuple[PrivateKey, PublicKey, _Trapdoor]:
    x = rand_BN_order()
    pk = PublicKey(generator_G1(), generator_G1(x), params)
    return PrivateKey(params.y1**x, pk), pk, _Trapdoor(generator_G2(x))


def sign1() -> Tuple[SecretState, PublicState]:
    """Perform first step of the split signing procedure."""
    k = rand_BN_order()
    return SecretState(k), PublicState(generator_G1(k), generator_G2(k))


def _H(message: bytes) -> G1:
    return hash_to_G1(message)


def sign2(sk: PrivateKey, message: bytes, st: SecretState) -> PreSignature:
    """Perform second step of the split signing procedure."""

    r = rand_BN_order()
    kinv = st.k.mod_inv(order())
    g1 = sk.y * _H(message) ** r
    return PreSignature(g1, (r * kinv) % order())


def sign3(psigma: PreSignature, pst: PublicState) -> Signature:
    """Perform thrid and lest step fo the split signing procedure."""

    return Signature(psigma.x, pst.u1**psigma.r, pst.u2**psigma.r)


def verify(pk: PublicKey, message: bytes, sigma: Signature) -> bool:
    """Verify a SFPK signature."""

    first = pair_product(
        (sigma.sig2.invert(), generator_G2()), (generator_G1(), sigma.sig3)
    )
    second = pair_product(
        (sigma.sig1.invert(), generator_G2()),
        (pk.b, pk.params.y2),
        (_H(message), sigma.sig3),
    )
    return first.is_neutral() and second.is_neutral()


def chgpk(pk: PublicKey, r: BN) -> PublicKey:
    """Change representation of a SFPK public key."""

    return PublicKey(pk.a**r, pk.b**r, pk.params)


def chgsk(sk: PrivateKey, r: BN) -> PrivateKey:
    """Change representation of a SFPK private key."""

    return PrivateKey(sk.y**r, chgpk(sk.pk, r))


def _chkrep(delta: _Trapdoor, pk: PublicKey) -> bool:
    return pair_product((pk.a, delta.g2), (pk.b.invert(), generator_G2())).is_neutral()


def rerand(
    pk: PublicKey, message: bytes, sigma: Signature, r: BN
) -> Tuple[PublicKey, Signature]:
    """Rerandomize a SFPK signature."""

    # assert verify(pk, message, sigma)
    k = rand_BN_order()
    pknew = chgpk(pk, r)
    sigmanew = Signature(
        power_product_G1((sigma.sig1, _H(message)), (r, k)),
        power_product_G1((sigma.sig2, generator_G1()), (r, k)),
        power_product_G2((sigma.sig3, generator_G2()), (r, k)),
    )

    return pknew, sigmanew


def sign(sk: PrivateKey, message: bytes) -> Signature:
    """Sign a message."""

    secretstate, publicstate = sign1()
    presigma = sign2(sk, message, secretstate)
    return sign3(presigma, publicstate)


def test_splitsign() -> None:
    params = crsgen()
    sk, pk = keygen(params)

    message = b"some message"
    sigma = sign(sk, message)
    assert verify(pk, message, sigma)

    pk2, sigma2 = rerand(pk, message, sigma, rand_BN_order())
    assert verify(pk2, message, sigma2)


if __name__ == "__main__":
    test_splitsign()
