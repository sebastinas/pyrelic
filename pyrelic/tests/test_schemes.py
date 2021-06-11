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

has_examples = True
try:
    from examples import bfibe, bls, hpra, spseq
except ImportError:
    has_examples = False


class DHKE:
    def test_dual_dhke(self):
        # use case: https://engineering.fb.com/2020/07/10/open-source/private-matching/
        s1 = pyrelic.rand_BN_order()
        s2 = pyrelic.rand_BN_order()

        for i in (b"some id", b"your name"):
            p = self.hash_to_curve(i)
            p1 = p ** s1
            p2 = p1 ** s2

            p1_ = p ** s2
            p2_ = p1_ ** s1

            self.assertEqual(p2, p2_)


class TestDHKEG1(DHKE, unittest.TestCase):
    def hash_to_curve(self, msg):
        return pyrelic.hash_to_G1(msg)


class TestDHKEG2(DHKE, unittest.TestCase):
    def hash_to_curve(self, msg):
        return pyrelic.hash_to_G2(msg)


@unittest.skipUnless(has_examples, "examples are not available")
class TestSchemes:
    def test_bfibe(self):
        bfibe.test_bf_ibe()

    def test_bls(self):
        bls.test_bls()

    def test_hpra(self):
        hpra.test_hpra()

    def test_spseq(self):
        for l in range(3, 10):
            spseq.test_spseq(l)
