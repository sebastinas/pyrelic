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
    rand_BN_order,
    generator_G2,
    hash_to_G1,
    pair,
)
from typing import Tuple


@dataclass
class MasterSecretKey:
    """BF master secret key."""

    alpha: BN


@dataclass
class PublicKey:
    """BF public key aka the public parameters."""

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
    """Computes H_1(identity) which maps an identity into G_1."""

    return hash_to_G1(identity)


def hash_and_xor(y: GT, message: bytes) -> bytes:
    """Computes H_2(y) ⊕ message."""
    message_len = len(message)

    # We use SHAKE-256 to easily derive a key stream that exactly matches the length
    # of the message.
    hash_context = hashlib.shake_256()
    # Hash "H_2" for domain seperation
    hash_context.update(b"H_2")
    hash_context.update(bytes(y))
    # Also hash the message length
    hash_context.update(struct.pack("<Q", message_len))

    # XOR message with the digest
    return bytes(d ^ m for d, m in zip(hash_context.digest(message_len), message))


def keygen() -> Tuple[MasterSecretKey, PublicKey]:
    """Generate a new key pair.

    The master secret key consists of an exponent α whereas the corresponding public
    key is α mapped into G_2, i.e., g_2^α.
    """

    alpha = rand_BN_order()
    return MasterSecretKey(alpha), PublicKey(generator_G2(alpha))


def extract_key(msk: MasterSecretKey, identity: bytes) -> SecretKey:
    """Extract secret key for an identity.

    Key extraction is done by first mapping the identity into G_1 using H_1 and then
    raising this group element to the secret exponent α, i.e, H_1(identity)^α.
    """

    return SecretKey(map_identity(identity) ** msk.alpha)


def encrypt(pk: PublicKey, identity: bytes, message: bytes) -> Ciphertext:
    """Encrypt a message with respect to some identity.

    Encryption works in multiple steps:
        * Sample a random exponent r and store u = g_1^r in the ciphertext.
        * Map the identity into G_1, i.e., q_id = H_1(identity).
        * Pair q_id and the public key to obtain g_id = e(q_id, pk).
        * Raise g_id to the r and use that element to derive the key stream to mask the
          message, i.e., v = H_2(g_id^r).
    """

    r = rand_BN_order()
    u = generator_G2(r)

    q_id = map_identity(identity)
    # Instead of computing g_id^r, we raise q_id to the r before pairing it which is
    # more efficient.
    g_id_r = pair(q_id**r, pk.pk)
    v = hash_and_xor(g_id_r, message)

    return Ciphertext(u, v)


def decrypt(sk: SecretKey, ciphertext: Ciphertext) -> bytes:
    """Decrypt a ciphertext with an extracted key.

    Decryption recomputes g_id^r by pairing the extracted secret key with u, i.e,
    g_id^r = e(sk, u)= e(H(identity)^α, g_2^r) = e(H(identity), pk)^r. Then, H_2 is
    used to unmask the message.
    """

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
    test_bf_ibe()
