# =============================================================================
# Draws three speckled tiles and updates each tile's base color once per
# second.  A speckled tile is just a single block of color where each pixel's
# intensity is varied slightly to give it a somewhat speckled look.  The top
# left tile is also constantly updating its speckliness at the frame rate of
# the tile manager.
# =============================================================================

import random
import time

from neopixel import ws
from neotiles import (
    MatrixSize, TileManager, PixelColor, Tile, TilePosition)


# Set these defaults to match your specific hardware.
MATRIX_SIZE = MatrixSize(8, 8)
LED_PIN = 18
STRIP_TYPE = ws.WS2811_STRIP_GRB


class SpeckledTile(Tile):
    """
    Defines a tile which receives a PixelColor as input data, and sets all its
    pixels to that color multiplied by an intensity picked randomly between
    0.4 and 1.0.  This should produce a speckled look to the tile.
    """
    def draw(self):
        if not isinstance(self.data, PixelColor):
            return

        for row in range(self.size.rows):
            for col in range(self.size.cols):
                # Set each pixel to the tile's color multiplied by an intensity
                # value between 0.4 and 1.0.
                intensity = random.uniform(0.4, 1.0)
                display_color = PixelColor(
                    self.data.red * intensity,
                    self.data.green * intensity,
                    self.data.blue * intensity
                )
                self.set_pixel(
                    TilePosition(col, row), display_color)


# -----------------------------------------------------------------------------

def main():
    # Initialize our matrix, animating at 10 frames per second.
    tiles = TileManager(
        MATRIX_SIZE, LED_PIN, draw_fps=10, strip_type=STRIP_TYPE)

    # Create three tiles based on our SpeckledTile class.  Tiles are told their
    # dimensions later.  We enable animation on the first tile only.
    speckled_tile_1 = SpeckledTile(animate=True)
    speckled_tile_2 = SpeckledTile(animate=False)
    speckled_tile_3 = SpeckledTile(animate=False)

    # Assign the 3 tiles to the tile manager.  This is when the tiles will be
    # given their dimensions.

    # NOTE: This assumes an 8x8 matrix.  Tweak these values for a different-
    # sized matrix.
    tiles.register_tile(speckled_tile_1, size=(4, 4), root=(0, 0))
    tiles.register_tile(speckled_tile_2, size=(4, 4), root=(4, 0))
    tiles.register_tile(speckled_tile_3, size=(8, 4), root=(0, 4))

    # Kick off the matrix animation loop.
    tiles.draw_hardware_matrix()

    try:
        while True:
            # Change the tile manager brightness each time through the loop.
            # This will affect all tiles being displayed on the matrix.
            tiles.brightness = random.choice([2, 4, 8, 16, 32, 64, 128])

            # Update each tile's base color.  Each tile is getting different
            # data (a different random color) so we call the Tile.data()
            # methods independently rather than calling the tile manager's
            # send_data_to_tiles() method.
            for tile in [speckled_tile_1, speckled_tile_2, speckled_tile_3]:
                tile.data = PixelColor(
                    random.random(), random.random(), random.random())

                # We also draw each tile manually.  This is only needed for
                # the 'animate=False' tiles but we do it for all of them.
                tile.draw()

            # We only want the base color to update once per second.  The
            # first tile will randomly animate its pixel intensities during
            # this one-second interval (see "animate=True" on the tile).
            time.sleep(1)
    except KeyboardInterrupt:
        tiles.draw_stop()
        tiles.clear_hardware_matrix()


# =============================================================================

if __name__ == '__main__':
    main()
