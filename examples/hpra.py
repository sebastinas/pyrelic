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
Financial Crytography 2017. https://eprint.iacr.org/2017/086.pdf.
"""

import pyrelic
from pyrelic import (
    BN,
    BN_from_int,
    neutral_BN,
    G1,
    G2,
    Relic,
    generator_G1,
    generator_G2,
    generator_GT,
    hash_to_G1,
    mul_sim_G1,
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

# Scheme 2


class HPRAParams:
    def __init__(self, l, gs):
        self.l = l
        self.gs = gs
        self.order = pyrelic.order()


def hpra_params(l):
    return HPRAParams(l, tuple(rand_G1() for i in range(l)))


class HPRASPrivateKey:
    def __init__(self, beta, pk):
        self.beta = beta
        self.pk = pk
        self.pp = pk.pp


class HPRASPublicKey:
    def __init__(self, g2beta, g2betainv, pp):
        self.pk1 = g2beta
        self.pk2 = g2betainv
        self.pp = pp


class HPRASID:
    def __init__(self, id):
        self.id = id


class HPRAVMK:
    def __init__(self, alpha, pp):
        self.alpha = alpha
        self.pp = pp


class HPRAAK:
    def __init__(self, ak):
        self.ak = ak


def hpra_sgen(pp):
    beta = rand_BN_order()
    g2beta = generator_G2(beta)
    g2betainv = generator_G2(beta.mod_inv(pp.order))

    pk = HPRASPublicKey(g2beta, g2betainv, pp)
    return HPRASID(g2beta), HPRASPrivateKey(beta, pk), pk


def hpra_hash(tau, id):
    return hash_to_G1(b"|".join((bytes(tau), bytes(id))))


def hpra_srgen(sk, aux):
    return None


def hpra_vgen(pp):
    alpha = rand_BN_order()
    return HPRAVMK(alpha, pp), None


def hpra_sign(sk, ms, tau):
    sigma = hpra_hash(tau, sk.pk.pk1)
    sigma = mul_sim_G1(sk.pk.pp.gs, ms, sigma)
    return sigma ** sk.beta


def hpra_verify(pk, ms, tau, sigma):
    sigmap = hpra_hash(tau, pk.pk1)
    sigmap = mul_sim_G1(pk.pp.gs, ms, sigmap)
    return pair(sigmap, pk.pk1) == pair(sigma, generator_G2())


def hpra_vrgen(pk, mk, rk=None):
    ak = pk.pk2 ** mk.alpha
    return HPRAAK(ak)


def hpra_agg(aks, sigmas, msgs, tau, weights, evalf):
    msg = evalf(msgs, weights)
    mu = pair_product(
        *((sigma ** weight, ak.ak) for sigma, weight, ak in zip(sigmas, weights, aks))
    )
    return msg, mu


def hpra_averify(mk, msg, mu, tau, ids, weights):
    ghat = generator_G2(mk.alpha)
    muprime = pair_product(
        (mul_sim_G1(mk.pp.gs, msg), ghat),
        *(
            (
                hpra_hash(tau, id.id) ** weight,
                ghat,
            )
            for id, weight in zip(ids, weights)
        ),
    )
    return muprime == mu


def evalf(msgs, weights):
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


def test_hpra():
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
    msg, mu = hpra_agg((ak1,), (sigma1,), (msg1,), tau, weights, evalf)
    assert hpra_averify(mk, msg, mu, tau, (id1,), weights)

    weights = (BN_from_int(1), BN_from_int(2))
    msg, mu = hpra_agg((ak1, ak2), (sigma1, sigma2), (msg1, msg2), tau, weights, evalf)

    # assert msg[0] == (msg1[0] * weights[0] + msg2[0] * weights[1]) % G1.order()
    assert hpra_averify(mk, msg, mu, tau, (id1, id2), weights)


# Scheme 3


class HPREPrivateKey:
    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2


class HPREPublicKey:
    def __init__(self, pk1, pk2):
        self.pk1 = pk1
        self.pk2 = pk2


def hpre_keygen(l):
    assert l >= 1
    a1 = tuple(rand_BN_order() for _ in range(l))
    a2 = tuple(rand_BN_order() for _ in range(l))

    sk = HPREPrivateKey(a1, a2)
    pk = HPREPublicKey(
        tuple(pair(generator_G1(a), generator_G2()) for a in a1),
        tuple(generator_G2(a) for a in a2),
    )

    return sk, pk


class HPREReEncKey:
    def __init__(self, rk):
        self.rk = rk


def hpre_rg(sk, pk):
    return HPREReEncKey(tuple(pk2 ** a1 for pk2, a1 in zip(pk.pk2, sk.a1)))


class HPRECiphertext:
    def __init__(self, level, c0, cs):
        self.level = level
        self.c0 = c0
        self.cs = cs


def hpre_encrypt(level, pk, ms, is_mapped=False):
    k = rand_BN_order()
    cs = tuple(
        (generator_GT(m) if not is_mapped else m) * pk1 ** k
        for m, pk1 in zip(ms, pk.pk1)
    )
    if level == 1:
        return HPRECiphertext(level, generator_GT(k), cs)
    elif level == 2:
        return HPRECiphertext(level, generator_G1(k), cs)
    assert False


def hpre_rencrypt(rk, c):
    assert c.level == 2
    return HPRECiphertext("R", tuple(pair(c.c0, r) for r in rk.rk), c.cs)


def hpre_decrypt(sk, c):
    order = pyrelic.order()
    if c.level == 1:
        return tuple(cs / c.c0 ** a1 for cs, a1 in zip(c.cs, sk.a1))
    elif c.level == 2:
        return tuple(
            cs * pair(c.c0 ** a1.mod_neg(order), generator_G2())
            for cs, a1 in zip(c.cs, sk.a1)
        )
    elif c.level == "R":
        return tuple(
            c1 / c0 ** a2.mod_inv(order) for c0, c1, a2 in zip(c.c0, c.cs, sk.a2)
        )


def hpre_eval(cs, weights):
    level = cs[0].level
    c1 = cs[0].c1 ** weights[0]
    c2 = cs[1].c2 ** weights[0]
    for c, w in zip(cs[1:], weights[1:]):
        c1 *= c.c1 ** w
        c2 *= c.c2 ** w
    return HPRECiphertext(level, c1, c2)


def test_hpre():
    l = 3
    sk1, pk1 = hpre_keygen(l)
    sk2, pk2 = hpre_keygen(l)
    ms = tuple(rand_BN_order() for x in range(l))
    ms_gt = tuple(generator_GT(m) for m in ms)

    c1 = hpre_encrypt(1, pk1, ms)
    c2 = hpre_encrypt(2, pk1, ms)

    assert hpre_decrypt(sk1, c1) == ms_gt
    assert hpre_decrypt(sk1, c2) == ms_gt

    rk12 = hpre_rg(sk1, pk2)
    c3 = hpre_rencrypt(rk12, c2)

    assert hpre_decrypt(sk2, c3)


# Scheme 4


class CombSPrivateKey:
    def __init__(self, sk, rsk, rpk):
        self.sk = sk
        self.rsk = rsk
        self.rpk = rpk


#   class CombSPublicKey:
#       def __init__(self, pk, rpk):
#           self.pk = pk
#           self.rpk = rpk


def comb_params(l):
    """Generate public parameters for HPRA."""

    assert l >= 1
    return hpra_params(l)


def comb_sgen(pp):
    """Generate "signing" key, i.e., the key of the source."""

    id, sk, pk = hpra_sgen(pp)
    rsk, rpk = hpre_keygen(pp.l + 1)

    return id, CombSPrivateKey(sk, rsk, rpk), pk


class CombMK:
    def __init__(self, mk, rsk):
        self.mk = mk
        self.rsk = rsk


class CombAUX:
    def __init__(self, aux, rpk):
        self.aux = aux
        self.rpk = rpk


def comb_vgen(pp):
    """Generate "verification" key, i.e., the key of the receiver."""

    mk, aux = hpra_vgen(pp)
    rsk, rpk = hpre_keygen(pp.l + 1)
    return CombMK(mk, rsk), CombAUX(aux, rpk)


class CombSignature:
    def __init__(self, sigma, c):
        self.sigma = sigma
        self.c = c


def comb_sign(sk, ms, tau):
    """Sign and encrypt message (exponents) with respect to given tag tau."""

    r = generator_G1(rand_BN_order())
    g2 = generator_G2()
    sigma = hpra_sign(sk.sk, ms, tau) * r
    # Make sure that messages are mapped into G_T with the correct base elements, e.g., that match
    # the bases used in Scheme 2.
    c = hpre_encrypt(
        2,
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


class CombSRKey:
    def __init__(self, prk):
        self.prki = prk


def comb_srgen(sk, aux):
    """Generate reencryption key."""

    # rk = hpra_srgen(sk.sk, None) # only returns None
    prk = hpre_rg(sk.rsk, aux.rpk)
    return CombSRKey(prk)


class CombAK:
    def __init__(self, ak, rk):
        self.ak = ak
        self.rk = rk


def comb_vrgen(pk, mk, rk):
    """Output aggregation key."""
    ak = hpra_vrgen(pk, mk.mk)
    return CombAK(ak, rk)


def comb_agg(aks, sigmas, tau, weights):
    """Aggregate and reencrypt authenticated message vector."""

    def evalcs(cs, weights):
        # The same as hpre_eval, but with the correct types level-2-ciphertexts.
        l = len(cs[0].cs)
        return HPRECiphertext(
            cs[0].level,
            tuple(
                math.prod(
                    (c.c0[idx] ** weight for c, weight in zip(cs, weights)),
                    start=neutral_GT(),
                )
                for idx in range(l)
            ),
            tuple(
                math.prod(
                    (c.cs[idx] ** weight for c, weight in zip(cs, weights)),
                    start=neutral_GT(),
                )
                for idx in range(l)
            ),
        )

    return hpra_agg(
        tuple(ak.ak for ak in aks),
        tuple(sigma.sigma for sigma in sigmas),
        tuple(hpre_rencrypt(ak.rk.prki, sigma.c) for ak, sigma in zip(aks, sigmas)),
        tau,
        weights,
        evalcs,
    )


def comb_averify(mk, cs, mu, tau, ids, weights):
    """Verify and decrypt authenticated message vector."""

    def hpra_averify(mk, msg, mu, tau, ids, weights):
        ghat = generator_G2()
        muprime = (
            math.prod(msg, start=neutral_GT())
            * pair_product(
                *(
                    (
                        hpra_hash(tau, id.id) ** weight,
                        ghat,
                    )
                    for id, weight in zip(ids, weights)
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


def test_comb():
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

    weights = (BN_from_int(1),)
    ctxt, mu = comb_agg((ak1,), (sigma1,), tau, weights)

    expected_msg = generator_GT(msg1[0])
    assert comb_averify(mk, ctxt, mu, tau, (id1,), weights)

    # Sign a message vector
    sigma2 = comb_sign(sk2, msg2, tau)
    # Compute aggregation key for second user
    rk2 = comb_srgen(sk2, aux)
    ak2 = comb_vrgen(pk2, mk, rk2)

    # Aggregate and reencrypt
    weights = (BN_from_int(2), BN_from_int(1))
    ctxt, mu = comb_agg((ak1, ak2), (sigma1, sigma2), tau, weights)

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