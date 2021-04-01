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
    generator_G2,
    hash_to_G1,
    BN,
    G1,
    G2,
    GT,
)
from typing import Sequence, Optional, Tuple, List


def get_position(hash_idx: int, data: bytes, filter_size: int) -> int:
    hash_context = hashlib.shake_256()
    hash_context.update(b"BFE_HASH")
    hash_context.update(struct.pack("<Q", hash_idx))
    hash_context.update(data)
    pos = struct.unpack("<Q", hash_context.digest(8))[0]
    return pos % filter_size


def get_bit_positions(data: bytes, hash_count: int, filter_size: int) -> Tuple[int, ...]:
    return tuple(get_position(hash_idx, data, filter_size) for hash_idx in range(hash_count))


class BloomFilter:
    """Bloom filter."""

    def __init__(self, filter_size: int, false_positive_probability: float) -> None:
        """Instantiate given the expected size (filter_size, n) and the desired false
        positive probability."""

        # size of bit array: m = -(n * log(p)) / log(2) ** 2
        self.bitset_size = -math.floor(
            filter_size * math.log(false_positive_probability) / (math.log(2) ** 2)
        )
        # hash count: k = m / n * ln(2)
        self.hash_count = math.ceil(self.bitset_size / filter_size * math.log(2))
        self.bits = bytearray(math.ceil(self.bitset_size / 8))

    def get_bit_positions(self, data: bytes) -> Tuple[int, ...]:
        return get_bit_positions(data, self.hash_count, self.bitset_size)

    def __getitem__(self, key: int) -> bool:
        if key < 0 or key >= self.bitset_size:
            raise IndexError

        return self.bits[key // 8] << (key & 7) != 0

    def __setitem__(self, key: int, value: bool) -> None:
        if key < 0 or key >= self.bitset_size:
            raise IndexError

        if value:
            self.bits[key // 8] |= 1 << (key & 7)
        else:
            self.bits[key // 8] &= ~(1 << (key & 7))


@dataclass
class PrivateKey:
    """BFE private key"""

    bloom_filter: BloomFilter
    secret_keys: List[Optional[G1]]
    key_size: int
    pk: G2

    def __getitem__(self, key: int) -> G1:
        value = self.secret_keys[key]
        if value is None:
            raise IndexError

        return value


@dataclass
class PublicKey:
    """BFE public key"""

    hash_count: int
    bitset_size: int
    key_size: int
    pk: G2


@dataclass
class Ciphertext:
    """BFE ciphertext"""

    u: G2
    v: Sequence[bytes]


def map_identity(identity: int) -> G1:
    return hash_to_G1(struct.pack("<Q", identity))


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
    pk = generator_G2(exponent)  # BF public key
    bloom_filter = BloomFilter(filter_size, false_positive_probability)

    # BF key extraction
    def extract(identity: int) -> G1:
        return map_identity(identity) ** exponent

    return (
        PrivateKey(
            bloom_filter,
            # extract derived keys for all identities
            [extract(identity) for identity in range(bloom_filter.bitset_size)],
            key_size,
            pk,
        ),
        PublicKey(bloom_filter.hash_count, bloom_filter.bitset_size, key_size, pk),
    )


def internal_encrypt(pkr: G2, identity: int, message: bytes) -> bytes:
    return hash_and_xor(pair(map_identity(identity), pkr), message)


def encaps(pk: PublicKey) -> Tuple[bytes, Ciphertext]:
    """Encapsulate a freshly sampled key."""

    # sample a random value for FO
    key = os.urandom(pk.key_size)
    # derive r and k
    r, k = hash_r(key, pk.key_size)

    u = generator_G2(r)
    # instead of applying r to each pairing, precompute pk ** r
    pkr = pk.pk ** r

    return k, Ciphertext(
        u,
        tuple(
            internal_encrypt(pkr, identity, key)
            for identity in get_bit_positions(bytes(u), pk.hash_count, pk.bitset_size)
        ),
    )


def puncture(sk: PrivateKey, ctxt: Ciphertext) -> None:
    """Puncture secret key on a ciphertext."""

    for identity in sk.bloom_filter.get_bit_positions(bytes(ctxt.u)):
        sk.bloom_filter[identity] = True  # set bit in Bloom filter
        sk.secret_keys[identity] = None  # remove associated key


def decaps(sk: PrivateKey, ctxt: Ciphertext) -> Optional[bytes]:
    """Decapsulate a key."""

    def internal_decrypt(sk: G1, v: bytes) -> bytes:
        return hash_and_xor(pair(sk, ctxt.u), v)

    # obtain encrypted key from one of the ciphertexts
    key: Optional[bytes] = None
    bit_positions = sk.bloom_filter.get_bit_positions(bytes(ctxt.u))
    for v, identity in zip(ctxt.v, bit_positions):
        # check if key is available for the identity
        if not sk.bloom_filter[identity]:
            key = internal_decrypt(sk[identity], v)
            break
    else:
        # no working derived keys available
        return None

    # derive r and k
    r, k = hash_r(key, sk.key_size)
    pkr = sk.pk ** r

    # recompute ciphertext and verify equality
    recomputed_u = generator_G2(r)
    recomputed_v = tuple(
        internal_encrypt(pkr, identity, key) for identity in bit_positions
    )
    return k if recomputed_u == ctxt.u and recomputed_v == ctxt.v else None


def test_bfe() -> None:
    # Generate a key pair (this will take forever)
    sk, pk = keygen(32, 2 ** 19, 0.0009765625)

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
