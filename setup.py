#!/usr/bin/env python

from setuptools import setup

setup(
    name="nlmk",
    version="1.0",
    description="Natural Language processing library for Macedonian (MK)",
    url="https://github.com/petrushev/nlmk",
    packages=["nlmk"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pyparsing"
    ]
)
