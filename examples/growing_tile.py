# =============================================================================
# Draws a single red tile, 1x1, at the top left of the matrix and then grows
# it out in both dimensions until it fills the full width of the matrix.  When
# it gets to the full width it shrinks the tile back again.  Repeat.
# =============================================================================

import time

from neopixel import ws
from neotiles import MatrixSize, TileManager, PixelColor, Tile, TileSize


# Set these defaults to match your specific hardware.
MATRIX_SIZE = MatrixSize(8, 8)
LED_PIN = 18
STRIP_TYPE = ws.WS2811_STRIP_GRB


# -----------------------------------------------------------------------------

def main():
    # Initialize our matrix, animating at 10 frames per second.
    tiles = TileManager(
        MATRIX_SIZE, LED_PIN, draw_fps=10, strip_type=STRIP_TYPE)

    # Use the default Tile class, setting its color to red.  We don't need to
    # override the draw method for this example as the default block drawing
    # implementation is enough.
    growing_tile = Tile(default_color=PixelColor(1, 0, 0))

    # Assign the tile to the tile manager.
    tiles.register_tile(growing_tile, size=(1, 1), root=(0, 0))

    # Kick off the matrix animation loop.
    tiles.draw_hardware_matrix()

    # Keep track of whether we're getting bigger or smaller.
    getting_bigger = True

    try:
        while True:
            # Get the current size of the tile.
            size = growing_tile.size

            # Switch between growing bigger and smaller when we reach the
            # boundaries of the matrix.
            if getting_bigger and size.cols >= MATRIX_SIZE.cols:
                getting_bigger = False
            elif not getting_bigger and size.cols <= 1:
                getting_bigger = True

            # Change the tile size.
            size_change = 1 if getting_bigger else -1
            growing_tile.size = TileSize(
                size.cols + size_change, size.rows + size_change)

            time.sleep(0.5)
    except KeyboardInterrupt:
        tiles.draw_stop()
        tiles.clear_hardware_matrix()


# =============================================================================

if __name__ == '__main__':
    main()
