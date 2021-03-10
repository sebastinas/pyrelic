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


class TestBN(RelicTestCase):
    def test_zero(self):
        zero = pyrelic.neutral_BN()
        self.assertFalse(zero)
        self.assertEqual(int(zero), 0)

    def test_bytes(self):
        element = pyrelic.rand_BN_order()
        bytes_element = bytes(element)

        self.assertEqual(element, pyrelic.BN(bytes_element))

    def test_str(self):
        element = pyrelic.rand_BN_order()
        str_element = str(element)

        self.assertEqual(element, pyrelic.BN.from_str(str_element))


if __name__ == "__main__":
    unittest.main()