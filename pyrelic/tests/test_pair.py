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

import unittest
import pyrelic
import math
import sys


class TestPair(unittest.TestCase):
    def test_pair_generators(self):
        gt = pyrelic.pair(pyrelic.generator_G1(), pyrelic.generator_G2())
        self.assertEqual(gt, pyrelic.generator_GT())

    def test_pair_neutral(self):
        gt = pyrelic.pair(pyrelic.neutral_G1(), pyrelic.generator_G2())
        self.assertEqual(gt, pyrelic.neutral_GT())

        gt = pyrelic.pair(pyrelic.generator_G1(), pyrelic.neutral_G2())
        self.assertEqual(gt, pyrelic.neutral_GT())

    def test_pair_bilinear(self):
        x = pyrelic.rand_BN_order()
        g1 = pyrelic.rand_G1()
        g2 = pyrelic.rand_G2()
        gt_base = pyrelic.pair(g1, g2)

        self.assertEqual(pyrelic.pair(g1 ** x, g2), gt_base ** x)
        self.assertEqual(pyrelic.pair(g1, g2 ** x), gt_base ** x)


class TestPairingProduct(unittest.TestCase):
    def test_pair_product_0(self):
        self.assertEqual(pyrelic.pair_product(), pyrelic.neutral_GT())

    def test_pair_product_1(self):
        g1 = pyrelic.rand_G1()
        g2 = pyrelic.rand_G2()

        self.assertEqual(pyrelic.pair_product((g1, g2)), pyrelic.pair(g1, g2))

    @unittest.skipUnless(sys.version_info[:2] >= (3, 8), "Requires math.prod")
    def test_pair_product_l(self):
        l = 5
        elements = [(pyrelic.rand_G1(), pyrelic.rand_G2()) for _ in range(l)]

        self.assertEqual(
            pyrelic.pair_product(*elements),
            math.prod(
                (pyrelic.pair(g1, g2) for g1, g2 in elements),
                start=pyrelic.neutral_GT(),
            ),
        )


if __name__ == "__main__":
    unittest.main()
