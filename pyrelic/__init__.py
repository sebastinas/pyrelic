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

from ._relic import (
    Relic,
    # BN
    BN,
    BN_from_int,
    rand_BN_mod,
    neutral_BN,
    # G1
    G1,
    generator_G1,
    hash_to_G1,
    mul_sim_G1,
    neutral_G1,
    order,
    rand_G1,
    rand_BN_order,
    # G2
    G2,
    generator_G2,
    hash_to_G2,
    mul_sim_G2,
    neutral_G2,
    rand_G2,
    # Gt
    GT,
    generator_GT,
    neutral_GT,
    rand_GT,
    # pairings
    pair,
    pair_product,
)

__version__ = "0.1"
__author__ = "Sebastian Ramacher"
__license__ = "MIT"
__copyright__ = f"(C) 2021 {__author__}"
