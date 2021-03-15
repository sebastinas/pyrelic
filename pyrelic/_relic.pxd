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
from cpython cimport int as Integer

cdef class BN:
    cdef relic.bn_t value

    cdef str as_string(self, int radix=*)

cpdef BN neutral_BN()
cpdef BN rand_BN_mod(BN mod)
cpdef BN BN_from_int(Integer data)

cdef class G1:
    cdef relic.g1_t value

cpdef BN order()
cpdef G1 generator_G1(BN exponent=*)
cpdef G1 neutral_G1()
cpdef G1 rand_G1()
cpdef G1 hash_to_G1(bytes data)
cpdef G1 mul_sim_G1(values, scalars, G1 base=*)

cdef class G2:
    cdef relic.g2_t value

cpdef G2 generator_G2(BN exponent=*)
cpdef G2 neutral_G2()
cpdef G2 rand_G2()
cpdef G2 hash_to_G2(bytes data)
cpdef G2 mul_sim_G2(values, scalars, G2 base=*)

cdef class GT:
    cdef relic.gt_t value

cpdef GT generator_GT(BN exponent=*)
cpdef GT rand_GT()
cpdef GT neutral_GT()
