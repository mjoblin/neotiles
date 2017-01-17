# =============================================================================
# Create a fire effect.  Multiple fires can be displayed at once.
#
# Most of this code is taken from this gist:
#    https://gist.github.com/tdicola/63768def5b2e4e3a942b085cd2264d7b
#
# ... which is described in this video:
#    https://www.youtube.com/watch?v=OJlYxnBLBbk
#
# All this example does is take the above code and make it work with neotiles
# (as well as adding a feature or two, like being able to define the fire
# base).
# =============================================================================

from __future__ import division
import random
import time

from neopixel import ws
from neotiles import MatrixSize, TileManager, PixelColor, Tile
from neotiles.matrixes import NTNeoPixelMatrix, NTRGBMatrix


# Set these defaults to match your specific hardware.
MATRIX_SIZE = MatrixSize(8, 8)

# For NeoPixel matrix.
LED_PIN = 18
STRIP_TYPE = ws.WS2811_STRIP_GRB

# For RGB matrix.
CHAIN = 2


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def hue2rgb(p, q, t):
    # Helper for the hsl2rgb function.
    # From: http://axonflux.com/handy-rgb-to-hsl-and-rgb-to-hsv-color-model-c
    if t < 0:
        t += 1
    if t > 1:
        t -= 1
    if t < 1/6:
        return p + (q - p) * 6 * t
    if t < 1/2:
        return q
    if t < 2/3:
        return p + (q - p) * (2/3 - t) * 6

    return p


def hsl2rgb(h, s, l):
    # Convert a hue, saturation, lightness color into red, green, blue color.
    # Expects incoming values in range 0...255 and outputs values in the same
    # range.
    # From: http://axonflux.com/handy-rgb-to-hsl-and-rgb-to-hsv-color-model-c
    h /= 255.0
    s /= 255.0
    l /= 255.0
    r = 0
    g = 0
    b = 0

    if s == 0:
        r = l
        g = l
        b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1/3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1/3)

    return int(r*255.0), int(g*255.0), int(b*255.0), 0


# -----------------------------------------------------------------------------

class FireMatrix(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [0]*(width*height)

    def get(self, x, y):
        x %= self.width   # Wrap around when x values go outside the bounds!
        y %= self.height  # Like-wise wrap around y values!
        return self.data[y * self.width + x]

    def set(self, x, y, value):
        x %= self.width
        y %= self.height
        self.data[y * self.width + x] = value


class FireTile(Tile):
    """
    Defines a tile which displays a fire effect.

    :param size_divisor: (float) Affects the height of the fire.
    :param hue_offset: (int) Affects the color palette of the fire.
    :param base: ('bottom'|'top') Base of the fire.
    """
    def __init__(self, size_divisor=10.0, hue_offset=0, base='bottom'):
        super(FireTile, self).__init__()

        self.size_divisor = size_divisor
        self.hue_offset = hue_offset
        self.base = base

        self.fire = None
        self.palette = []
        self.frame = 0

        for x in range(256):
            self.palette.append(
                PixelColor(
                    *hsl2rgb(self.hue_offset + (x // 3), 255, min(255, x * 2)),
                    normalized=False))

    def on_size_set(self):
        # When the size of the tile is set by the TileManager, we want to
        # initialize our FireMatrix.
        self.fire = FireMatrix(self.size.cols, self.size.rows + 1)

    def draw(self):
        # Set the base concealed row to random intensity values (0 to 255).
        # The concealed row is there to reduce the base intensity, resulting in
        # a more pleasing result (see the video linked to above).
        concealed_row = self.size.rows if self.base == 'bottom' else -1
        for x in range(self.size.cols):
            self.fire.set(x, concealed_row, int(random.random() * 255))

        if self.base == 'bottom':
            row_list = list(range(self.size.rows))
            row_index_direction = 1
        else:
            row_list = list(reversed(range(self.size.rows)))
            row_index_direction = -1

        # Perform a step of flame intensity calculation.
        for x in range(self.size.cols):
            for y in row_list:
                value = 0
                value += self.fire.get(x - 1, y + row_index_direction)
                value += self.fire.get(x, y + row_index_direction)
                value += self.fire.get(x + 1, y + row_index_direction)
                value += self.fire.get(x, y + (row_index_direction * 2))
                value = int(value / self.size_divisor)
                self.fire.set(x, y, value)

        # Convert the fire intensity values to neopixel colors and update the
        # pixels.
        for x in range(self.size.cols):
            for y in range(self.size.rows):
                self.set_pixel((x, y), self.palette[self.fire.get(x, y)])


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

    # Play with this number to set the fire height.
    size_divisor = 7.2

    # Create two tiles based on our FireTile class.  One will display a red
    # fire based at the bottom of the matrix and the other will display a
    # green fire based at the top of the matrix.
    red_fire = FireTile(size_divisor=size_divisor)
    grn_fire = FireTile(size_divisor=size_divisor, hue_offset=50, base='top')

    # Each fire will take half the width of the matrix, and the full height.
    fire_width = int(MATRIX_SIZE.cols // 2)
    fire_height = MATRIX_SIZE.rows

    tiles.register_tile(red_fire, size=(fire_width, fire_height), root=(0, 0))
    tiles.register_tile(grn_fire, size=(fire_width, fire_height),
                        root=(fire_width, 0))

    # Kick off the matrix animation loop.
    tiles.draw_hardware_matrix()

    # Keep animating the fires until the user Ctrl-C's the process.
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        tiles.draw_stop()
        tiles.clear_hardware_matrix()


# =============================================================================

if __name__ == '__main__':
    main()
