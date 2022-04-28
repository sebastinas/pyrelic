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

import pyrelic
import math
import unittest
from pyrelic import additive
from pyrelic.additive import G1, G2


class GroupTests:
    def test_bytes(self):
        element = self.rand()
        bytes_element = bytes(element)

        self.assertEqual(element, self.group(bytes_element))

    def test_repr(self):
        element = self.rand()
        repr_element = repr(element)

        self.assertEqual(element, eval(repr_element))

    def test_neutral(self):
        element = self.neutral()
        exp = additive.rand_BN_order()

        self.assertEqual(element * exp, element)
        self.assertEqual(exp * element, element)

    def test_is_neutral(self):
        self.assertTrue(self.neutral().is_neutral())

    def test_generator(self):
        exp = additive.rand_BN_order()

        self.assertEqual(self.generator(exp), self.generator() * exp)
        self.assertEqual(self.generator(exp), exp * self.generator())

    def test_mul(self):
        exp1 = 5
        exp2 = 1024
        lhs = self.generator(additive.BN_from_int(exp1))
        rhs = self.generator(additive.BN_from_int(exp2))

        self.assertEqual(lhs + rhs, self.generator(additive.BN_from_int(exp1 + exp2)))

    def test_div(self):
        lhs = self.rand()
        self.assertEqual(lhs - lhs, self.neutral())

    def test_div_exp(self):
        lhs = self.rand()
        self.assertEqual(lhs * -1, self.neutral() - lhs)

    def test_exp(self):
        element = self.rand()

        self.assertEqual(element * 2, element + element)

    def test_exp_BN(self):
        element = self.rand()
        exp = additive.rand_BN_order()

        self.assertEqual(element * int(exp), element * exp)
        self.assertEqual(element * int(exp), exp * element)

    def test_exp_negative(self):
        element = self.rand()
        exp = additive.rand_BN_order()

        self.assertEqual(element * -int(exp), element * -exp)
        self.assertEqual(element * -exp, self.neutral() - element * exp)
        self.assertEqual(element * -exp, (self.neutral() - element) * exp)

    def test_exp_0(self):
        element = self.rand()

        self.assertEqual(element * 0, self.neutral())
        self.assertEqual(element * additive.neutral_BN(), self.neutral())

    def test_exp_1(self):
        element = self.rand()

        self.assertEqual(element * 1, element)


class TestG1(GroupTests, unittest.TestCase):
    def group(self, *args):
        return G1(*args)

    def generator(self, *args):
        return additive.generator_G1(*args)

    def neutral(self):
        return additive.neutral_G1()

    def rand(self):
        return additive.rand_G1()


class TestG2(GroupTests, unittest.TestCase):
    def group(self, *args):
        return G2(*args)

    def generator(self, *args):
        return additive.generator_G2(*args)

    def neutral(self):
        return additive.neutral_G2()

    def rand(self):
        return additive.rand_G2()


class TestPair(unittest.TestCase):
    def test_pair_generators(self):
        gt = additive.pair(additive.generator_G1(), additive.generator_G2())
        self.assertEqual(gt, additive.generator_GT())

    def test_pair_neutral(self):
        gt = additive.pair(additive.neutral_G1(), additive.generator_G2())
        self.assertEqual(gt, additive.neutral_GT())

        gt = additive.pair(additive.generator_G1(), additive.neutral_G2())
        self.assertEqual(gt, additive.neutral_GT())

    def test_pair_bilinear(self):
        x = additive.rand_BN_order()
        g1 = additive.rand_G1()
        g2 = additive.rand_G2()
        gt_base = additive.pair(g1, g2)

        self.assertEqual(additive.pair(g1 * x, g2), gt_base**x)
        self.assertEqual(additive.pair(g1, g2 * x), gt_base**x)


class TestPairingProduct(unittest.TestCase):
    def test_pair_product_0(self):
        self.assertEqual(additive.pair_product(), additive.neutral_GT())

    def test_pair_product_1(self):
        g1 = additive.rand_G1()
        g2 = additive.rand_G2()

        self.assertEqual(additive.pair_product((g1, g2)), additive.pair(g1, g2))

    def test_pair_product_l(self):
        l = 5
        elements = [(additive.rand_G1(), additive.rand_G2()) for _ in range(l)]

        self.assertEqual(
            additive.pair_product(*elements),
            math.prod(
                (additive.pair(g1, g2) for g1, g2 in elements),
                start=additive.neutral_GT(),
            ),
        )
