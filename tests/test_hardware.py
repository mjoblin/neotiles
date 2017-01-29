import time

import pytest

from neotiles import PixelColor, Tile, TileManager
from neotiles.matrixes import NTNeoPixelMatrix, NTRGBMatrix


HARDWARE_NEOPIXEL = pytest.config.getoption('--hardware-neopixel')
HARDWARE_RGB = pytest.config.getoption('--hardware-rgb')

# neopixel matrix
HARDWARE_LED_PIN = pytest.config.getoption('--hardware-led-pin')
HARDWARE_COLS = pytest.config.getoption('--hardware-cols')

# rgb matrix
HARDWARE_CHAIN_LENGTH = pytest.config.getoption('--hardware-chain-length')
HARDWARE_PARALLEL = pytest.config.getoption('--hardware-parallel')

# both neopixel and hardware matrixes
HARDWARE_ROWS = pytest.config.getoption('--hardware-rows')

hardware = pytest.mark.skipif(
    (HARDWARE_NEOPIXEL is False and HARDWARE_RGB is False)
    or
    (HARDWARE_RGB and (
        HARDWARE_ROWS is None or
        HARDWARE_CHAIN_LENGTH is None or
        HARDWARE_PARALLEL is None
    ))
    or
    (HARDWARE_NEOPIXEL and (
        HARDWARE_LED_PIN is None or
        HARDWARE_COLS is None or
        HARDWARE_ROWS is None
    )),
    reason='one or more required --hardware flags were not specified'
)


class TestHardware:
    """
    Some simple hardware tests just to poke the code.
    """
    def _check_all_pixels(self, pixels, color):
        for row in range(len(pixels)):
            for col in range(len(pixels[row])):
                assert pixels[row][col] == color

    @hardware
    def test_hardware_with_animation(self):
        """
        Performs a simple hardware test which creates a single tile with a
        single color, filling the entire matrix.  Checks the pixels look
        right and tries to draw it to the hardware with animation enabled.
        """
        if HARDWARE_NEOPIXEL:
            matrix = NTNeoPixelMatrix(
                size=(HARDWARE_COLS, HARDWARE_ROWS),
                led_pin=HARDWARE_LED_PIN
            )
        else:
            matrix = NTRGBMatrix(
                rows=HARDWARE_ROWS,
                chain_length=HARDWARE_CHAIN_LENGTH,
                parallel=HARDWARE_PARALLEL
            )

        rows = matrix.size.rows
        cols = matrix.size.cols

        tm = TileManager(matrix=matrix)

        red_color = PixelColor(128, 0, 0)
        tile = Tile(default_color=red_color)
        tm.register_tile(tile, size=(cols, rows), root=(0, 0))

        # Start the animation loop.
        tm.draw_hardware_matrix()

        self._check_all_pixels(tm.pixels, red_color)
        time.sleep(0.5)

        green_color = PixelColor(0, 128, 0)

        # Set the color of the tile to green.  The animation loop should
        # take care of drawing this to the virtual matrix.
        tile.default_color = green_color
        time.sleep(0.5)
        self._check_all_pixels(tm.pixels, green_color)

        tm.draw_stop()
        tm.clear_hardware_matrix()

    @hardware
    def test_hardware_without_animation(self):
        """
        Same test but with animation disabled.
        """
        if HARDWARE_NEOPIXEL:
            matrix = NTNeoPixelMatrix(
                size=(HARDWARE_COLS, HARDWARE_ROWS),
                led_pin=HARDWARE_LED_PIN
            )
        else:
            matrix = NTRGBMatrix(
                rows=HARDWARE_ROWS,
                chain_length=HARDWARE_CHAIN_LENGTH,
                parallel=HARDWARE_PARALLEL
            )

        rows = matrix.size.rows
        cols = matrix.size.cols

        tm = TileManager(matrix=matrix, draw_fps=None)

        red_color = PixelColor(128, 0, 0)
        tile = Tile(default_color=red_color)
        tm.register_tile(tile, size=(cols, rows), root=(0, 0))

        # Draw the tile in red.
        tm.draw_hardware_matrix()
        self._check_all_pixels(tm.pixels, red_color)
        time.sleep(0.5)

        green_color = PixelColor(0, 128, 0)
        tile.default_color = green_color

        # pixels should still be red as we're not animating.
        self._check_all_pixels(tm.pixels, red_color)

        # Draw the matrix and check that the pixels are green.
        tm.draw_hardware_matrix()
        time.sleep(0.5)
        self._check_all_pixels(tm.pixels, green_color)

        tm.clear_hardware_matrix()
