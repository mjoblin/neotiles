#!/usr/bin/env python

from setuptools import setup, find_packages


packages = [package for package in find_packages()
            if package.startswith('neotiles')]

version = '0.1.0'

install_requires = [
    'wrapt',
]

setup_requires = [
    'pytest-runner'
]

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-sugar'
]

extras_require = {
    'dev': [
        'sphinx',
        'flake8',
    ] + tests_require,
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
    setup_requires=setup_requires,
    tests_require=tests_require,
    license='MIT',
    classifiers=[
    ]
)

