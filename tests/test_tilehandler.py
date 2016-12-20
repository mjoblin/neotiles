import pytest

from neotiles import PixelColor, PixelPosition, TileHandler, TileSize

from .fixtures import default_handler


class TestTileHandler:
    def init_pixels(self, handler, color):
        """
        Set all pixels in a tile handler to ``color``.

        :param handler: (TileHandler) The handler whose pixels are to be
            inititialized.
        :param color: (PixelColor) Color to set each pixel to.
        """
        handler._init_pixels(color)

        for row in range(handler.size.rows):
            for col in range(handler.size.cols):
                assert handler.pixels[row][col] == color

    def test_instantiate(self, default_handler):
        """
        Test that the default size is 1x1.
        """
        assert default_handler.size == (1, 1)
        assert len(default_handler.pixels) == 1
        assert len(default_handler.pixels[0]) == 1

    def test_default_color(self):
        """
        Test that we can set the default color.
        """
        color = PixelColor(0, 0.5, 1)
        handler = TileHandler(default_color=color)
        assert handler.default_color is color
        assert handler.pixels[0][0] is color

        pixel = handler.pixels[0][0]
        assert pixel.red == 0
        assert pixel.green == 0.5
        assert pixel.blue == 1
        assert pixel.white is None

    def test_size(self, default_handler):
        """
        Test setting the size of the tile.
        """
        assert isinstance(default_handler.size, TileSize) is True

        default_handler.size = (10, 5)
        assert isinstance(default_handler.size, TileSize) is True
        assert default_handler.size.cols == 10
        assert default_handler.size.rows == 5

        default_handler.size = TileSize(8, 4)
        assert isinstance(default_handler.size, TileSize) is True
        assert default_handler.size.cols == 8
        assert default_handler.size.rows == 4

    def test_set_pixel(self, default_handler):
        """
        Test setting a individual pixel colors.
        """
        default_handler.size = (10, 5)
        main_color = PixelColor(100, 200, 50)
        special_color = PixelColor(99, 99, 99)
        self.init_pixels(default_handler, main_color)

        default_handler.set_pixel((1, 1), special_color)
        default_handler.set_pixel(PixelPosition(2, 2), special_color)

        for row in range(default_handler.size.rows):
            for col in range(default_handler.size.cols):
                pixel_color = default_handler.pixels[row][col]
                if (col, row) in [(1, 1), (2, 2)]:
                    assert pixel_color == special_color
                else:
                    assert pixel_color == main_color

    def test_clear(self, default_handler):
        """
        Test clearing a tile (setting all pixels to (0, 0, 0).
        """
        default_handler.size = (10, 5)
        color = PixelColor(100, 200, 50)
        self.init_pixels(default_handler, color)
        default_handler.clear()

        for row in range(default_handler.size.rows):
            for col in range(default_handler.size.cols):
                pixel_color = default_handler.pixels[row][col]
                assert pixel_color.red == 0
                assert pixel_color.green == 0
                assert pixel_color.blue == 0
                assert pixel_color.white == 0

    def test_init_pixels(self, default_handler):
        """
        Test initializing all pixels to the same color.
        """
        default_handler.size = (10, 5)
        color = PixelColor(100, 200, 50)
        self.init_pixels(default_handler, color)

    def test_data(self, default_handler):
        """
        Test sending different types of data to the hander.
        """
        for some_data in [99, 'something', [1, 2, 3], {'a': 1, 'b': 2}]:
            default_handler.data(some_data)
            assert default_handler._data is some_data

    def test_repr(self):
        """
        Test the repr output.
        """
        handler = TileHandler(default_color=PixelColor(100, 200, 50, 10))
        assert repr(handler) == (
            'TileHandler(default_color=PixelColor(red=100, green=200, blue=50, '
            'white=10, normalized=False))'
        )
