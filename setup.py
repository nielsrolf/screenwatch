import os
import sys
import setuptools


setuptools.setup(
    name="screenwatch",
    version="0.1",
    description="Take screenshots once every minute",
    author="Niels Warncke",
    url="http://github.com/nielsrolf/screenwatch",
    license="Apache 2.0",
    packages=setuptools.find_packages(),
    scripts=[],
    install_requires=[
        "click",
    ],
    extras_require={},
    entry_points={
        "console_scripts": [
            "watchme = screenwatch.cli:cli",
        ],
    },
    classifiers=[],
    tests_require=[],
    setup_requires=[],
)
