import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--hardware-led-pin',
        action='store',
        type='int',
        help='LED pin for neopixel hardware tests'
    )

    parser.addoption(
        '--hardware-cols',
        action='store',
        type='int',
        help='column count for neopixel hardware tests'
    )

    parser.addoption(
        '--hardware-rows',
        action='store',
        type='int',
        help='row count for neopixel hardware test'
    )
