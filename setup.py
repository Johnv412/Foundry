#!/usr/bin/env python3
"""
Foundry OS Setup Script
Installs the foundry command globally
"""

from setuptools import setup, find_packages

setup(
    name='foundry-os',
    version='1.0.0',
    description='The AI Empire Command Center',
    author='John V.',
    py_modules=['foundry'],
    install_requires=[
        'click>=8.0',
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'foundry=foundry:cli',
        ],
    },
    python_requires='>=3.8',
)