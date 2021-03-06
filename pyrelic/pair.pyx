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
from .g1 cimport G1
from .g2 cimport G2
from .gt cimport GT
from libc.stdlib cimport malloc, free


def pair(G1 g1, G2 g2):
    """Computes the pairing of g1 and g2."""

    cdef GT result = GT()
    relic.pc_map(result.value, g1.value, g2.value)
    return result


def pair_product(*args):
    """Given a list if pairs of G1 and G2 elements, computes the product of their pairings."""

    cdef int length = len(args), idx
    cdef relic.g1_t* g1s = NULL
    cdef relic.g2_t* g2s = NULL
    cdef GT result = GT()
    if length == 0:
        raise ValueError("Expected list of length >= 1")
    if length == 1:
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
            for idx in range(length):
                relic.g2_free(g2s[idx])
            for idx in range(length):
                relic.g1_free(g1s[idx])
    finally:
        free(g2s)
        free(g1s)

    return result
