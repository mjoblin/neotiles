#!/usr/bin/env python

from setuptools import setup


packages = ['neotiles']

version = '0.0.1'

install_requires = [
]

extras_require = {
    'dev': ['pytest', 'sphinx']
}

setup(
    name='neotiles',
    version=version,
    description='Treat a neopixel matrix as a collection of separate tiles',
    author='Mike Joblin',
    author_email='mike@tastymoss.com',
    url='https://github.com/mjoblin/neotiles',
    packages=packages,
    install_requires=install_requires,
    extras_require=extras_require,
    license='MIT',
    classifiers=[
    ]
)
