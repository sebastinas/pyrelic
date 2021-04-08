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

"""Implementation of Bloom Filter KEM

Based on David Derler, Tibor Jager, Daniel Slamanig, Christoph Striecks:
Bloom Filter Encryption and Applications to Efficient Forward-Secret 0-RTT Key Exchange.
EUROCRYPT 2018. https://eprint.iacr.org/2018/199.pdf.

This example requires Python >= 3.7.
"""

import array
import hashlib
import math
import os
import pyrelic
import struct
from dataclasses import dataclass
from pyrelic import (
    rand_BN_order,
    pair,
    generator_G1,
    hash_to_G2,
    BN,
    G1,
    G2,
    GT,
)
from typing import Sequence, Optional, Tuple, List


class BloomFilter:
    """Bloom filter only with some helper functions."""

    def __init__(self, filter_size: int, false_positive_probability: float) -> None:
        """Instantiate given the expected size (filter_size, n) and the desired false
        positive probability."""

        # size of bit array: m = -(n * log(p)) / log(2) ** 2
        self.bitset_size = -math.floor(
            filter_size * math.log(false_positive_probability) / (math.log(2) ** 2)
        )
        # hash count: k = m / n * ln(2)
        self.hash_count = math.ceil(self.bitset_size / filter_size * math.log(2))

    def _hash_to_position(self, hash_idx: int, data: bytes) -> int:
        hash_context = hashlib.shake_256()
        hash_context.update(b"BFE_HASH")
        hash_context.update(struct.pack("<Q", hash_idx))
        hash_context.update(data)
        pos = struct.unpack("<Q", hash_context.digest(8))[0]
        return pos % self.bitset_size

    def get_bit_positions(self, data: bytes) -> Tuple[int, ...]:
        """Return all indices for the element."""

        return tuple(
            self._hash_to_position(hash_idx, data)
            for hash_idx in range(self.hash_count)
        )


@dataclass
class PrivateKey:
    """BFE private key"""

    bloom_filter: BloomFilter
    secret_keys: List[Optional[G2]]
    key_size: int
    pk: G1

    def __contains__(self, identity: int) -> bool:
        """Return True if key for the given identity is available."""

        return (
            identity >= 0
            and identity < self.bloom_filter.bitset_size
            and self.secret_keys[identity] is not None
        )

    def __getitem__(self, identity: int) -> G2:
        """Return key associated to an identity."""

        key = self.secret_keys[identity]
        if key is None:
            raise IndexError

        return key

    def __delitem__(self, identity: int) -> None:
        """Remove key associated to an identity."""

        key = self.secret_keys[identity]
        if key is not None:
            self.secret_keys[identity] = None
            del key


@dataclass
class PublicKey:
    """BFE public key"""

    bloom_filter: BloomFilter
    key_size: int
    pk: G1


@dataclass
class Ciphertext:
    """BFE ciphertext"""

    u: G1
    v: Sequence[bytes]


def map_identity(identity: int) -> G2:
    return hash_to_G2(struct.pack("<Q", identity))


def hash_r(key: bytes, key_size: int) -> Tuple[BN, bytes]:
    """Hash some initial random key and output r and k."""

    hash_context = hashlib.shake_256()
    hash_context.update(b"BFE_BF_H_R")
    hash_context.update(key)

    order = pyrelic.order()
    buffer = hash_context.digest(len(bytes(order)) * 2 + key_size)
    return (BN(buffer[:-key_size]) % order, buffer[-key_size:])


def hash_and_xor(y: GT, message: bytes) -> bytes:
    """Hash y and produce and mask message with the derived bit stream."""

    message_len = len(message)
    hash_context = hashlib.shake_256()
    hash_context.update(b"BFE_BF_G")
    hash_context.update(bytes(y))
    hash_context.update(struct.pack("<Q", message_len))

    return bytes(d ^ m for d, m in zip(hash_context.digest(message_len), message))


def keygen(
    key_size: int, filter_size: int, false_positive_probability: float
) -> Tuple[PrivateKey, PublicKey]:
    """Generate a new key pair."""

    exponent = rand_BN_order()  # BF secret key
    pk = generator_G1(exponent)  # BF public key
    bloom_filter = BloomFilter(filter_size, false_positive_probability)

    return (
        PrivateKey(
            bloom_filter,
            # extract derived keys for all identities
            [
                map_identity(identity) ** exponent
                for identity in range(bloom_filter.bitset_size)
            ],
            key_size,
            pk,
        ),
        PublicKey(bloom_filter, key_size, pk),
    )


def internal_encrypt(pkr: G1, identity: int, message: bytes) -> bytes:
    return hash_and_xor(pair(pkr, map_identity(identity)), message)


def encaps(pk: PublicKey) -> Tuple[bytes, Ciphertext]:
    """Encapsulate a freshly sampled key."""

    # sample a random value for FO
    key = os.urandom(pk.key_size)
    # derive r and k
    r, k = hash_r(key, pk.key_size)

    u = generator_G1(r)
    # instead of applying r to each pairing, precompute pk ** r
    pkr = pk.pk ** r

    return k, Ciphertext(
        u,
        tuple(
            internal_encrypt(pkr, identity, key)
            for identity in pk.bloom_filter.get_bit_positions(bytes(u))
        ),
    )


def puncture(sk: PrivateKey, ctxt: Ciphertext) -> None:
    """Puncture secret key on a ciphertext."""

    for identity in sk.bloom_filter.get_bit_positions(bytes(ctxt.u)):
        del sk[identity]  # remove associated key


def decaps(sk: PrivateKey, ctxt: Ciphertext) -> Optional[bytes]:
    """Decapsulate a key."""

    assert len(ctxt.v) == sk.bloom_filter.hash_count

    def internal_decrypt(sk: G2, v: bytes) -> bytes:
        return hash_and_xor(pair(ctxt.u, sk), v)

    # obtain encrypted key from one of the ciphertexts
    key: Optional[bytes] = None
    bit_positions = sk.bloom_filter.get_bit_positions(bytes(ctxt.u))
    for v, identity in zip(ctxt.v, bit_positions):
        # check if key is available for the identity
        if identity in sk:
            key = internal_decrypt(sk[identity], v)
            break
    else:
        # no working derived keys available
        return None

    # derive r and k
    r, k = hash_r(key, sk.key_size)
    pkr = sk.pk ** r

    # recompute ciphertext and verify equality
    recomputed_u = generator_G1(r)
    recomputed_v = tuple(
        internal_encrypt(pkr, identity, key) for identity in bit_positions
    )
    return k if recomputed_u == ctxt.u and recomputed_v == ctxt.v else None


def test_bfe() -> None:
    # Generate a key pair (this will take forever)
    sk, pk = keygen(32, 2 ** 19, 0.0009765625)

    for _ in range(32):
        # Encapsulate a new key
        k, ctxt = encaps(pk)
        # Decapsulate the key
        received_k = decaps(sk, ctxt)
        assert received_k is not None
        assert k == received_k

        # Puncture the ciphertext
        puncture(sk, ctxt)
        # Decapsulation now fails
        received_k = decaps(sk, ctxt)
        assert received_k is None


if __name__ == "__main__":
    test_bfe()
