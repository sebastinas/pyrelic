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

from libc.stdint cimport uint8_t, uint64_t

cdef extern from "<relic/relic_core.h>" nogil:
    int RLC_OK
    int RLC_ERR
    int RLC_NEG
    int RLC_POS

    ctypedef struct ctx_t:
        pass

    # relic init and clean up
    int core_init()
    int core_clean()
    ctx_t* core_get()


cdef extern from "<relic/relic_conf.h>" nogil:
    cdef const char* RLC_VERSION


cdef extern from "<relic/relic_bn.h>" nogil:
    int WSIZE

    ctypedef uint64_t dig_t

    ctypedef struct bn_st:
        pass
    ctypedef bn_st bn_t[1]

    # bn init and clean up
    void bn_null(bn_t)
    void bn_new(bn_t)
    void bn_new_size(bn_t, int)
    void bn_free(bn_t)
    # copy
    void bn_copy(bn_t, const bn_t)

    # bn arithmetic
    void bn_zero(bn_t)
    void bn_add(bn_t, const bn_t, const bn_t)
    void bn_sub(bn_t, const bn_t, const bn_t)
    void bn_neg(bn_t, const bn_t)
    void bn_mul(bn_t, const bn_t, const bn_t)
    void bn_div(bn_t, const bn_t, const bn_t)
    void bn_mod(bn_t, const bn_t, const bn_t, ...)
    void bn_gcd_ext(bn_t, bn_t, bn_t, const bn_t, const bn_t)

    # bn serialization
    void bn_write_bin(uint8_t*, int, const bn_t)
    void bn_read_bin(bn_t, const uint8_t*, int)
    int bn_size_bin(const bn_t)
    void bn_read_str(bn_t, const char*, int, int)
    void bn_write_str(char*, int, const bn_t, int)
    int bn_size_str(const bn_t, int)
    void bn_read_raw(bn_t, const dig_t*, int)
    void bn_write_raw(dig_t*, int, const bn_t)
    int bn_size_raw(const bn_t)

    # bn comparison
    int bn_cmp(const bn_t, const bn_t)
    int bn_is_zero(const bn_t)

    # bn randomization
    void bn_rand(bn_t, int, int)
    void bn_rand_mod(bn_t, bn_t)


cdef extern from "<relic/relic_pc.h>" nogil:
    ctypedef struct ep_t:
        pass
    ctypedef struct ep2_t:
        pass
    ctypedef struct fp12_t:
        pass

    ctypedef ep_t g1_t
    ctypedef ep2_t g2_t
    ctypedef fp12_t gt_t

    # gx init and clean up
    void g1_null(g1_t)
    void g2_null(g2_t)
    void gt_null(gt_t)
    void g1_new(g1_t)
    void g2_new(g2_t)
    void gt_new(gt_t)
    void g1_free(g1_t)
    void g2_free(g2_t)
    void gt_free(gt_t)
    # gx copy
    void g1_copy(g1_t, const g1_t)
    void g2_copy(g2_t, const g2_t)
    void gt_copy(gt_t, const gt_t)

    # gx generators
    void g1_get_gen(g1_t)
    void g2_get_gen(g2_t)
    void gt_get_gen(gt_t)

    # gx arithmetic
    void g1_set_infty(g1_t)
    void g2_set_infty(g2_t)
    void gt_zero(gt_t)
    void gt_set_unity(gt_t)
    void g1_add(g1_t, const g1_t, const g1_t)
    void g2_add(g2_t, const g2_t, const g2_t)
    void g1_sub(g1_t, const g1_t, const g1_t)
    void g2_sub(g2_t, const g2_t, const g2_t)
    void g1_mul(g1_t, const g1_t, const bn_t)
    void g2_mul(g2_t, const g2_t, const bn_t)
    void gt_mul(gt_t, const gt_t, const gt_t)
    void g1_mul_gen(g1_t, const bn_t)
    void g2_mul_gen(g2_t, const bn_t)
    void g1_norm(g1_t, const g1_t)
    void g2_norm(g2_t, const g2_t)
    void g1_get_ord(bn_t)
    void g2_get_ord(bn_t)
    void g1_neg(g1_t, const g1_t)
    void g2_neg(g2_t, const g2_t)
    void g1_mul_sim(g1_t, g1_t, bn_t, g1_t, bn_t)
    void g2_mul_sim(g2_t, g2_t, bn_t, g2_t, bn_t)
    void gt_exp(gt_t, const gt_t, const bn_t)
    void gt_inv(gt_t, const gt_t)

    # gx comparison
    int g1_is_infty(const g1_t)
    int g2_is_infty(const g2_t)
    int gt_is_unity(const gt_t)
    int g1_cmp(const g1_t, const g1_t)
    int g2_cmp(const g2_t, const g2_t)
    int gt_cmp(const gt_t, const gt_t)

    # gx serializtion
    int gt_size_bin(const gt_t, int)
    void gt_write_bin(uint8_t*, int, const gt_t, int)
    void gt_read_bin(gt_t, const uint8_t*, int)
    int g2_size_bin(const g2_t, int)
    void g2_write_bin(uint8_t*, int, const g2_t, int)
    void g2_read_bin(g2_t, const uint8_t*, int)
    int g1_size_bin(const g1_t, int)
    void g1_write_bin(uint8_t*, int, const g1_t, int)
    void g1_read_bin(g1_t, const uint8_t*, int)

    # gx randomization
    void g1_rand(g1_t)
    void g2_rand(g2_t)
    void gt_rand(gt_t)

    # gx hash
    void g1_map(g1_t, const uint8_t*, int)
    void g2_map(g2_t, const uint8_t*, int)

    # pairings
    void pc_map(gt_t, const g1_t, const g2_t)
    void pc_map_sim(gt_t, const g1_t*, const g2_t*, int)
    int pc_param_set_any()
