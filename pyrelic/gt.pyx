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
from .bn cimport BN

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

    def __mul__(GT self, GT other):
        cdef GT result = GT()
        relic.gt_mul(result.value, self.value, other.value)
        return result

    def __truediv__(GT self, GT other):
        cdef GT result = GT()
        relic.gt_inv(result.value, other.value)
        relic.gt_mul(result.value, result.value, self.value)
        return result

    def __pow__(GT self, BN exp, modulo):
        cdef GT result = GT()
        relic.gt_exp(result.value, self.value, exp.value)
        return result

    def __hash__(self):
        return hash(bytes(self))

    def __eq__(self, GT other):
        return relic.gt_cmp(self.value, other.value) == 0

    def __ne__(self, GT other):
        return relic.gt_cmp(self.value, other.value) != 0

    def __bytes__(self):
        cdef int size = relic.gt_size_bin(self.value, 0)
        buf = bytearray(size)
        relic.gt_write_bin(buf, size, self.value, 0)
        return bytes(buf)


cpdef GT generator(BN exponent=None):
    """Return the generator of GT and if the optional exponent is given, the generator raised to
    this exponent is returned."""

    cdef GT generator = GT()
    relic.gt_get_gen(generator.value)
    return generator if exponent is None else generator ** exponent


cpdef GT rand():
    """Returns a randomly sampled element from GT."""

    cdef GT value = GT()
    relic.gt_rand(value.value)
    return value

cpdef GT neutral():
    """Returns the neutral element of G2."""

    cdef GT value = GT()
    relic.gt_set_unity(value.value)
    return value
