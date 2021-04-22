# -*- coding: utf-8 -*-
"""Python package config."""
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='veil-api-client',
    version='2.2.8',
    author='Aleksey Devyatkin, Emile Gareev',
    author_email='a.devyatkin@mashtab.org, e.gareev@mashtab.org',
    description='VeiL ECP Api client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jsc-masshtab/veil-api-client',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
    install_requires=['aiohttp==3.6.*', 'ujson==3.0.*']
)
