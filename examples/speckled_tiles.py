# =============================================================================
# Draws three speckled tiles and updates each tile's base color once per
# second.  A speckled tile is just a single block of color where each pixel's
# intensity is varied slightly to give it a somewhat speckled look.  The top
# left tile is also constantly updating its speckliness at the frame rate of
# the tile manager.
# =============================================================================

import random
import time

try:
    from neopixel import ws
    STRIP_TYPE = ws.WS2811_STRIP_GRB
except ImportError:
    STRIP_TYPE = None

from neotiles import MatrixSize, TileManager, PixelColor, Tile, TilePosition
from neotiles.matrixes import NTNeoPixelMatrix, NTRGBMatrix


# Matrix size.  cols, rows.
MATRIX_SIZE = MatrixSize(8, 8)

# For a neopixel matrix.
LED_PIN = 18

# For an RGB matrix.
CHAIN = 2


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
        NTNeoPixelMatrix(MATRIX_SIZE, LED_PIN, strip_type=STRIP_TYPE),
        draw_fps=10
    )
    #tiles = TileManager(
    #    NTRGBMatrix(rows=MATRIX_SIZE.rows, chain=CHAIN),
    #    draw_fps=10
    #)

    # Create three tiles based on our SpeckledTile class.  Tiles are told their
    # dimensions later.  We enable animation on the first tile only.
    speckled_tile_1 = SpeckledTile(animate=True)
    speckled_tile_2 = SpeckledTile(animate=False)
    speckled_tile_3 = SpeckledTile(animate=False)

    cols = MATRIX_SIZE.cols
    rows = MATRIX_SIZE.rows

    # Assign the 3 tiles to the tile manager.
    tiles.register_tile(
        speckled_tile_1, size=(cols//2, rows//2), root=(0, 0))
    tiles.register_tile(
        speckled_tile_2, size=(cols//2, rows//2), root=(cols//2, 0))
    tiles.register_tile(
        speckled_tile_3, size=(cols, rows//2), root=(0, rows//2))

    # Kick off the matrix animation loop.
    tiles.draw_hardware_matrix()

    try:
        while True:
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
