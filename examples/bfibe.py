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

"""Implementation of the Boneh-Franklin IBE scheme (BasicIdent)

Based on Dan Boneh, Matthew K. Franklin: Identity-Based Encryption from the Weil
Pairing. CRYPTO 2001.

This example requires Python >= 3.7.
"""

import hashlib
import struct
from dataclasses import dataclass
from pyrelic import (
    BN,
    G1,
    G2,
    GT,
    Relic,
    rand_BN_order,
    generator_G1,
    generator_G2,
    hash_to_G1,
    pair,
)
from typing import Tuple


@dataclass
class MasterSecretKey:
    """BF master secret key."""

    exponent: BN


@dataclass
class PublicKey:
    """BF public ke aka the public parameters."""

    pk: G2


@dataclass
class SecretKey:
    """Extracted secret key for an identity."""

    sk: G1


@dataclass
class Ciphertext:
    """BF ciphertext"""

    u: G2
    v: bytes


def map_identity(identity: bytes) -> G1:
    """Computes H_1(identity)."""

    return hash_to_G1(identity)


def hash_and_xor(y: GT, message: bytes) -> bytes:
    """Computes H_2(y) ⊕ message."""
    message_len = len(message)

    hash_context = hashlib.shake_256()
    hash_context.update(b"H_2")
    hash_context.update(bytes(y))
    hash_context.update(struct.pack("<Q", message_len))

    return bytes(d ^ m for d, m in zip(hash_context.digest(message_len), message))


def keygen() -> tuple[MasterSecretKey, PublicKey]:
    """Generate a new key pair."""

    exponent = rand_BN_order()
    return MasterSecretKey(exponent), PublicKey(generator_G2(exponent))


def extract_key(msk: MasterSecretKey, identity: bytes) -> SecretKey:
    """Extract secret key for an identity."""

    return SecretKey(map_identity(identity) ** msk.exponent)


def encrypt(pk: PublicKey, identity: bytes, message: bytes) -> Ciphertext:
    """Encrypt a message with respect to some identity."""

    q_id = map_identity(identity)
    r = rand_BN_order()
    g_id_r = pair(q_id ** r, pk.pk)

    u = generator_G2(r)
    v = hash_and_xor(g_id_r, message)
    return Ciphertext(u, v)


def decrypt(sk: SecretKey, ciphertext: Ciphertext) -> bytes:
    """Decrypt a ciphertext with an extracted key."""

    g_id_r = pair(sk.sk, ciphertext.u)
    return hash_and_xor(g_id_r, ciphertext.v)


def test_bf_ibe() -> None:
    # Generate key pair
    msk, pk = keygen()
    # Extract keys for two identities
    sk_id_1 = extract_key(msk, b"identity 1")
    sk_id_2 = extract_key(msk, b"identity 2")

    # Encrypt a message with respect to the first identity
    msg = b"some message"
    ctxt = encrypt(pk, b"identity 1", msg)

    # Decrypt ciphertext with the correct identity
    received_msg = decrypt(sk_id_1, ctxt)
    assert received_msg == msg

    # Decrypt ciphertext with the incorrect identity
    received_msg = decrypt(sk_id_2, ctxt)
    assert received_msg != msg


if __name__ == "__main__":
    with Relic():
        test_bf_ibe()
