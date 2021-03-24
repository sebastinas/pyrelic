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

"""Implementation of homomorphic proxy re-authenticators for linear functions

Based on David Derler, Sebastian Ramacher, Danial Slamanig: Homomorphic Proxy
Re-Authenticators and Applications to Verifiable Multi-User Data Aggregration.
Financial Cryptography 2017. https://eprint.iacr.org/2017/086.pdf.

This example requires Python >= 3.8.
"""

import pyrelic
from pyrelic import (
    BN,
    BN_from_int,
    neutral_BN,
    G1,
    G2,
    GT,
    Relic,
    generator_G1,
    generator_G2,
    generator_GT,
    hash_to_G1,
    mul_sim_G1,
    neutral_G1,
    neutral_GT,
    pair,
    pair_product,
    rand_BN_order,
    rand_G1,
    rand_G2,
    rand_GT,
)
import math
import itertools
import enum
import struct
from dataclasses import dataclass, field
from typing import Union, Sequence, Any, Optional, TypeVar, Callable, cast, Tuple

T = TypeVar("T")

# Scheme 2


@dataclass
class HPRAParams:
    """Public parameters for HPRA."""

    l: int
    gs: Sequence[G1]
    order: BN = field(init=False)

    def __post_init__(self) -> None:
        self.order = pyrelic.order()


def hpra_params(l: int) -> HPRAParams:
    """Generate public parameters for HPRA."""

    return HPRAParams(
        l,
        tuple(
            hash_to_G1(b" ".join((b"public params", struct.pack("<L", i))))
            for i in range(l)
        ),
    )


@dataclass
class HPRASPublicKey:
    pk1: G2
    pk2: G2
    pp: HPRAParams


@dataclass
class HPRASPrivateKey:
    beta: BN
    pk: HPRASPublicKey
    pp: HPRAParams = field(init=False)

    def __post_init__(self) -> None:
        self.pp = self.pk.pp


@dataclass
class HPRASID:
    id: G2

    def __bytes__(self) -> bytes:
        return bytes(self.id)


@dataclass
class HPRAVMK:
    alpha: BN
    pp: HPRAParams


@dataclass
class HPRAAK:
    ak: G2


def hpra_sgen(pp: HPRAParams) -> Tuple[HPRASID, HPRASPrivateKey, HPRASPublicKey]:
    beta = rand_BN_order()
    g2beta = generator_G2(beta)
    g2betainv = generator_G2(beta.mod_inv(pp.order))

    pk = HPRASPublicKey(g2beta, g2betainv, pp)
    return HPRASID(g2beta), HPRASPrivateKey(beta, pk), pk


def hpra_hash(*args: Any) -> G1:
    return hash_to_G1(b"|".join(bytes(arg) for arg in args))


def hpra_srgen(sk: HPRASPrivateKey, aux: None) -> None:
    return None


def hpra_vgen(pp: HPRAParams) -> Tuple[HPRAVMK, None]:
    alpha = rand_BN_order()
    return HPRAVMK(alpha, pp), None


def hpra_sign(sk: HPRASPrivateKey, ms: Sequence[BN], tau: Any, id_=None) -> G1:
    sigma = hpra_hash(tau, id_ if id_ is not None else sk.pk.pk1)
    sigma = mul_sim_G1(sk.pk.pp.gs, ms, sigma)
    return sigma ** sk.beta


def hpra_verify(pk: HPRASPublicKey, ms: Sequence[BN], tau: Any, sigma: G1) -> bool:
    sigmap = hpra_hash(tau, pk.pk1)
    sigmap = mul_sim_G1(pk.pp.gs, ms, sigmap)
    return pair(sigmap, pk.pk1) == pair(sigma, generator_G2())


def hpra_vrgen(pk: HPRASPublicKey, mk: HPRAVMK, rk: None = None) -> HPRAAK:
    ak = pk.pk2 ** mk.alpha
    return HPRAAK(ak)


def hpra_agg(
    aks: Sequence[HPRAAK],
    sigmas: Sequence[G1],
    msgs: Sequence[T],
    weights: Sequence[BN],
    evalf: Callable[[Sequence[T], Sequence[BN]], T],
) -> Tuple[T, GT]:
    msg = evalf(msgs, weights)
    mu = pair_product(
        *((sigma ** weight, ak.ak) for sigma, weight, ak in zip(sigmas, weights, aks))
    )
    return msg, mu


def hpra_averify(
    mk: HPRAVMK,
    msg: Sequence[BN],
    mu: GT,
    tau: Any,
    ids: Sequence[HPRASID],
    weights: Sequence[BN],
) -> bool:
    ghat = generator_G2(mk.alpha)
    muprime = pair_product(
        (mul_sim_G1(mk.pp.gs, msg), ghat),
        *(
            (
                hpra_hash(tau, _id) ** weight,
                ghat,
            )
            for _id, weight in zip(ids, weights)
        ),
    )
    return muprime == mu


def evalf(msgs: Sequence[Sequence[BN]], weights: Sequence[BN]) -> Tuple[BN, ...]:
    l = len(msgs[0])
    order = pyrelic.order()
    return tuple(
        sum(
            (msg[idx] * weight for msg, weight in zip(msgs, weights)),
            neutral_BN(),
        )
        % order
        for idx in range(l)
    )


def test_hpra() -> None:
    l = 1
    pp = hpra_params(l)
    id1, sk1, pk1 = hpra_sgen(pp)
    id2, sk2, pk2 = hpra_sgen(pp)
    mk, aux = hpra_vgen(pp)

    msg1 = tuple(rand_BN_order() for x in range(l))
    msg2 = tuple(rand_BN_order() for x in range(l))

    tau = b"some random tag"

    sigma1 = hpra_sign(sk1, msg1, tau)
    assert hpra_verify(pk1, msg1, tau, sigma1)

    sigma2 = hpra_sign(sk2, msg2, tau)
    assert hpra_verify(pk2, msg2, tau, sigma2)

    ak1 = hpra_vrgen(pk1, mk, aux)
    ak2 = hpra_vrgen(pk2, mk, aux)

    weights = (BN_from_int(1),)
    msg, mu = hpra_agg((ak1,), (sigma1,), (msg1,), weights, evalf)
    assert hpra_averify(mk, msg, mu, tau, (id1,), weights)

    weights_2 = (BN_from_int(1), BN_from_int(2))
    msg, mu = hpra_agg((ak1, ak2), (sigma1, sigma2), (msg1, msg2), weights_2, evalf)

    # assert msg[0] == (msg1[0] * weights[0] + msg2[0] * weights[1]) % G1.order()
    assert hpra_averify(mk, msg, mu, tau, (id1, id2), weights_2)


# Scheme 3


@dataclass
class HPREPrivateKey:
    a1: Sequence[BN]
    a2: Sequence[BN]


@dataclass
class HPREPublicKey:
    pk1: Sequence[GT]
    pk2: Sequence[G2]

    def __bytes__(self) -> bytes:
        return b"||".join(
            (
                b"|".join(bytes(x) for x in self.pk1),
                b"|".join(bytes(x) for x in self.pk2),
            )
        )


def hpre_keygen(l: int) -> Tuple[HPREPrivateKey, HPREPublicKey]:
    assert l >= 1
    a1 = tuple(rand_BN_order() for _ in range(l))
    a2 = tuple(rand_BN_order() for _ in range(l))

    sk = HPREPrivateKey(a1, a2)
    pk = HPREPublicKey(
        tuple(pair(generator_G1(a), generator_G2()) for a in a1),
        tuple(generator_G2(a) for a in a2),
    )

    return sk, pk


@dataclass
class HPREReEncKey:
    rk: Sequence[G2]


def hpre_rg(sk: HPREPrivateKey, pk: HPREPublicKey) -> HPREReEncKey:
    return HPREReEncKey(tuple(pk2 ** a1 for pk2, a1 in zip(pk.pk2, sk.a1)))


class HPRECiphertextLevel(enum.Enum):
    L1 = enum.auto()
    L2 = enum.auto()
    LR = enum.auto()


@dataclass
class HPRECiphertext:
    level: HPRECiphertextLevel
    c0: Union[G1, GT, Sequence[GT]]
    cs: Sequence[GT]


def hpre_encrypt(
    level: HPRECiphertextLevel,
    pk: HPREPublicKey,
    ms: Union[Sequence[BN], Sequence[GT]],
    is_mapped: bool = False,
) -> HPRECiphertext:
    k = rand_BN_order()
    cs = tuple(
        (generator_GT(cast(BN, m)) if not is_mapped else cast(GT, m)) * pk1 ** k
        for m, pk1 in zip(ms, pk.pk1)
    )
    if level == HPRECiphertextLevel.L1:
        return HPRECiphertext(level, generator_GT(k), cs)
    elif level == HPRECiphertextLevel.L2:
        return HPRECiphertext(level, generator_G1(k), cs)
    assert False


def hpre_rencrypt(rk: HPREReEncKey, c: HPRECiphertext) -> HPRECiphertext:
    assert c.level == HPRECiphertextLevel.L2
    return HPRECiphertext(
        HPRECiphertextLevel.LR, tuple(pair(cast(G1, c.c0), r) for r in rk.rk), c.cs
    )


def hpre_decrypt(sk: HPREPrivateKey, c: HPRECiphertext) -> Tuple[GT, ...]:
    order = pyrelic.order()
    if c.level == HPRECiphertextLevel.L1:
        return tuple(cs / cast(GT, c.c0) ** a1 for cs, a1 in zip(c.cs, sk.a1))
    elif c.level == HPRECiphertextLevel.L2:
        return tuple(
            cs * pair(cast(G1, c.c0) ** a1.mod_neg(order), generator_G2())
            for cs, a1 in zip(c.cs, sk.a1)
        )
    # elif c.level == HPRECiphertextLevel.LR:
    return tuple(
        c1 / c0 ** a2.mod_inv(order)
        for c0, c1, a2 in zip(cast(Sequence[GT], c.c0), c.cs, sk.a2)
    )


#   def hpre_eval(cs, weights):
#       level = cs[0].level
#       c1 = cs[0].c1 ** weights[0]
#       c2 = cs[1].c2 ** weights[0]
#       for c, w in zip(cs[1:], weights[1:]):
#           c1 *= c.c1 ** w
#           c2 *= c.c2 ** w
#       return HPRECiphertext(level, c1, c2)


def test_hpre() -> None:
    l = 3
    sk1, pk1 = hpre_keygen(l)
    sk2, pk2 = hpre_keygen(l)
    ms = tuple(rand_BN_order() for x in range(l))
    ms_gt = tuple(generator_GT(m) for m in ms)

    c1 = hpre_encrypt(HPRECiphertextLevel.L1, pk1, ms)
    c2 = hpre_encrypt(HPRECiphertextLevel.L2, pk1, ms)

    assert hpre_decrypt(sk1, c1) == ms_gt
    assert hpre_decrypt(sk1, c2) == ms_gt

    rk12 = hpre_rg(sk1, pk2)
    c3 = hpre_rencrypt(rk12, c2)

    assert hpre_decrypt(sk2, c3)


# Scheme 4


@dataclass
class CombSPrivateKey:
    sk: HPRASPrivateKey
    rsk: HPREPrivateKey
    rpk: HPREPublicKey


def comb_params(l: int) -> HPRAParams:
    """Generate public parameters for HPRA."""

    assert l >= 1
    return hpra_params(l)


def comb_sgen(pp: HPRAParams) -> Tuple[HPRASID, CombSPrivateKey, HPRASPublicKey]:
    """Generate "signing" key, i.e., the key of the source."""

    id, sk, pk = hpra_sgen(pp)
    rsk, rpk = hpre_keygen(pp.l + 1)

    return id, CombSPrivateKey(sk, rsk, rpk), pk


@dataclass
class CombMK:
    mk: HPRAVMK
    rsk: HPREPrivateKey


@dataclass
class CombAUX:
    aux: None
    rpk: HPREPublicKey


def comb_vgen(pp: HPRAParams) -> Tuple[CombMK, CombAUX]:
    """Generate "verification" key, i.e., the key of the receiver."""

    mk, aux = hpra_vgen(pp)
    rsk, rpk = hpre_keygen(pp.l + 1)
    return CombMK(mk, rsk), CombAUX(aux, rpk)


@dataclass
class CombSignature:
    sigma: G1
    c: HPRECiphertext


def comb_sign(sk: CombSPrivateKey, ms: Sequence[BN], tau: Any) -> CombSignature:
    """Sign and encrypt message (exponents) with respect to given tag tau."""

    r = generator_G1(rand_BN_order())
    g2 = generator_G2()
    sigma = hpra_sign(sk.sk, ms, tau) * r
    # Make sure that messages are mapped into G_T with the correct base elements, e.g., that match
    # the bases used in Scheme 2.
    c = hpre_encrypt(
        HPRECiphertextLevel.L2,
        sk.rpk,
        tuple(
            pair(lhs, rhs)
            for lhs, rhs in itertools.chain(
                ((base ** m, g2) for base, m in zip(sk.sk.pk.pp.gs, ms)),
                ((r, sk.sk.pk.pk2),),
            )
        ),
        is_mapped=True,
    )

    return CombSignature(sigma, c)


@dataclass
class CombSRKey:
    prki: HPREReEncKey


def comb_srgen(sk: CombSPrivateKey, aux: CombAUX) -> CombSRKey:
    """Generate reencryption key."""

    # rk = hpra_srgen(sk.sk, None) # only returns None
    prk = hpre_rg(sk.rsk, aux.rpk)
    return CombSRKey(prk)


@dataclass
class CombAK:
    ak: HPRAAK
    rk: CombSRKey


def comb_vrgen(pk: HPRASPublicKey, mk: CombMK, rk: CombSRKey) -> CombAK:
    """Output aggregation key."""
    ak = hpra_vrgen(pk, mk.mk)
    return CombAK(ak, rk)


def comb_agg(
    aks: Sequence[CombAK], sigmas: Sequence[CombSignature], weights: Sequence[BN]
) -> Tuple[HPRECiphertext, GT]:
    """Aggregate and reencrypt authenticated message vector."""

    def evalcs(cs: Sequence[HPRECiphertext], weights: Sequence[BN]) -> HPRECiphertext:
        # The same as hpre_eval, but with the correct types level-2-ciphertexts.
        l = len(cs[0].cs)
        return HPRECiphertext(
            cs[0].level,
            tuple(
                math.prod(
                    (
                        cast(Sequence[GT], c.c0)[idx] ** weight
                        for c, weight in zip(cs, weights)
                    ),
                    start=neutral_GT(),
                )  # type: ignore
                for idx in range(l)
            ),
            tuple(
                math.prod(
                    (
                        cast(Sequence[GT], c.cs)[idx] ** weight
                        for c, weight in zip(cs, weights)
                    ),
                    start=neutral_GT(),
                )  # type: ignore
                for idx in range(l)
            ),
        )

    return hpra_agg(
        tuple(ak.ak for ak in aks),
        tuple(sigma.sigma for sigma in sigmas),
        tuple(hpre_rencrypt(ak.rk.prki, sigma.c) for ak, sigma in zip(aks, sigmas)),
        weights,
        evalcs,
    )


def comb_averify(
    mk: CombMK,
    cs: HPRECiphertext,
    mu: GT,
    tau: Any,
    ids: Sequence[HPRASID],
    weights: Sequence[BN],
) -> Union[Sequence[GT], bool]:
    """Verify and decrypt authenticated message vector."""

    def hpra_averify(
        mk: HPRAVMK,
        msg: Sequence[GT],
        mu: GT,
        tau: Any,
        ids: Sequence[HPRASID],
        weights: Sequence[BN],
    ) -> bool:
        ghat = generator_G2()
        muprime = (
            math.prod(msg, start=neutral_GT())  # type: ignore
            * pair_product(
                *(
                    (
                        hpra_hash(tau, _id) ** weight,
                        ghat,
                    )
                    for _id, weight in zip(ids, weights)
                ),
            )
        ) ** mk.alpha
        return muprime == mu

    ms = hpre_decrypt(mk.rsk, cs)
    msu, r = ms[:-1], ms[-1]
    return (
        msu
        if hpra_averify(mk.mk, msu, mu / (r ** mk.mk.alpha), tau, ids, weights)
        else False
    )


def test_comb() -> None:
    l = 3  # length of the message vectors
    pp = comb_params(l)
    # Generate two signer keys
    id1, sk1, pk1 = comb_sgen(pp)
    id2, sk2, pk2 = comb_sgen(pp)
    # Generate one verification key
    mk, aux = comb_vgen(pp)

    msg1 = tuple(rand_BN_order() for x in range(l))
    msg2 = tuple(rand_BN_order() for x in range(l))

    tau = b"some random tag"

    # Sign a message vector
    sigma1 = comb_sign(sk1, msg1, tau)
    # Compute aggregation key for first user
    rk1 = comb_srgen(sk1, aux)
    ak1 = comb_vrgen(pk1, mk, rk1)

    weights: Tuple[BN, ...] = (BN_from_int(1),)
    ctxt, mu = comb_agg((ak1,), (sigma1,), weights)

    expected_msg = tuple(
        pair(base ** (m1 * weights[0]), generator_G2()) for base, m1 in zip(pp.gs, msg1)
    )
    msg = comb_averify(mk, ctxt, mu, tau, (id1,), weights)

    assert msg
    assert expected_msg == msg

    # Sign a message vector
    sigma2 = comb_sign(sk2, msg2, tau)
    # Compute aggregation key for second user
    rk2 = comb_srgen(sk2, aux)
    ak2 = comb_vrgen(pk2, mk, rk2)

    # Aggregate and reencrypt
    weights = (BN_from_int(2), BN_from_int(1))
    ctxt, mu = comb_agg((ak1, ak2), (sigma1, sigma2), weights)

    expected_msg = tuple(
        pair(base ** (m1 * weights[0] + m2 * weights[1]), generator_G2())
        for base, m1, m2 in zip(pp.gs, msg1, msg2)
    )
    # Verify and decrypt
    msg = comb_averify(mk, ctxt, mu, tau, (id1, id2), weights)

    assert msg
    assert expected_msg == msg


if __name__ == "__main__":
    with Relic():
        test_hpra()
        test_hpre()
        test_comb()
