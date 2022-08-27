# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2022, spyder-vim
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------
"""
spyder-vim setup.
"""
from setuptools import find_packages
from setuptools import setup

from spyder_vim import __version__


setup(
    # See: https://setuptools.readthedocs.io/en/latest/setuptools.html
    name="spyder-vim",
    version=__version__,
    author="spyder-vim",
    author_email="contrebasse@gmail.com",
    description="A plugin to enable vim keybingins to the spyder editor",
    license="MIT license",
    url="https://github.com/Joseph Martinot-Lagarde/spyder-vim",
    python_requires='>= 3.7',
    install_requires=[
        "qtpy",
        "qtawesome",
        "spyder>=5.2.2",
    ],
    packages=find_packages(),
    entry_points={
        "spyder.plugins": [
            "spyder_vim = spyder_vim.spyder.plugin:SpyderVim"
        ],
    },
    classifiers=[
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Editors :: Integrated Development Environments (IDE)",
    ],
)
