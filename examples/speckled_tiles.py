import random
import time

from neotiles import (
    TileManager, PixelColor, TileHandler, TilePosition, TileSize)


# Set these defaults to match your specific hardware.  You may also need to
# set the TileManager's strip_type parameter.
TILE_SIZE = TileSize(8, 8)
LED_PIN = 18


class SpeckledTile(TileHandler):
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
    # Initialize an 8x8 matrix, animating at 10 frames per second.
    tiles = TileManager(TILE_SIZE, LED_PIN, draw_fps=10)

    # Create three tile handlers based on our SpeckledTile class.  Handlers are
    # told their dimensions later.  We enable animation on the first tile only.
    speckled_tile_1 = SpeckledTile(animate=True)
    speckled_tile_2 = SpeckledTile(animate=False)
    speckled_tile_3 = SpeckledTile(animate=False)

    # Assign the 3 tile handlers to the tile manager.  This is when the
    # tiles will be given their dimensions.
    tiles.register_tile(size=(4, 4), root=(0, 0), handler=speckled_tile_1)
    tiles.register_tile(size=(4, 4), root=(4, 0), handler=speckled_tile_2)
    tiles.register_tile(size=(8, 4), root=(0, 4), handler=speckled_tile_3)

    # Kick off the matrix animation loop.
    tiles.draw_matrix()

    try:
        while True:
            # Change the tile manager brightness each time through the loop.
            # This will affect all tiles being displayed on the matrix.
            tiles.brightness = random.choice([2, 4, 8, 16, 32, 64, 128])

            # Update each tile's base color.
            for tile in [speckled_tile_1, speckled_tile_2, speckled_tile_3]:
                tile.data = PixelColor(
                    random.random(), random.random(), random.random())
                tile.draw()

            # We only want the base color to update once per second.  The
            # first tile will randomly animate its pixel intensities during
            # this one-second interval (see "animate=True" on the handler).
            time.sleep(1)
    except KeyboardInterrupt:
        tiles.draw_stop()
        tiles.clear()


# =============================================================================

if __name__ == '__main__':
    main()