#!/usr/bin/python3

import collections
from setuptools import setup, Extension


have_pkgconfig = True
try:
    import pkgconfig

    def pkgconfig_exists(package):
        try:
            return pkgconfig.exists(package)
        except OSError:
            return False


except ImportError:
    have_pkgconfig = False


if have_pkgconfig and pkgconfig_exists("relic"):
    flags = pkgconfig.parse("relic")
else:
    flags = collections.defaultdict(list)
    flags["libraries"] = ["relic"]


ext_modules = [
    Extension(
        "pyrelic._relic",
        ["pyrelic/_relic.pyx"],
        define_macros=flags["define_macros"],
        include_dirs=flags["include_dirs"],
        library_dirs=flags["library_dirs"],
        libraries=flags["libraries"],
    )
]

setup(
    ext_modules=ext_modules,
    packages=["pyrelic"],
    package_data={
        "pyrelic": ["_relic.pyi", "py.typed"],
    },
)
