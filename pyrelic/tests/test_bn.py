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
from pyrelic import BN


class TestBN(unittest.TestCase):
    def test_zero(self):
        zero = pyrelic.neutral_BN()
        self.assertFalse(zero)
        self.assertEqual(int(zero), 0)
        self.assertEqual(pyrelic.BN_from_int(0), zero)

    def test_bytes(self):
        element = pyrelic.rand_BN_order()
        bytes_element = bytes(element)

        self.assertEqual(element, BN(bytes_element))

    def test_str(self):
        element = pyrelic.rand_BN_order()
        str_element = str(element)

        self.assertEqual(element, pyrelic.BN.from_str(str_element))

    def test_int(self):
        element = pyrelic.rand_BN_order()
        int_element = int(element)

        self.assertEqual(element, pyrelic.BN_from_int(int_element))
        self.assertEqual(-element, pyrelic.BN_from_int(-int_element))

    def test_repr(self):
        element = pyrelic.rand_BN_order()
        repr_element = repr(element)

        self.assertEqual(element, eval(repr_element))

    def test_add(self):
        lhs = pyrelic.rand_BN_order()
        rhs = pyrelic.rand_BN_order()

        self.assertEqual(lhs + rhs, pyrelic.BN_from_int(int(lhs) + int(rhs)))
        self.assertEqual(lhs + rhs, lhs + int(rhs))
        self.assertEqual(lhs + rhs, int(lhs) + rhs)

    def test_sub(self):
        lhs = pyrelic.rand_BN_order()
        rhs = pyrelic.rand_BN_order()

        self.assertEqual(lhs - rhs, pyrelic.BN_from_int(int(lhs) - int(rhs)))
        self.assertEqual(lhs - rhs, lhs - int(rhs))
        self.assertEqual(lhs - rhs, int(lhs) - rhs)

    def test_mul(self):
        lhs = pyrelic.rand_BN_order()
        rhs = pyrelic.rand_BN_order()

        self.assertEqual(lhs * rhs, pyrelic.BN_from_int(int(lhs) * int(rhs)))
        self.assertEqual(lhs * rhs, lhs * int(rhs))
        self.assertEqual(lhs * rhs, int(lhs) * rhs)

    def test_mod(self):
        lhs = pyrelic.rand_BN_order()
        order = pyrelic.order()

        self.assertEqual((lhs + order) % order, lhs)

    def test_mod_neg(self):
        lhs = pyrelic.rand_BN_order()
        rhs = lhs.mod_neg(pyrelic.order())

        self.assertEqual(
            lhs.mod_neg(pyrelic.order()),
            pyrelic.BN_from_int((-int(lhs)) % int(pyrelic.order())),
        )

    def test_mod_inv(self):
        lhs = pyrelic.rand_BN_order()
        rhs = lhs.mod_inv(pyrelic.order())

        self.assertEqual((lhs * rhs) % pyrelic.order(), pyrelic.BN_from_int(1))


if __name__ == "__main__":
    unittest.main()
