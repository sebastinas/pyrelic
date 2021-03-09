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

# cython: language_level=3, bind=true

from . cimport relic
from .bn cimport BN, from_int
from libc.stdint cimport uint8_t


cdef class G1:
    """Represents an element in the (multiplicative) group G1."""

    def __cinit__(self):
        relic.g1_null(self.value)

    def __init__(self, bytes buf=None):
        relic.g1_new(self.value)
        if buf is not None:
            relic.g1_read_bin(self.value, buf, len(buf))

    def __dealloc__(self):
        relic.g1_free(self.value)

    def __imul__(self, G1 other):
        relic.g1_add(self.value, self.value, other.value)

    def __mul__(G1 self, G1 other):
        cdef G1 result = G1()
        relic.g1_add(result.value, self.value, other.value)
        return result

    def __pow__(G1 self, exp, modulo):
        cdef G1 result = G1()
        cdef BN tmp
        if isinstance(exp, BN):
            relic.g1_mul(result.value, self.value, (<BN>exp).value)
        elif isinstance(exp, int):
            if exp < 0:
                relic.g1_neg(result.value, self.value)
                tmp = from_int(-exp)
                relic.g1_mul(result.value, result.value, tmp.value)
            else:
                tmp = from_int(exp)
                relic.g1_mul(result.value, self.value, tmp.value)
        else:
            return NotImplemented

        return result

    def __hash__(self):
        return hash(bytes(self))

    def __eq__(self, G1 other):
        return relic.g1_cmp(self.value, other.value) == 0

    def __ne__(self, G1 other):
        return relic.g1_cmp(self.value, other.value) != 0

#   def __nonzero__(self):
#       return not relic.g1_is_infty(self.value)

    def normalize(self):
        relic.g1_norm(self.value, self.value)

    def __bytes__(self):
        cdef int size = relic.g1_size_bin(self.value, 0)
        buf = bytearray(size)
        relic.g1_write_bin(buf, size, self.value, 0)
        return bytes(buf)

cpdef G1 generator(BN exponent=None):
    """Returns the generator of G1 and if the optional exponent is given, the generator raised to
    this exponent is returned."""

    cdef G1 generator = G1()
    if exponent is not None:
        relic.g1_mul_gen(generator.value, exponent.value)
    else:
        relic.g1_get_gen(generator.value)
    return generator


cpdef BN order():
    """Returns the group order of G1."""

    cdef BN order = BN()
    relic.g1_get_ord(order.value)
    return order


cpdef G1 neutral():
    """Returns the neutral element of G1."""

    cdef G1 neutral = G1()
    relic.g1_set_infty(neutral.value)
    return neutral


cpdef G1 rand():
    """Returns a randomly sampled element from G1."""

    cdef G1 value = G1()
    relic.g1_rand(value.value)
    return value


cpdef G1 hash_to(bytes data):
    """Hashes a byte string to an element in G1."""

    cdef const uint8_t[::1] view = data
    cdef G1 value = G1()
    relic.g1_map(value.value, &view[0], view.size);
    return value


cpdef G1 mul_sim(values, scalars, G1 base=None):
    """Computes the product of all elements raised to the respective scalars."""

    cdef size_t length = len(values), idx
    cdef G1 lhs, rhs, tmp1 = G1(), result = G1()
    cdef BN lhs_scalar, rhs_scalar

    if length != <size_t>len(scalars):
        raise ValueError("Length of values and scalars does not match")

    if base is not None:
        relic.g1_copy(result.value, base.value)
    else:
        relic.g1_set_infty(result.value)

    for idx in range(0, length & ~1, 2):
        if not isinstance(values[idx], G1) or not isinstance(scalars[idx], BN):
            raise TypeError(f"Expected G1, BN at index {idx} of values and scalars.")
        if not isinstance(values[idx + 1], G1) or not isinstance(scalars[idx + 1], BN):
            raise TypeError(f"Expected G1, BN at index {idx + 1} of values and scalars.")

        lhs = <G1>values[idx]
        lhs_scalar = <BN>scalars[idx]
        rhs = <G1>values[idx + 1]
        rhs_scalar = <BN>scalars[idx + 1]

        relic.g1_mul_sim(tmp1.value, lhs.value, lhs_scalar.value, rhs.value, rhs_scalar.value)
        relic.g1_add(result.value, result.value, tmp1.value)

    if length & 1:
        idx = length - 1
        if not isinstance(values[idx], G1) or not isinstance(scalars[idx], BN):
            raise TypeError(f"Expected G1, BN at index {idx} of values and scalars.")

        lhs = <G1>values[idx]
        lhs_scalar = <BN>scalars[idx]
        relic.g1_mul(tmp1.value, lhs.value, lhs_scalar.value)
        relic.g1_add(result.value, result.value, tmp1.value)
    return result


def rand_BN_order():
    """Returns a randomly sampled exponent."""

    cdef BN value = BN()
    cdef BN order = BN()
    relic.g1_get_ord(order.value)
    relic.bn_rand_mod(value.value, order.value)
    return value
