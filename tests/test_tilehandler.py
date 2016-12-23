import pytest

from neotiles import PixelColor, PixelPosition, Tile, TileSize

from .fixtures import default_tile


class TestTile:
    def init_pixels(self, tile, color):
        """
        Set all pixels in a tile to ``color``.

        :param tile: (Tile) The tile whose pixels are to be inititialized.
        :param color: (PixelColor) Color to set each pixel to.
        """
        tile._init_pixels(color)

        for row in range(tile.size.rows):
            for col in range(tile.size.cols):
                assert tile.pixels[row][col] == color

    def test_instantiate(self, default_tile):
        """
        Test that the default size is 1x1.
        """
        assert default_tile.size == (1, 1)
        assert len(default_tile.pixels) == 1
        assert len(default_tile.pixels[0]) == 1

    def test_default_color(self):
        """
        Test that we can set the default color.
        """
        color = PixelColor(0, 0.5, 1)
        tile = Tile(default_color=color)
        assert tile.default_color is color
        assert tile.pixels[0][0] is color

        pixel = tile.pixels[0][0]
        assert pixel.red == 0
        assert pixel.green == 0.5
        assert pixel.blue == 1
        assert pixel.white is None

    def test_size(self, default_tile):
        """
        Test setting the size of the tile.
        """
        assert isinstance(default_tile.size, TileSize) is True

        default_tile.size = (10, 5)
        assert isinstance(default_tile.size, TileSize) is True
        assert default_tile.size.cols == 10
        assert default_tile.size.rows == 5

        default_tile.size = TileSize(8, 4)
        assert isinstance(default_tile.size, TileSize) is True
        assert default_tile.size.cols == 8
        assert default_tile.size.rows == 4

    def test_set_pixel(self, default_tile):
        """
        Test setting a individual pixel colors.
        """
        default_tile.size = (10, 5)
        main_color = PixelColor(100, 200, 50)
        special_color = PixelColor(99, 99, 99)
        self.init_pixels(default_tile, main_color)

        default_tile.set_pixel((1, 1), special_color)
        default_tile.set_pixel(PixelPosition(2, 2), special_color)

        for row in range(default_tile.size.rows):
            for col in range(default_tile.size.cols):
                pixel_color = default_tile.pixels[row][col]
                if (col, row) in [(1, 1), (2, 2)]:
                    assert pixel_color == special_color
                else:
                    assert pixel_color == main_color

    def test_clear(self, default_tile):
        """
        Test clearing a tile (setting all pixels to (0, 0, 0).
        """
        default_tile.size = (10, 5)
        color = PixelColor(100, 200, 50)
        self.init_pixels(default_tile, color)
        default_tile.clear()

        for row in range(default_tile.size.rows):
            for col in range(default_tile.size.cols):
                pixel_color = default_tile.pixels[row][col]
                assert pixel_color.red == 0
                assert pixel_color.green == 0
                assert pixel_color.blue == 0
                assert pixel_color.white == 0

    def test_init_pixels(self, default_tile):
        """
        Test initializing all pixels to the same color.
        """
        default_tile.size = (10, 5)
        color = PixelColor(100, 200, 50)
        self.init_pixels(default_tile, color)

    def test_data(self, default_tile):
        """
        Test sending different types of data to the tile.
        """
        for some_data in [99, 'something', [1, 2, 3], {'a': 1, 'b': 2}]:
            default_tile.data = some_data
            assert default_tile._data is some_data

    def test_repr(self):
        """
        Test the repr output.
        """
        tile = Tile(default_color=PixelColor(100, 200, 50, 10))
        assert repr(tile) == (
            'Tile(default_color=PixelColor(red=100, green=200, blue=50, '
            'white=10, normalized=False))'
        )
