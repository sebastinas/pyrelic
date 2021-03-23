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

# cython: language_level=3, binding=True

from . cimport relic
from cpython.object cimport Py_LT, Py_EQ, Py_GT, Py_LE, Py_NE, Py_GE
from cpython cimport int as Integer
from libc.stdint cimport uint8_t
from libc.stdlib cimport malloc, free


cdef extern from "Python.h":
    size_t _PyLong_NumBits(object) except -1


cdef extern from *:
    """
    #include <relic/relic_conf.h>
    #if !defined(WITH_PC)
    #error "Relic built without pairing support!"
    #endif
    """


_relic_version = tuple(map(Integer, relic.RLC_VERSION.split(b".")))


cdef class Relic:
    """Context manager to intialize relic.

    Usage of all other functions and classes needs to happen within a `Relic`
    context.
    """

    cdef int code_core
    cdef int code_pairing

    def __init__(self):
        self.code_core = relic.RLC_ERR
        self.code_pairing = relic.RLC_ERR

    def __enter__(self):
        # relic up to 0.5.0 does not perform internal refcounting
        if _relic_version <= (0, 5, 0):
            if relic.core_get() is not NULL:
                return self

        self.code_core = relic.core_init()
        if self.code_core != relic.RLC_OK:
            raise RuntimeError("Failed to initialize relic!")
        self.code_pairing = relic.pc_param_set_any()
        if self.code_pairing != relic.RLC_OK:
            raise RuntimeError("Failed to initialize relic (pairing)!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.code_core == relic.RLC_OK:
            relic.core_clean()


cdef class BN:
    """Represents an arbitrary length integer."""

    def __cinit__(self):
        relic.bn_null(self.value)

    def __init__(self, bytes buf=None):
        relic.bn_new(self.value)
        if buf is not None:
            relic.bn_read_bin(self.value, buf, len(buf))

    def __dealloc__(self):
        relic.bn_free(self.value)

    def copy(self):
        cdef BN other = BN()
        relic.bn_copy(other.value, self.value)
        return other

    # arithmetic operations

    def __iadd__(self, other):
        cdef BN tmp
        if isinstance(other, BN):
            relic.bn_add(self.value, self.value, (<BN>other).value)
        elif isinstance(other, int):
            tmp = BN_from_int(other)
            relic.bn_add(self.value, self.value, tmp.value)
        else:
            return NotImplemented
        return self

    def __add__(self, other):
        cdef BN result
        cdef BN self_bn

        if isinstance(self, BN):
            self_bn = <BN>self
        elif isinstance(self, int):
            self_bn = BN_from_int(self)
        else:
            return NotImplemented

        if isinstance(other, BN):
            result = BN()
            relic.bn_add(result.value, self_bn.value, (<BN>other).value)
        elif isinstance(other, int):
            result = BN_from_int(other)
            relic.bn_add(result.value, self_bn.value, result.value)
        else:
            return NotImplemented
        return result

    def __isub__(self, other):
        cdef BN tmp
        if isinstance(other, BN):
            relic.bn_sub(self.value, self.value, (<BN>other).value)
        elif isinstance(other, int):
            tmp = BN_from_int(other)
            relic.bn_sub(self.value, self.value, tmp.value)
        else:
            return NotImplemented
        return self

    def __sub__(self, other):
        cdef BN result
        cdef BN self_bn

        if isinstance(self, BN):
            self_bn = <BN>self
        elif isinstance(self, int):
            self_bn = BN_from_int(self)
        else:
            return NotImplemented

        if isinstance(other, BN):
            result = BN()
            relic.bn_sub(result.value, self_bn.value, (<BN>other).value)
        elif isinstance(other, int):
            result = BN_from_int(other)
            relic.bn_sub(result.value, self_bn.value, result.value)
        else:
            return NotImplemented
        return result

    def __neg__(self):
        cdef BN result = BN()
        relic.bn_neg(result.value, self.value)
        return result

    def __imul__(self, other):
        cdef BN tmp
        if isinstance(other, BN):
            relic.bn_mul(self.value, self.value, (<BN>other).value)
        elif isinstance(other, int):
            tmp = BN_from_int(other)
            relic.bn_mul(self.value, self.value, tmp.value)
        else:
            return NotImplemented
        return self

    def __mul__(self, other):
        cdef BN result
        cdef BN self_bn

        if isinstance(self, BN):
            self_bn = <BN>self
        elif isinstance(self, int):
            self_bn = BN_from_int(self)
        else:
            return NotImplemented

        if isinstance(other, BN):
            result = BN()
            relic.bn_mul(result.value, self_bn.value, (<BN>other).value)
        elif isinstance(other, int):
            result = BN_from_int(other)
            relic.bn_mul(result.value, self_bn.value, result.value)
        else:
            return NotImplemented
        return result

    def __mod__(BN self, BN other):
        cdef BN result = BN()
        relic.bn_mod(result.value, self.value, other.value)
        return result

    def mod_inv(BN self, BN mod):
        cdef BN result = BN()
        cdef BN c = BN()
        relic.bn_gcd_ext(c.value, result.value, NULL, self.value, mod.value)
        return result % mod

    def mod_neg(BN self, BN mod):
        return (-self) % mod

    # comparisons

    def __hash__(self):
        return hash(bytes(self))

    def __richcmp__(self, other, int op):
        cdef int ret
        if not isinstance(other, BN):
            return NotImplemented

        ret = relic.bn_cmp(self.value, (<BN>other).value)
        if op == Py_EQ:
            return ret == 0
        elif op == Py_NE:
            return ret != 0
        elif op == Py_LT:
            return ret < 0
        elif op == Py_LE:
            return ret <= 0
        elif op == Py_GT:
            return ret > 0
        return ret >= 0

    def __nonzero__(self):
        return not relic.bn_is_zero(self.value)

    # conversion to bytes/strs/ints

    def __bytes__(self):
        cdef int size = relic.bn_size_bin(self.value)
        buf = bytearray(size)
        relic.bn_write_bin(buf, size, self.value)
        return bytes(buf)

    def __repr__(self):
        return f"BN({bytes(self)!r})"

    cdef str as_string(self, int radix=16):
        cdef int size = relic.bn_size_str(self.value, radix)
        buf = bytearray(size)
        relic.bn_write_str(buf, size, self.value, radix)
        return buf[:size - 1].decode("ascii")

    def __str__(self):
        return self.as_string(radix=16)

    def __int__(self):
        cdef int length = relic.bn_size_raw(self.value)
        cdef int idx
        cdef relic.dig_t* buf = <relic.dig_t*>malloc(sizeof(relic.dig_t) * length)
        cdef Integer result = 0

        try:
            relic.bn_write_raw(buf, length, self.value)
            for idx in range(length):
                result |= Integer(buf[idx]) << (relic.WSIZE * idx)
        finally:
            free(buf)

        return result

    @staticmethod
    def from_str(str data, int radix=16):
        bdata = data.encode("ascii")
        cdef const char* sdata = bdata
        cdef BN bn = BN()
        relic.bn_read_str(bn.value, sdata, len(bdata), radix)
        return bn


cpdef BN neutral_BN():
    """Return zero as BN."""

    cdef BN value = BN()
    relic.bn_zero(value.value)
    return value


cpdef BN rand_BN_mod(BN mod):
    """Return a randomly sampled BN in [0, mod)."""

    cdef BN value = BN()
    relic.bn_rand_mod(value.value, mod.value)
    return value


def rand_BN_order():
    """Returns a randomly sampled exponent."""

    cdef BN value = BN()
    cdef BN order = BN()
    relic.g1_get_ord(order.value)
    relic.bn_rand_mod(value.value, order.value)
    return value


cdef BN BN_from_int_implementation(Integer data):
    cdef int length = (_PyLong_NumBits(data) + relic.WSIZE - 1) // relic.WSIZE
    cdef int idx
    cdef relic.dig_t mask = -1
    cdef BN result = BN()
    cdef relic.dig_t* buf = <relic.dig_t*>malloc(sizeof(relic.dig_t) * length)

    try:
        for idx in range(length):
            buf[idx] = (data >> (relic.WSIZE * idx)) & mask
        relic.bn_read_raw(result.value, buf, length)
    finally:
        free(buf)

    return result


cpdef BN BN_from_int(Integer data):
    """Convert a Python integer to BN."""

    cdef BN result
    if data < 0:
        result = BN_from_int_implementation(-data)
        relic.bn_neg(result.value, result.value)
    else:
        result = BN_from_int_implementation(data)
    return result


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

    def __truediv__(G1 self, G1 other):
        cdef G1 result = G1()
        relic.g1_sub(result.value, self.value, other.value)
        return result

    def __pow__(G1 self, exp, modulo):
        cdef G1 result = G1()
        cdef BN tmp
        if isinstance(exp, BN):
            relic.g1_mul(result.value, self.value, (<BN>exp).value)
        elif isinstance(exp, int):
            if exp < 0:
                relic.g1_neg(result.value, self.value)
                tmp = BN_from_int(-exp)
                relic.g1_mul(result.value, result.value, tmp.value)
            else:
                tmp = BN_from_int(exp)
                relic.g1_mul(result.value, self.value, tmp.value)
        else:
            return NotImplemented

        return result

    def __hash__(self):
        return hash(bytes(self))

    def __eq__(self, other):
        if not isinstance(other, G1):
            return NotImplemented
        return relic.g1_cmp(self.value, (<G1>other).value) == 0

    def __ne__(self, other):
        if not isinstance(other, G1):
            return NotImplemented
        return relic.g1_cmp(self.value, (<G1>other).value) != 0

    def __bytes__(self):
        cdef int size = relic.g1_size_bin(self.value, 0)
        buf = bytearray(size)
        relic.g1_write_bin(buf, size, self.value, 0)
        return bytes(buf)

    def __repr__(self):
        return f"G1({bytes(self)!r})"

    def normalize(self):
        relic.g1_norm(self.value, self.value)

    def invert(self):
        cdef G1 result = G1()
        relic.g1_neg(result.value, self.value)
        return result


cpdef BN order():
    """Returns the group order of G1."""

    cdef BN order = BN()
    relic.g1_get_ord(order.value)
    return order


cpdef G1 generator_G1(BN exponent=None):
    """Returns the generator of G1 and if the optional exponent is given, the generator raised to
    this exponent is returned."""

    cdef G1 generator = G1()
    if exponent is not None:
        relic.g1_mul_gen(generator.value, exponent.value)
    else:
        relic.g1_get_gen(generator.value)
    return generator


cpdef G1 neutral_G1():
    """Returns the neutral element of G1."""

    cdef G1 neutral = G1()
    relic.g1_set_infty(neutral.value)
    return neutral


cpdef G1 rand_G1():
    """Returns a randomly sampled element from G1."""

    cdef G1 value = G1()
    relic.g1_rand(value.value)
    return value


cpdef G1 hash_to_G1(bytes data):
    """Hashes a byte string to an element in G1."""

    cdef const uint8_t[::1] view = data
    cdef G1 value = G1()
    relic.g1_map(value.value, &view[0], view.size);
    return value


cpdef G1 mul_sim_G1(values, scalars, G1 base=None):
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


cdef class G2:
    """Represents an element in the (multiplicative) group G2."""

    def __cinit__(self):
        relic.g2_null(self.value)

    def __init__(self, bytes buf=None):
        relic.g2_new(self.value)
        if buf is not None:
            relic.g2_read_bin(self.value, buf, len(buf))

    def __dealloc__(self):
        relic.g2_free(self.value)

    def __imul__(self, G2 other):
        relic.g2_add(self.value, self.value, other.value)

    def __mul__(G2 self, G2 other):
        cdef G2 result = G2()
        relic.g2_add(result.value, self.value, other.value)
        return result

    def __truediv__(G2 self, G2 other):
        cdef G2 result = G2()
        relic.g2_sub(result.value, self.value, other.value)
        return result

    def __pow__(G2 self, exp, modulo):
        cdef G2 result = G2()
        cdef BN tmp
        if isinstance(exp, BN):
            relic.g2_mul(result.value, self.value, (<BN>exp).value)
        elif isinstance(exp, int):
            if exp < 0:
                relic.g2_neg(result.value, self.value)
                tmp = BN_from_int(-exp)
                relic.g2_mul(result.value, result.value, tmp.value)
            else:
                tmp = BN_from_int(exp)
                relic.g2_mul(result.value, self.value, tmp.value)
        else:
            return NotImplemented

        return result

    def __hash__(self):
        return hash(bytes(self))

    def __eq__(self, other):
        if not isinstance(other, G2):
            return NotImplemented
        return relic.g2_cmp(self.value, (<G2>other).value) == 0

    def __ne__(self, other):
        if not isinstance(other, G2):
            return NotImplemented
        return relic.g2_cmp(self.value, (<G2>other).value) != 0

    def __nonzero__(self):
        return not relic.g2_is_infty(self.value)

    def normalize(self):
        relic.g2_norm(self.value, self.value)

    def __bytes__(self):
        cdef int size = relic.g2_size_bin(self.value, 0)
        buf = bytearray(size)
        relic.g2_write_bin(buf, size, self.value, 0)
        return bytes(buf)

    def __repr__(self):
        return f"G2({bytes(self)!r})"

    def invert(self):
        cdef G2 result = G2()
        relic.g2_neg(result.value, self.value)
        return result


cpdef G2 generator_G2(BN exponent=None):
    """Returns the generator of G2 and if the optional exponent is given, the generator raised to
    this exponent is returned."""

    cdef G2 generator = G2()
    if exponent is not None:
        relic.g2_mul_gen(generator.value, exponent.value)
    else:
        relic.g2_get_gen(generator.value)
    return generator


cpdef G2 neutral_G2():
    """Returns the neutral element of G2."""

    cdef G2 neutral = G2()
    relic.g2_set_infty(neutral.value)
    return neutral


cpdef G2 rand_G2():
    """Returns a randomly sampled element from G2."""

    cdef G2 value = G2()
    relic.g2_rand(value.value)
    return value


cpdef G2 hash_to_G2(bytes data):
    """Hashes a byte string to an element in G2."""

    cdef const uint8_t[::1] view = data
    cdef G2 value = G2()
    relic.g2_map(value.value, &view[0], view.size);
    return value


cpdef G2 mul_sim_G2(values, scalars, G2 base=None):
    """Computes the product of all elements raised to the respective scalars."""

    cdef size_t length = len(values), idx
    cdef G2 lhs, rhs, tmp1 = G2(), result = G2()
    cdef BN lhs_scalar, rhs_scalar

    if length != <size_t>len(scalars):
        raise ValueError("Length of values and scalars does not match")

    if base is not None:
        relic.g2_copy(result.value, base.value)
    else:
        relic.g2_set_infty(result.value)

    for idx in range(0, length & ~1, 2):
        if not isinstance(values[idx], G2) or not isinstance(scalars[idx], BN):
            raise TypeError(f"Expected G2, BN at index {idx} of values and scalars.")
        if not isinstance(values[idx + 1], G2) or not isinstance(scalars[idx + 1], BN):
            raise TypeError(f"Expected G2, BN at index {idx + 1} of values and scalars.")

        lhs = <G2>values[idx]
        lhs_scalar = <BN>scalars[idx]
        rhs = <G2>values[idx + 1]
        rhs_scalar = <BN>scalars[idx + 1]

        relic.g2_mul_sim(tmp1.value, lhs.value, lhs_scalar.value, rhs.value, rhs_scalar.value)
        relic.g2_add(result.value, result.value, tmp1.value)

    if length & 1:
        idx = length - 1
        if not isinstance(values[idx], G2) or not isinstance(scalars[idx], BN):
            raise TypeError(f"Expected G2, BN at index {idx} of values and scalars.")

        lhs = <G2>values[idx]
        lhs_scalar = <BN>scalars[idx]
        relic.g2_mul(tmp1.value, lhs.value, lhs_scalar.value)
        relic.g2_add(result.value, result.value, tmp1.value)
    return result


cdef class GT:
    """Represents an element in the (multiplicative) group GT."""

    def __cinit__(self):
        relic.gt_null(self.value)

    def __init__(self, bytes buf=None):
        relic.gt_new(self.value)
        if buf is not None:
            relic.gt_read_bin(self.value, buf, len(buf))

    def __dealloc__(self):
        relic.gt_free(self.value)

    def __imul__(GT self, GT other):
        relic.gt_mul(self.value, self.value, other.value)
        return self

    def __mul__(GT self, GT other):
        cdef GT result = GT()
        relic.gt_mul(result.value, self.value, other.value)
        return result

    def __truediv__(GT self, GT other):
        cdef GT result = GT()
        relic.gt_inv(result.value, other.value)
        relic.gt_mul(result.value, result.value, self.value)
        return result

    def __pow__(GT self, exp, modulo):
        cdef GT result = GT()
        cdef BN tmp
        if isinstance(exp, BN):
            relic.gt_exp(result.value, self.value, (<BN>exp).value)
        elif isinstance(exp, int):
            if exp < 0:
                relic.gt_inv(result.value, self.value)
                tmp = BN_from_int(-exp)
                relic.gt_exp(result.value, result.value, tmp.value)
            else:
                tmp = BN_from_int(exp)
                relic.gt_exp(result.value, self.value, tmp.value)
        else:
            return NotImplemented

        return result

    def __hash__(self):
        return hash(bytes(self))

    def __eq__(self, other):
        if not isinstance(other, GT):
            return NotImplemented
        return relic.gt_cmp(self.value, (<GT>other).value) == 0

    def __ne__(self, GT other):
        if not isinstance(other, GT):
            return NotImplemented
        return relic.gt_cmp(self.value, (<GT>other).value) != 0

    def __bytes__(self):
        cdef int size = relic.gt_size_bin(self.value, 0)
        buf = bytearray(size)
        relic.gt_write_bin(buf, size, self.value, 0)
        return bytes(buf)

    def __repr__(self):
        return f"GT({bytes(self)!r})"


cpdef GT generator_GT(BN exponent=None):
    """Return the generator of GT and if the optional exponent is given, the generator raised to
    this exponent is returned."""

    cdef GT generator = GT()
    relic.gt_get_gen(generator.value)
    return generator if exponent is None else generator ** exponent


cpdef GT rand_GT():
    """Returns a randomly sampled element from GT."""

    cdef GT value = GT()
    relic.gt_rand(value.value)
    return value

cpdef GT neutral_GT():
    """Returns the neutral element of GT."""

    cdef GT value = GT()
    relic.gt_set_unity(value.value)
    return value


cpdef GT pair(G1 g1, G2 g2):
    """Computes the pairing of g1 and g2."""

    cdef GT result = GT()
    relic.pc_map(result.value, g1.value, g2.value)
    return result


def pair_product(*args):
    """Given a list of pairs of G1 and G2 elements, computes the product of their pairings."""

    cdef int length = len(args), idx
    cdef relic.g1_t* g1s = NULL
    cdef relic.g2_t* g2s = NULL
    cdef GT result = GT()

    if length == 0:
        # empty products return 1
        relic.gt_set_unity(result.value)
        return result

    if length == 1:
        # fall back to pc_map if only one pair was provided
        cur_args_0, cur_args_1 = args[0]
        if not isinstance(cur_args_0, G1) or not isinstance(cur_args_1, G2):
            raise TypeError("Expected a tuple of (G1, G2) at index 0.")

        relic.pc_map(result.value, (<G1>cur_args_0).value, (<G2>cur_args_1).value)
        return result

    try:
        g1s = <relic.g1_t*>malloc(sizeof(relic.g1_t) * length)
        for idx in range(length):
            relic.g1_null(g1s[idx])

        g2s = <relic.g2_t*>malloc(sizeof(relic.g2_t) * length)
        for idx in range(length):
            relic.g2_null(g2s[idx])

        try:
            for idx in range(length):
                cur_args_0, cur_args_1 = args[idx]
                if not isinstance(cur_args_0, G1) or not isinstance(cur_args_1, G2):
                    raise TypeError(f"Expected a tuple of (G1, G2) at index {idx}.")

                relic.g1_new(g1s[idx])
                relic.g1_copy(g1s[idx], (<G1>cur_args_0).value)
                relic.g2_new(g2s[idx])
                relic.g2_copy(g2s[idx], (<G2>cur_args_1).value)

            relic.pc_map_sim(result.value, g1s, g2s, length)
        finally:
            for idx in reversed(range(length)):
                relic.g2_free(g2s[idx])
            for idx in reversed(range(length)):
                relic.g1_free(g1s[idx])
    finally:
        free(g2s)
        free(g1s)

    return result
