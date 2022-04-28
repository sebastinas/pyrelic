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

import secrets
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from pyrelic import rand_BN_order

from . import aaeq, splitsign
from .splitsign import Parameters
from .aaeq import (
    Attribute,
    aidgen,
    PublicKey as IssuerPublicKey,
    PrivateKey as IssuerPrivateKey,
)


@dataclass
class CoreSecretKey:
    """Secret key of the core."""

    sk: splitsign.PrivateKey
    pk: splitsign.PublicKey
    ss: splitsign.SecretState
    ps: splitsign.PublicState


@dataclass
class APRequest:
    """Intermediate state during obtain/show."""

    pk: splitsign.PublicKey
    ps: splitsign.PublicState
    presigma: splitsign.PreSignature


@dataclass
class Credentials:
    """User credentials."""

    signatures: Dict[str, aaeq.Signature]


@dataclass
class AReq:
    """Intermediate state during showing."""

    pk: splitsign.PublicKey
    sigma: splitsign.Signature


@dataclass
class ASig:
    """Showing a CHAC credential"""

    pk: splitsign.PublicKey
    ssigma: splitsign.Signature
    asigma: aaeq.Signature


def setup() -> Parameters:
    """Generate CHAC public parameters."""

    return splitsign.crsgen()


def issuer_kgen(
    attribute_names: Sequence[str],
) -> Tuple[IssuerPrivateKey, IssuerPublicKey]:
    """Generate private and public key for a CHAC issuer."""

    return aaeq.setup(attribute_names, 2)


def core_kgen(params: Parameters) -> CoreSecretKey:
    """Generate private key for the core."""

    sk, pk = splitsign.keygen(params)
    ss, ps = splitsign.sign1()

    return CoreSecretKey(sk, pk, ss, ps)


def core_obtain(aid: bytes, _ipk: IssuerPublicKey, ssk: CoreSecretKey) -> APRequest:
    """Perform steps of the obtain/show procedure that run on the core."""

    return APRequest(ssk.pk, ssk.ps, splitsign.sign2(ssk.sk, aid, ssk.ss))


APSig = APRequest
core_show = core_obtain


def helper_obtain(
    _attributes: List[Attribute], _nonce: bytes, ipk: IssuerPublicKey, apreq: APSig
) -> AReq:
    """Perform steps of the obtain procedure that run on the helper."""

    sigma = splitsign.sign3(apreq.presigma, apreq.ps)
    return AReq(apreq.pk, sigma)


def helper_show(
    attributes: List[Attribute],
    nonce: bytes,
    credentials: Credentials,
    ipk: IssuerPublicKey,
    apsig: APSig,
) -> ASig:
    """Perform steps of the show procued that run on the helper."""

    # compute aid and finalize signature
    aid = aaeq.aidgen(attributes, nonce)
    sigma = splitsign.sign3(apsig.presigma, apsig.ps)

    # aggregate AAEQ signatures
    aggrsigma = aaeq.aggregate(
        ipk, [credentials.signatures[attribute.name] for attribute in attributes]
    )

    # rerandomize
    r = rand_BN_order()
    pknew, sigmanew = splitsign.rerand(apsig.pk, aid, sigma, r)
    _, aggrsigmanew = aaeq.change_representation(
        ipk, _pk_to_message_vector(apsig.pk), aggrsigma, r
    )

    return ASig(pknew, sigmanew, aggrsigmanew)


def issue(
    attributes: List[Attribute],
    nonce: bytes,
    areq: AReq,
    isk: IssuerPrivateKey,
    _params: Parameters,
) -> Optional[Tuple[Credentials, splitsign.PublicKey]]:
    "Issue a credential."

    aid = aaeq.aidgen(attributes, nonce)
    if not splitsign.verify(areq.pk, aid, areq.sigma) or not areq.pk.is_canonical():
        return None

    messagepk = _pk_to_message_vector(areq.pk)
    sigmas = {
        attribute.name: aaeq.sign(
            aaeq.gen(isk, attribute.name), messagepk, attribute.value
        )
        for attribute in attributes
    }
    return Credentials(sigmas), areq.pk


def verify(
    attributes: List[Attribute],
    nonce: bytes,
    asig: ASig,
    ipk: IssuerPublicKey,
    _params: Parameters,
) -> bool:
    """Verify a CHAC showing."""

    aid = aaeq.aidgen(attributes, nonce)
    if not splitsign.verify(asig.pk, aid, asig.ssigma):
        return False
    messagepk = _pk_to_message_vector(asig.pk)
    return aaeq.verify(ipk, messagepk, attributes, asig.asigma)


def _pk_to_message_vector(pk: splitsign.PublicKey) -> aaeq.MessageVector:
    return aaeq.MessageVector((pk.a, pk.b))


def test_chac(num_attributes: int) -> None:
    params = setup()
    attributes_o = tuple(
        Attribute(f"attr{i}", f"value{i}") for i in range(num_attributes)
    )
    attribute_names = tuple(attr.name for attr in attributes_o)

    isk, ipk = issuer_kgen(attribute_names)
    ssk = core_kgen(params)

    nonce_o = secrets.token_bytes(32)
    aid_o = aidgen(attributes_o, nonce_o)
    aprequest = core_obtain(aid_o, ipk, ssk)
    areq = helper_obtain(attributes_o, nonce_o, ipk, aprequest)

    cred = issue(attributes_o, nonce_o, areq, isk, params)
    assert cred is not None
    cred = cred[0]

    for t in range(1, num_attributes):
        attributes_s = attributes_o[:t]
        nonce_s = secrets.token_bytes(32)
        aid_s = aidgen(attributes_s, nonce_s)

        apsig = core_show(aid_s, ipk, ssk)
        asig = helper_show(attributes_s, nonce_s, cred, ipk, apsig)
        assert verify(attributes_s, nonce_s, asig, ipk, params)


if __name__ == "__main__":
    for num_attr in range(7, 10):
        test_chac(num_attr)
