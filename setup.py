#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for spyderplugins.p_autopep8
"""
from setuptools import setup, find_packages


def readme():
    return str(open('README.md').read())


setup(
    name='spyderplugins.vim',
    version="0.1.0",
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    keywords=["spyder ide plugin addon vi vim"],
    url='https://github.com/Nodd/spyderplugins.vim',
    license='MIT',
    author='Joseph Martinot-Lagarde',
    author_email='contrebasse@gmail.com',
    description='A plugin to enable vim keybingins to the spyder editor',
    long_description=readme(),
    install_requires=['spyder>=2.3'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Widget Sets'])
