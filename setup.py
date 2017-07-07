#!/usr/bin/env python

from distutils.core import setup

setup(
    name='colorMap',
    version='1.0.0',
    packages=['colorMap'],
    include_package_data=True,
    install_requires=[
        'flask',
        'colour',
    ],    
    description='Create color maps using CSVs',
    author='Jack Lindgren + Andrew Montes',
    long_description=open('README.md').read(),
)