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
        Test that we can get and set the default color.
        """
        color = PixelColor(0, 0.5, 1)
        tile = Tile(default_color=color)
        assert tile.default_color is color

        # When instantiating with a color, check that the pixels were set.
        assert tile.pixels[0][0] is color

        pixel = tile.pixels[0][0]
        assert pixel.red == 0
        assert pixel.green == 0.5
        assert pixel.blue == 1
        assert pixel.white is None

        # Try a new color by setting the default_color attribute.
        color = PixelColor(0.1, 0.2, 0.3)
        tile.default_color = color
        assert tile.default_color.components == (0.1, 0.2, 0.3)

        # Draw the tile and make sure the pixels were set.
        tile.draw()

        pixel = tile.pixels[0][0]
        assert pixel.red == 0.1
        assert pixel.green == 0.2
        assert pixel.blue == 0.3
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

        # Check that an out of bounds index moves along silently.
        default_tile.set_pixel((999, -999), PixelColor(0, 0, 0, 0))

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

    def test_data_get(self, default_tile):
        """
        Test getting the data attribute.
        """
        assert default_tile._data is None

        default_tile.data = 'foo'
        assert default_tile.data == 'foo'

    def test_animate(self, default_tile):
        """
        Test the animate attribute.
        """
        assert default_tile.animate is True

        default_tile.animate = False
        assert default_tile.animate is False

        with pytest.raises(ValueError) as e:
            default_tile.animate = 'foo'
        assert 'must be set to True or False' in str(e)

    def test_is_accepting_data(self, default_tile):
        """
        Test the animate attribute.
        """
        assert default_tile.is_accepting_data is True

        default_tile.is_accepting_data = False
        assert default_tile.is_accepting_data is False

        with pytest.raises(ValueError) as e:
            default_tile.is_accepting_data = 'foo'
        assert 'must be set to True or False' in str(e)

    def test_visibility(self, default_tile):
        """
        Test the visible attribute.
        """
        assert default_tile.visible is True

        default_tile.visible = False
        assert default_tile.visible is False

        with pytest.raises(ValueError) as e:
            default_tile.visible = 'foo'
        assert 'must be set to True or False' in str(e)

    def test_on_size_set(self):
        """
        Test the on_size_set handler.  This handler should be called whenever
        the tile size is set.
        """
        class TestOnSizeSetTile(Tile):
            def __init__(self):
                super(TestOnSizeSetTile, self).__init__()
                self.some_state = False

            def on_size_set(self):
                self.some_state = True

        test_tile = TestOnSizeSetTile()
        assert test_tile.some_state is False

        test_tile.size = TileSize(8, 8)
        assert test_tile.some_state is True

    def test_unsettable_attributes(self, default_tile):
        """
        Try setting unsettable attributes.
        """
        for unsettable in ['pixels']:
            with pytest.raises(AttributeError):
                setattr(default_tile, unsettable, 'foo')

    def test_repr(self):
        """
        Test the repr output.
        """
        tile = Tile(default_color=PixelColor(100, 200, 50, 10))
        assert repr(tile) == (
            'Tile(default_color=PixelColor(red=100, green=200, blue=50, '
            'white=10, normalized=False))'
        )

    def test_subclass_default_color(self):
        """
        Tile subclasses should get a blank default color.
        """
        class TileSubclass(Tile):
            pass

        tile = TileSubclass()
        assert tile.default_color.components == (0, 0, 0, 0)
