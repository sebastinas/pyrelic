#!/usr/bin/python3

import pkgconfig
from setuptools import setup, Extension

flags = pkgconfig.parse("relic")

ext_modules = [
    Extension(
        "pyrelic.bn",
        ["pyrelic/bn.pyx"],
        define_macros=flags["define_macros"],
        include_dirs=flags["include_dirs"],
        library_dirs=flags["library_dirs"],
        libraries=flags["libraries"],
    ),
    Extension(
        "pyrelic.core",
        ["pyrelic/core.pyx"],
        define_macros=flags["define_macros"],
        include_dirs=flags["include_dirs"],
        library_dirs=flags["library_dirs"],
        libraries=flags["libraries"],
    ),
    Extension(
        "pyrelic.g1",
        ["pyrelic/g1.pyx"],
        define_macros=flags["define_macros"],
        include_dirs=flags["include_dirs"],
        library_dirs=flags["library_dirs"],
        libraries=flags["libraries"],
    ),
    Extension(
        "pyrelic.g2",
        ["pyrelic/g2.pyx"],
        define_macros=flags["define_macros"],
        include_dirs=flags["include_dirs"],
        library_dirs=flags["library_dirs"],
        libraries=flags["libraries"],
    ),
    Extension(
        "pyrelic.gt",
        ["pyrelic/gt.pyx"],
        define_macros=flags["define_macros"],
        include_dirs=flags["include_dirs"],
        library_dirs=flags["library_dirs"],
        libraries=flags["libraries"],
    ),
    Extension(
        "pyrelic.pair",
        ["pyrelic/pair.pyx"],
        define_macros=flags["define_macros"],
        include_dirs=flags["include_dirs"],
        library_dirs=flags["library_dirs"],
        libraries=flags["libraries"],
    ),
]

setup(
    ext_modules=ext_modules,
    packages=["pyrelic"],
)
