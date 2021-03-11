#!/usr/bin/python3

import pkgconfig
from setuptools import setup, Extension

flags = pkgconfig.parse("relic")

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
