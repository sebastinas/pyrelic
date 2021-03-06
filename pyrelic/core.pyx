# cython: language_level=3

from . cimport relic

cdef class Relic:
    cdef int code_core
    cdef int code_pairing

    def __init__(self):
        self.code_core = relic.RLC_ERR
        self.code_pairing = relic.RLC_ERR

    def __enter__(self):
        self.code_core = relic.core_init()
        if self.code_core != relic.RLC_OK:
            raise RuntimeError("Failed to initialize relic!")
        self.code_pairing = relic.pc_param_set_any()
        if self.code_pairing != relic.RLC_OK:
            raise RuntimeError("Failed to initialize relic (pairing)!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.code_core == relic.RLC_OK:
            relic.core_clean()
