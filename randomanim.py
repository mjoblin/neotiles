import random
import time

from neotiles import TileManager, NPColor, TileHandler, TilePosition


class RandomAnimTile(TileHandler):
    def __init__(self):
        super().__init__(default_color=NPColor(0, 0, 0))
        self.clear()

    def data(self, in_data):
        super().data(in_data)

        for row in range(self.size.rows):
            for col in range(self.size.cols):
                # Set each pixel to the tile's color multiplied by an intensity
                # value between 0.4 and 1.0.
                intensity = random.uniform(0.4, 1.0)
                display_color = NPColor(
                    in_data.red * intensity,
                    in_data.green * intensity,
                    in_data.blue * intensity
                )
                self.set_pixel(
                    TilePosition(col, row), display_color)


# Initialize an 8x8 matrix.
tiles = TileManager(size=(8, 8))

# Create three tile handlers.  Handlers are told their dimensions
# later.
random_tile_1 = RandomAnimTile()
random_tile_2 = RandomAnimTile()
random_tile_3 = RandomAnimTile()

# Assign the 3 tile handlers to the matrix.  This is when the
# tiles will be given their dimensions.
tiles.register_tile(size=(4, 4), root=(0, 0), handler=random_tile_1)
tiles.register_tile(size=(4, 4), root=(4, 0), handler=random_tile_2)
tiles.register_tile(size=(8, 4), root=(0, 4), handler=random_tile_3)

# Kick off the matrix animation.
tiles.animate()

while True:
    # Update each tile's color each second.
    for tile in [random_tile_1, random_tile_2, random_tile_3]:
        tile.data(NPColor(
            random.random(), random.random(), random.random()))
    time.sleep(1)
