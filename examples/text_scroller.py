import random
import time

from bitmapfont.bitmapfont import BitmapFont
from neotiles import PixelColor, TileManager, Tile, TileSize


# Set these defaults to match your specific hardware.  You may also need to
# set the TileManager's strip_type parameter.
TILE_SIZE = TileSize(8, 8)
LED_PIN = 18


class TextScrollerTile(Tile):
    """
    """
    def __init__(self, *args, **kwargs):
        super(TextScrollerTile, self).__init__(*args, **kwargs)
        self._pos = None
        self._text_width = None
        self._display_width = None
        self._cols_displayed = None
        self._bitmap_font = None
        self._color = None

    def _get_current_ms(self):
        return int(round(time.time() * 1000))

    def _draw_text_pixel(self, col, row):
        if col < 0:
            return

        self.set_pixel((col, row), self._color)

    def draw(self):
        if self.data is None:
            return

        if self.is_accepting_data:
            # TODO: Make a settable property?
            self._is_accepting_data = False
            self._bitmap_font = BitmapFont(*self.size, self._draw_text_pixel,
                                           font_name='bitmapfont/font5x8.bin')
            self._bitmap_font.init()
            self._pos = self.size.cols
            self._text_width = self._bitmap_font.width(self.data['text'])
            self._display_width = self._text_width + self.size.cols
            self._cols_displayed = 0
            self._color = PixelColor(
                random.random(), random.random(), random.random())

        self.clear()
        self._bitmap_font.text(self.data['text'], int(self._pos), 0)
        self._cols_displayed += 1
        self._pos -= 1

        self.data['progress_tile'].data = (
            self._cols_displayed / self._display_width)

        if self._pos < -self._text_width:
            self.clear()
            self._bitmap_font.deinit()
            self._bitmap_font = None
            self.data = None
            self._is_accepting_data = True


class TextScrollProgressTile(Tile):
    def draw(self):
        if self.data is None:
            return

        self.clear()
        progress_pixels = round(self.size.cols * self.data)
        for row in range(self.size.rows):
            for col in range(progress_pixels):
                self.set_pixel((col, row), PixelColor(128, 0, 0))


# -----------------------------------------------------------------------------

def main():
    # Initialize an 8x8 matrix, animating at 10 frames per second.
    tiles = TileManager(TILE_SIZE, LED_PIN, draw_fps=10)

    text_tile = TextScrollerTile(animate=True)
    progress_tile = TextScrollProgressTile(animate=True)

    tiles.register_tile(size=(8, 7), root=(0, 0), tile=text_tile)
    tiles.register_tile(size=(8, 1), root=(0, 7), tile=progress_tile)

    # Kick off the matrix animation loop.
    tiles.draw_hardware_matrix()

    try:
        while True:
            if text_tile.is_accepting_data:
                text_tile.data = {
                    'progress_tile': progress_tile,
                    'text': random.choice([
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
                     ])
                }

            time.sleep(0.25)
    except KeyboardInterrupt:
        tiles.draw_stop()
        tiles.clear()


# =============================================================================

if __name__ == '__main__':
    main()
