# Copyright 2022 Sebastian Ramacher <sebastian.ramacher@ait.ac.at>
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

"""Implementation of core/helper anonymous credentials

Based on L. Hanzlik, D. Slamanig: With a Little Help from My Friends:
Constructing Practical Anonymous Credentials. CCS 2021.

Parts of the implemenation are based on work done by Adela-Iulia Georgescu
during her internship at AIT.

This example requires Python >= 3.7.
"""

from .chac import (
    setup,
    issuer_kgen,
    issue,
    core_obtain,
    core_show,
    core_kgen,
    helper_obtain,
    helper_show,
    verify,
    aidgen,
    Attribute,
    IssuerPrivateKey,
    IssuerPublicKey,
    CoreSecretKey,
)
