import pytest

from neotiles import (
    PixelColor, TileHandler, TileManager, TilePosition, TileSize)
from neotiles.exceptions import NeoTilesError

from .fixtures import default_handler, manager_10x5


class TestTileManager:
    def test_instantiate(self):
        """
        Test instantiations.
        """
        # led_pin and size are required.
        with pytest.raises(NeoTilesError) as e:
            TileManager()
        assert 'size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            TileManager(led_pin=18)
        assert 'size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            TileManager(size=(8, 8))
        assert 'size and led_pin must be specified' in str(e)

        # Check default properties.
        tm = TileManager(size=(10, 5), led_pin=18)
        assert isinstance(tm.size, TileSize) is True
        assert tm.size == (10, 5)
        assert tm.brightness == 16
        assert len(tm.tiles) == 0
        assert len(tm.tile_handlers) == 0

    def test_register_tile(self, manager_10x5):
        """
        Test tile registration.
        """
        red_handler = TileHandler(default_color=PixelColor(128, 0, 0))
        grn_handler = TileHandler(default_color=PixelColor(0, 128, 0))

        # Register two tiles, making sure the tiles length looks good.
        manager_10x5.register_tile(
            size=(4, 4), root=(0, 0), handler=red_handler)
        assert len(manager_10x5.tiles) == 1

        manager_10x5.register_tile(
            size=(4, 4), root=(4, 0), handler=grn_handler)
        assert len(manager_10x5.tiles) == 2

        # Check that the tiles dict looks good.
        tiles = manager_10x5.tiles
        assert sorted(tiles[0].keys()) == ['handler', 'root', 'size']
        assert tiles[0]['handler'] == red_handler
        assert isinstance(tiles[0]['root'], TilePosition) is True
        assert tiles[0]['root'] == (0, 0)
        assert isinstance(tiles[0]['size'], TileSize) is True
        assert tiles[0]['size'] == (4, 4)

        # Check that the tile_handlers list looks OK.
        assert len(manager_10x5.tile_handlers) == 2
        assert isinstance(manager_10x5.tile_handlers[0], TileHandler) is True
        assert isinstance(manager_10x5.tile_handlers[1], TileHandler) is True

    def test_deregister_tile(self, manager_10x5):
        """
        Test tile deregistration.
        """
        red_handler = TileHandler(default_color=PixelColor(128, 0, 0))
        grn_handler = TileHandler(default_color=PixelColor(0, 128, 0))

        # Register two tiles, making sure the tiles length looks good.
        manager_10x5.register_tile(
            size=(4, 4), root=(0, 0), handler=red_handler)
        assert len(manager_10x5.tiles) == 1

        manager_10x5.register_tile(
            size=(4, 4), root=(4, 0), handler=grn_handler)
        assert len(manager_10x5.tiles) == 2

        # Deregister each tile.
        manager_10x5.deregister_tile(red_handler)
        assert len(manager_10x5.tiles) == 1

        manager_10x5.deregister_tile(grn_handler)
        assert len(manager_10x5.tiles) == 0

    def test_data(self, manager_10x5):
        """
        Test sending data to the handlers.
        """
        red_handler = TileHandler(default_color=PixelColor(128, 0, 0))
        grn_handler = TileHandler(default_color=PixelColor(0, 128, 0))

        manager_10x5.register_tile(
            size=(4, 4), root=(0, 0), handler=red_handler)
        manager_10x5.register_tile(
            size=(4, 4), root=(4, 0), handler=grn_handler)

        data = 'some data'
        manager_10x5.data(data)
        for handler in manager_10x5.tile_handlers:
            assert handler._data == data

    def test_brightness(self, manager_10x5):
        """
        Test setting the brightness attribute.
        """
        tm = TileManager(size=(3, 2), led_pin=18)
        assert tm.brightness == 16
        tm.brightness = 100
        assert tm.brightness == 100

        with pytest.raises(ValueError):
            tm.brightness = -1
        with pytest.raises(ValueError):
            tm.brightness = 256
        with pytest.raises(ValueError):
            tm.brightness = 'string'
        with pytest.raises(ValueError):
            tm.brightness = [50]

    def test_pixels(self, manager_10x5):
        """
        Test retrieving the pixel colors.
        """
        pixel = PixelColor(128, 0, 0, 0)
        red_handler = TileHandler(default_color=pixel)
        manager_10x5.register_tile(
            size=(10, 5), root=(0, 0), handler=red_handler)

        # Ensure we have the right number of cols and rows, and ensure that
        # each pixel is correct.
        pixels = manager_10x5.pixels
        assert len(pixels) == 5
        for row in pixels:
            assert len(row) == 10
            for matrix_pixel in row:
                assert matrix_pixel == pixel

    def test_repr(self):
        """
        Test the repr output.
        """
        tm = TileManager(size=(3, 2), led_pin=18)
        assert repr(tm) == (
            'TileManager(size=TileSize(cols=3, rows=2), led_pin=18, '
            'led_freq_hz=800000, led_dma=5, led_brightness=16, '
            'led_invert=False, strip_type=ws.WS2811_STRIP_GRB)'
        )

    def test_str(self):
        """
        Test the stringified output.
        """
        # Test default (no tile handlers).
        tm = TileManager(size=(3, 2), led_pin=18)
        assert str(tm) == (
            '[ 0]   0,  0,  0,  0  [ 1]   0,  0,  0,  0  [ 2]   0,  0,  0,  0  \n'
            '[ 3]   0,  0,  0,  0  [ 4]   0,  0,  0,  0  [ 5]   0,  0,  0,  0'
        )

        # Test with RGB.
        red_handler = TileHandler(default_color=PixelColor(128, 0, 0))
        tm.register_tile(size=(3, 2), root=(0, 0), handler=red_handler)
        assert str(tm) == (
            '[ 0] 128,  0,  0  [ 1] 128,  0,  0  [ 2] 128,  0,  0  \n'
            '[ 3] 128,  0,  0  [ 4] 128,  0,  0  [ 5] 128,  0,  0'
        )

        # Test with RGBW.
        red_handler = TileHandler(default_color=PixelColor(128, 1, 2, 3))
        tm.register_tile(size=(3, 2), root=(0, 0), handler=red_handler)
        assert str(tm) == (
            '[ 0] 128,  1,  2,  3  [ 1] 128,  1,  2,  3  [ 2] 128,  1,  2,  3  \n'
            '[ 3] 128,  1,  2,  3  [ 4] 128,  1,  2,  3  [ 5] 128,  1,  2,  3'
        )

        # Test normalized RGB.
        red_handler = TileHandler(default_color=PixelColor(1.0, 0, 0.5))
        tm.register_tile(size=(3, 2), root=(0, 0), handler=red_handler)
        assert str(tm) == (
            '[ 0] 255,  0,127  [ 1] 255,  0,127  [ 2] 255,  0,127  \n'
            '[ 3] 255,  0,127  [ 4] 255,  0,127  [ 5] 255,  0,127'
        )
