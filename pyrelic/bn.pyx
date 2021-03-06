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
from cpython.object cimport Py_LT, Py_EQ, Py_GT, Py_LE, Py_NE, Py_GE


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
            tmp = from_int(other)
            relic.bn_add(self.value, self.value, tmp.value)
        else:
            return NotImplemented
        return self

    def __add__(self, other):
        cdef BN result
        cdef BN self_bn

        if not isinstance(self, BN):
            return NotImplemented

        self_bn = <BN>self
        if isinstance(other, BN):
            result = BN()
            relic.bn_add(result.value, self_bn.value, (<BN>other).value)
        elif isinstance(other, int):
            result = from_int(other)
            relic.bn_add(result.value, self_bn.value, result.value)
        else:
            return NotImplemented
        return result

    def __isub__(self, other):
        cdef BN tmp
        if isinstance(other, BN):
            relic.bn_sub(self.value, self.value, (<BN>other).value)
        elif isinstance(other, int):
            tmp = from_int(other)
            relic.bn_sub(self.value, self.value, tmp.value)
        else:
            return NotImplemented
        return self

    def __sub__(BN self, BN other):
        cdef BN result
        cdef BN self_bn

        if not isinstance(self, BN):
            return NotImplemented

        self_bn = <BN>self
        if isinstance(other, BN):
            result = BN()
            relic.bn_sub(result.value, self_bn.value, (<BN>other).value)
        elif isinstance(other, int):
            result = from_int(other)
            relic.bn_sub(result.value, self_bn.value, result.value)
        else:
            return NotImplemented
        return result

    def __neg__(self):
        cdef BN result = BN()
        relic.bn_neg(result.value, self.value)
        return result

    def __imul__(self, BN other):
        cdef BN tmp
        if isinstance(other, BN):
            relic.bn_mul(self.value, self.value, (<BN>other).value)
        elif isinstance(other, int):
            tmp = from_int(other)
            relic.bn_mul(self.value, self.value, tmp.value)
        else:
            return NotImplemented
        return self

    def __mul__(BN self, BN other):
        cdef BN result
        cdef BN self_bn

        if not isinstance(self, BN):
            return NotImplemented

        self_bn = <BN>self
        if isinstance(other, BN):
            result = BN()
            relic.bn_mul(result.value, self_bn.value, (<BN>other).value)
        elif isinstance(other, int):
            result = from_int(other)
            relic.bn_mul(result.value, self_bn.value, result.value)
        else:
            return NotImplemented
        return result

    def __mod__(BN self, BN other):
        cdef BN result = BN()
        relic.bn_mod(result.value, self.value, other.value)
        return result

#   def mod_inv(BN self, BN mod):
#       cdef BN result = BN()
#       relic.bn_mod_inv(result.value, self.value, mod.value)
#       return result

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

    def str(self, int radix=16):
        cdef int size = relic.bn_size_str(self.value, radix)
        buf = bytearray(size)
        relic.bn_write_str(buf, size, self.value, radix)
        return buf.decode("ascii")

    def __str__(self):
        return self.str(radix=16)

    def __int__(self):
        return int(str(self), 16)

    @staticmethod
    def from_str(str data, int radix=16):
        bdata = data.encode("ascii")
        cdef const char* sdata = bdata
        cdef BN bn = BN()
        relic.bn_read_str(bn.value, sdata, len(bdata), radix)
        return bn


cpdef BN zero():
    """Return zero as BN."""

    cdef BN value = BN()
    relic.bn_zero(value.value)
    return value


cpdef BN rand_mod(BN mod):
    """Return a randomly sampled BN in [0, mod)."""

    cdef BN value = BN()
    relic.bn_rand_mod(value.value, mod.value)
    return value


cpdef BN from_int(object data):
    """Convert a Python integer to BN."""

    return BN.from_str(hex(data)[2:])
