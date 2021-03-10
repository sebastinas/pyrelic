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
from . import RelicTestCase


class GroupTests:
    def test_bytes(self):
        element = self.rand()
        bytes_element = bytes(element)

        self.assertEqual(element, self.group(bytes_element))

    def test_neutral(self):
        element = self.neutral()

        self.assertEqual(element ** 2, element)

    def test_generator(self):
        exp = pyrelic.rand_BN_order()

        self.assertEqual(self.generator(exp), self.generator() ** exp)

    def test_mul(self):
        exp1 = 5
        exp2 = 1024
        lhs = self.generator(pyrelic.BN_from_int(exp1))
        rhs = self.generator(pyrelic.BN_from_int(exp2))

        self.assertEqual(lhs * rhs, self.generator(pyrelic.BN_from_int(exp1 + exp2)))

    def test_div(self):
        lhs = self.rand()
        self.assertEqual(lhs / lhs, self.neutral())

    def test_div_exp(self):
        lhs = self.rand()
        self.assertEqual(lhs ** -1, self.neutral() / lhs)

    def test_exp(self):
        element = self.rand()

        self.assertEqual(element ** 2, element * element)

    def test_exp_BN(self):
        element = self.rand()
        exp = pyrelic.rand_BN_order()

        self.assertEqual(element ** int(exp), element ** exp)


class TestG1(GroupTests, RelicTestCase):
    group = pyrelic.G1
    generator = pyrelic.generator_G1
    neutral = pyrelic.neutral_G1
    rand = pyrelic.rand_G1


class TestG2(GroupTests, RelicTestCase):
    group = pyrelic.G2
    generator = pyrelic.generator_G2
    neutral = pyrelic.neutral_G2
    rand = pyrelic.rand_G2


class TestGT(GroupTests, RelicTestCase):
    group = pyrelic.GT
    generator = pyrelic.generator_GT
    neutral = pyrelic.neutral_GT
    rand = pyrelic.rand_GT


if __name__ == "__main__":
    unittest.main()
