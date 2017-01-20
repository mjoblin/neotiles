# =============================================================================
# Draws two tiles: the top one (using most of the matrix) displays scrolling
# text.  The bottom one displays the progress of the scrolling text.
#
# This example relies on an external text drawing library:
#    https://github.com/adafruit/micropython-adafruit-bitmap-font
#
# ... see installation instructions here:
#    http://neotiles.readthedocs.io/pages/examples.html
# =============================================================================

from __future__ import division
import random
import time

from bitmapfont.bitmapfont import BitmapFont
from neopixel import ws
from neotiles import MatrixSize, PixelColor, TileManager, Tile
from neotiles.matrixes import NTNeoPixelMatrix


# Matrix size.  cols, rows.
MATRIX_SIZE = MatrixSize(8, 8)

# For a neopixel matrix.
LED_PIN = 18
STRIP_TYPE = ws.WS2811_STRIP_GRB


class TextScrollerTile(Tile):
    """
    Scrolls a text message from right to left across its tile.  Each message
    will be displayed with a different random color.

    Expects to receive data as a dictionary with two keys: 'text' and
    'progress_tile'.  'text' contains the text to scroll, and 'progress_tile'
    contains a reference to a tile which is displaying the scroller's
    progress.  This tile sends its progress (as a value between 0 and 1) to
    the data attribute of the 'progress_tile' tile.
    """
    def __init__(self, *args, **kwargs):
        super(TextScrollerTile, self).__init__(*args, **kwargs)

        # The current scroll position (will range from 0 to the length of the
        # text + the width of the tile).
        self._pos = None

        # The width of the entire text (in pixels).
        self._text_width = None

        # The width of the text + the tile width.  This represents the total
        # number of pixels the text has to scroll through.
        self._display_width = None

        # The number of pixel columns we've scrolled through.
        self._cols_displayed = None

        # The BitmapFont object used to draw the individual characters.
        self._bitmap_font = None

        # The color to render the text with.
        self._color = None

    def _init_new_scroll(self):
        """
        Initialize the tile's state when about to embark on scrolling a new
        text string.
        """
        # Set up the beginning state of the text scroll.
        self._bitmap_font = BitmapFont(*self.size, pixel=self._draw_text_pixel,
                                       font_name='bitmapfont/font5x8.bin')
        self._bitmap_font.init()
        self._pos = self.size.cols
        self._text_width = self._bitmap_font.width(self.data['text'])
        self._display_width = self._text_width + self.size.cols
        self._cols_displayed = 0
        self._color = PixelColor(
            random.random(), random.random(), random.random())

    def _get_current_ms(self):
        """
        Compute the current time in milliseconds.

        :return: (int) The current time in milliseconds.
        """
        return int(round(time.time() * 1000))

    def _draw_text_pixel(self, col, row):
        """
        The pixel-drawing method that we pass to the BitmapFont object.  This
        results in BitmapFont (which takes care of rendering the actual
        text characters) drawing its pixels to our tile.

        :param col: The character's pixel col.
        :param row: The character's pixel row.
        """
        if col < 0:
            return

        self.set_pixel((col, row), self._color)

    def draw(self):
        """
        Draw the tile.  This involves starting the text at the far right hand
        side of the tile and scrolling it left, one pixel at a time, until it
        scrolls off the left hand side of the tile.

        This draw method will get called for every animation frame by the
        TileManager.  As a result, we need to retain enough state between
        each invocation to know where we are in the scroll.
        """
        if self.data is None:
            return

        if self.is_accepting_data:
            # Ensure we don't get more data until we're ready.
            self.is_accepting_data = False
            self._init_new_scroll()

        # Clear the tile to prepare for the next frame of the scroll animation.
        self.clear()

        # Prepare the text string at the correct position for this frame.
        self._bitmap_font.text(self.data['text'], int(self._pos), 0)
        self._cols_displayed += 1
        self._pos -= 1

        # Notify the progress tile of our progress through the scroll.
        self.data['progress_tile'].data = (
            self._cols_displayed / self._display_width)

        if self._pos < -self._text_width:
            # We've reached the end of the scroll for this text string so we
            #  reset some things and prepare to receive the next text string.
            self.clear()
            self._bitmap_font.deinit()
            self._bitmap_font = None
            self.is_accepting_data = True
            self.data = None


class TextScrollProgressTile(Tile):
    """
    Displays a progress bar.  Expects data between 0 and 1 which represents
    the progress done, and draws its pixels from left to right based on
    progress.
    """
    def draw(self):
        if self.data is None:
            return

        self.clear()
        progress_pixels = int(round(self.size.cols * self.data))
        for row in range(self.size.rows):
            for col in range(progress_pixels):
                self.set_pixel((col, row), PixelColor(128, 0, 0))


# -----------------------------------------------------------------------------

def main():
    # Initialize our matrix, animating at 10 frames per second.
    tiles = TileManager(
        NTNeoPixelMatrix(MATRIX_SIZE, LED_PIN, strip_type=STRIP_TYPE),
        draw_fps=10
    )

    text_tile = TextScrollerTile()
    progress_tile = TextScrollProgressTile()

    # Assign the tiles to the tile manager.
    tiles.register_tile(
        text_tile,
        size=(MATRIX_SIZE.cols, MATRIX_SIZE.rows - 1), root=(0, 0)
    )

    tiles.register_tile(
        progress_tile,
        size=(MATRIX_SIZE.cols, 1), root=(0, MATRIX_SIZE.rows - 1)
    )

    # Kick off the matrix animation loop.
    tiles.draw_hardware_matrix()

    #
    lines = [
        'If you think it long and mad',
        'the wind of banners',
        'that passes through my life',
        'and you decide',
        'to leave me at the shore',
        'of the heart where I have roots',
        'remember',
        'that on that day',
        'at that hour',
        'I shall lift my arms',
        'and my roots will set off',
        'to seek another land',
    ]

    try:
        while True:
            if text_tile.is_accepting_data:
                # Send a new text string to the tile.  This will only succeed
                # when the tile is ready to receive a new string (i.e. when its
                # is_accepting_data attribute is True); so we keep trying every
                # second until we're able to send a new string.
                new_line = random.choice(lines)
                print('Scrolling line: {}'.format(new_line))

                text_tile.data = {
                    'progress_tile': progress_tile,
                    'text': new_line
                }

            time.sleep(1)
    except KeyboardInterrupt:
        tiles.draw_stop()
        tiles.clear_hardware_matrix()


# =============================================================================

if __name__ == '__main__':
    main()
