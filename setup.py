#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='kumo',
    version='0.2',
    packages=['kumo'],
    url='https://github.com/johnnykv/kumo',
    license='',
    author='jkv',
    author_email='jkv@unixcluster.dk',
    description='Middleware that submits logs to cloud services like loggly and loggr.',
    install_requires=[
        'requests',
        'webob'
    ]
)
