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

from .core import Relic
from .bn import (
    BN,
    from_int as BN_from_int,
    rand_mod as rand_BN_mod,
    zero as neutral_BN,
)
from .g1 import (
    G1,
    generator as generator_G1,
    hash_to as hash_to_G1,
    mul_sim as mul_sim_G1,
    neutral as neutral_G1,
    order,
    rand as rand_G1,
    rand_BN_order,
)
from .g2 import (
    G2,
    generator as generator_G2,
    hash_to as hash_to_G2,
    mul_sim as mul_sim_G2,
    neutral as neutral_G2,
    rand as rand_G2,
)
from .gt import (
    GT,
    generator as generator_GT,
    neutral as neutral_GT,
    rand as rand_GT,
)
from .pair import pair, pair_product
