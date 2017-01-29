import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--hardware-neopixel',
        action='store_true',
        default=False,
        help='use neopixel matrix for hardware tests'
    )

    parser.addoption(
        '--hardware-rgb',
        action='store_true',
        default=False,
        help='use RGB matrix for hardware tests'
    )

    parser.addoption(
        '--hardware-led-pin',
        action='store',
        type='int',
        metavar='pin',
        help='LED pin for neopixel hardware tests'
    )

    parser.addoption(
        '--hardware-cols',
        action='store',
        type='int',
        metavar='cols',
        help='column count for neopixel hardware tests'
    )

    parser.addoption(
        '--hardware-rows',
        action='store',
        type='int',
        metavar='rows',
        help='row count for neopixel or RGB hardware test'
    )

    parser.addoption(
        '--hardware-chain-length',
        action='store',
        type='int',
        metavar='chain_length',
        help='chain length for RGB hardware test'
    )

    parser.addoption(
        '--hardware-parallel',
        action='store',
        type='int',
        metavar='parallel',
        help='parallel count for RGB hardware test'
    )
