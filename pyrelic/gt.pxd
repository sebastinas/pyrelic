# cython: language_level=3, bind=true

from . cimport relic
from .bn cimport BN

cdef class GT:
    cdef relic.gt_t value

cpdef GT generator(BN exponent=*)
cpdef GT rand()
cpdef GT neutral()
