import time

import pytest

from neotiles import PixelColor, Tile, TileManager


HARDWARE_LED_PIN = pytest.config.getoption('--hardware-led-pin')
HARDWARE_COLS = pytest.config.getoption('--hardware-cols')
HARDWARE_ROWS = pytest.config.getoption('--hardware-rows')


hardware = pytest.mark.skipif(
    pytest.config.getoption('--hardware-led-pin') is None or
    pytest.config.getoption('--hardware-cols') is None or
    pytest.config.getoption('--hardware-rows') is None,
    reason='need --hardware-led-pin, --hardware-cols, and --hardware-rols '
           'options to run'
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
        tm = TileManager(
            (HARDWARE_COLS, HARDWARE_ROWS), led_pin=HARDWARE_LED_PIN)

        red_color = PixelColor(128, 0, 0)
        tile = Tile(default_color=red_color)
        tm.register_tile(tile, size=(8, 8), root=(0, 0))

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
        tm = TileManager(
            (HARDWARE_COLS, HARDWARE_ROWS),
            led_pin=HARDWARE_LED_PIN,
            draw_fps=None
        )

        red_color = PixelColor(128, 0, 0)
        tile = Tile(default_color=red_color)
        tm.register_tile(tile, size=(8, 8), root=(0, 0))

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
