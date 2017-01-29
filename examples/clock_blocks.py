# =============================================================================
# Displays the current time as 4 vertical tiles representing the day of the
# week, the hour, the minute, and the second.  The intensity of each tile
# depends on how far through the week/day/hour/minute we are at the current
# time.  This means that the seconds tile will go from dark to bright once per
# minute; the minute tile will go from dark to bright once per hour; etc.
#
# The changes are all pretty subtle (except perhaps for the seconds tile).
# =============================================================================

from __future__ import division
import datetime
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


class TimeTile(Tile):
    """
    Defines a tile which receives a PixelColor and time component as input
    data, and sets all its pixels to that color multiplied by an intensity
    determined by how far through the time_component we are.

    :param color: (PixelColor) The color of the tile.
    :param time_component: (string) The time component to look for in the
        data.  One of 'day', 'hour', 'minute', or 'second'.
    """
    def __init__(self, color, time_component):
        super(TimeTile, self).__init__()
        self._color = color
        self._time_component = time_component

        if time_component == 'day':
            self._display_multiplier = 1 / 7
        elif time_component == 'hour':
            self._display_multiplier = 1 / 24
        elif time_component == 'minute':
            self._display_multiplier = 1 / 60
        elif time_component == 'second':
            self._display_multiplier = 1 / 60

    def draw(self):
        if self.data is None:
            return

        # Find the current time_component value from the input data and
        # compute the current intensity based on how far through the time
        # component we are.
        display_value = self.data[self._time_component] + 1
        display_intensity = display_value * self._display_multiplier

        for row in range(self.size.rows):
            for col in range(self.size.cols):
                # Set each pixel to the tile's color multiplied by its
                # intensity.
                display_color = PixelColor(
                    self._color.red * display_intensity,
                    self._color.green * display_intensity,
                    self._color.blue * display_intensity,
                    self._color.white * display_intensity
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
    #tiles = TileManager(NTRGBMatrix(chain_length=CHAIN), draw_fps=10)

    # Create three tiles based on our SpeckledTile class.  Tiles are told their
    # dimensions later.  We enable animation on the first tile only.
    day_tile = TimeTile(color=PixelColor(1, 0, 0, 0), time_component='day')
    hrs_tile = TimeTile(color=PixelColor(0, 1, 0, 0), time_component='hour')
    min_tile = TimeTile(color=PixelColor(0, 0, 1, 0), time_component='minute')
    sec_tile = TimeTile(color=PixelColor(1, 1, 1, 0), time_component='second')

    cols = MATRIX_SIZE.cols
    rows = MATRIX_SIZE.rows
    width = cols // 4

    # Assign the tiles to the tile manager.
    tiles.register_tile(day_tile, size=(width, rows), root=(0, 0))
    tiles.register_tile(hrs_tile, size=(width, rows), root=(int(cols*0.25), 0))
    tiles.register_tile(min_tile, size=(width, rows), root=(int(cols*0.5), 0))
    tiles.register_tile(sec_tile, size=(width, rows), root=(int(cols*0.75), 0))

    # Kick off the matrix animation loop.
    tiles.draw_hardware_matrix()

    try:
        while True:
            now = datetime.datetime.now()

            data = {
                'day': now.weekday(),
                'hour': now.hour,
                'minute': now.minute,
                'second': now.second,
            }

            tiles.send_data_to_tiles(data)
            time.sleep(0.5)
    except KeyboardInterrupt:
        tiles.draw_stop()
        tiles.clear_hardware_matrix()


# =============================================================================

if __name__ == '__main__':
    main()
