import pytest

from neotiles import (
    MatrixSize, PixelColor, Tile, TileManager, TilePosition)
from neotiles.exceptions import NeoTilesError

from .fixtures import default_tile, manager_10x5


class TestTileManager:
    def test_instantiate(self):
        """
        Test instantiations.
        """
        # led_pin and matrix_size are required.
        with pytest.raises(NeoTilesError) as e:
            TileManager()
        assert 'matrix_size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            TileManager(led_pin=18)
        assert 'matrix_size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            TileManager(matrix_size=(8, 8))
        assert 'matrix_size and led_pin must be specified' in str(e)

        # Check default properties.
        tm = TileManager(matrix_size=(10, 5), led_pin=18)
        assert isinstance(tm.matrix_size, MatrixSize) is True
        assert tm.matrix_size == (10, 5)
        assert tm.brightness == 64
        assert len(tm.tiles_meta) == 0
        assert len(tm.tiles) == 0

    def test_register_tile(self, manager_10x5):
        """
        Test tile registration.
        """
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        grn_tile = Tile(default_color=PixelColor(0, 128, 0))

        # Register two tiles, making sure the tiles length looks good.
        manager_10x5.register_tile(
            tile=red_tile, size=(4, 4), root=(0, 0))
        assert len(manager_10x5.tiles_meta) == 1

        manager_10x5.register_tile(
            tile=grn_tile, size=(4, 4), root=(4, 0))
        assert len(manager_10x5.tiles_meta) == 2

        # Check that the tiles dict looks good.
        tiles = manager_10x5.tiles_meta
        assert sorted(tiles[0].keys()) == ['root', 'tile_object']
        assert tiles[0]['tile_object'] == red_tile
        assert isinstance(tiles[0]['root'], TilePosition) is True
        assert tiles[0]['root'] == (0, 0)

        # Check that the tile_objects list looks OK.
        assert len(manager_10x5.tiles) == 2
        assert isinstance(manager_10x5.tiles[0], Tile) is True
        assert isinstance(manager_10x5.tiles[1], Tile) is True

    def test_deregister_tile(self, manager_10x5):
        """
        Test tile deregistration.
        """
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        grn_tile = Tile(default_color=PixelColor(0, 128, 0))

        # Register two tiles, making sure the tiles length looks good.
        manager_10x5.register_tile(
            tile=red_tile, size=(4, 4), root=(0, 0))
        assert len(manager_10x5.tiles_meta) == 1

        manager_10x5.register_tile(
            tile=grn_tile, size=(4, 4), root=(4, 0))
        assert len(manager_10x5.tiles_meta) == 2

        # Deregister each tile.
        manager_10x5.deregister_tile(red_tile)
        assert len(manager_10x5.tiles_meta) == 1

        manager_10x5.deregister_tile(grn_tile)
        assert len(manager_10x5.tiles_meta) == 0

    def test_data(self, manager_10x5):
        """
        Test sending data to the tile objects.
        """
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        grn_tile = Tile(default_color=PixelColor(0, 128, 0))

        manager_10x5.register_tile(
            tile=red_tile, size=(4, 4), root=(0, 0))
        manager_10x5.register_tile(
            tile=grn_tile, size=(4, 4), root=(4, 0))

        data = 'some data'
        manager_10x5.send_data_to_tiles(data)
        for tile_object in manager_10x5.tiles:
            assert tile_object._data == data

    def test_brightness(self, manager_10x5):
        """
        Test setting the brightness attribute.
        """
        tm = TileManager(matrix_size=(3, 2), led_pin=18)
        assert tm.brightness == 64
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
        red_pixel = PixelColor(128, 0, 0, 0)
        red_tile = Tile(default_color=red_pixel)
        manager_10x5.register_tile(
            tile=red_tile, size=(10, 5), root=(0, 0))

        # Ensure we have the right number of cols and rows, and ensure that
        # each pixel is correct.
        pixels = manager_10x5.pixels
        assert len(pixels) == 5
        for row in pixels:
            assert len(row) == 10
            for matrix_pixel in row:
                assert matrix_pixel == red_pixel

    def test_tile_visibility(self, manager_10x5):
        """
        Test that an invisible tile does not have its pixels drawn to the
        virtual matrix.
        """
        red_pixel = PixelColor(128, 0, 0, 0)
        red_tile = Tile(default_color=red_pixel)
        red_tile.visible = False

        manager_10x5.register_tile(
            tile=red_tile, size=(10, 5), root=(0, 0))

        manager_10x5._set_pixels_from_tiles()
        pixels = manager_10x5.pixels
        for row in pixels:
            for matrix_pixel in row:
                # Default pixel color is 0, 0, 0, 0
                assert (matrix_pixel.red == matrix_pixel.green ==
                        matrix_pixel.blue == matrix_pixel.white == 0)

        # With tile visibility enabled, the red pixels should get drawn to the
        # virtual matrix.
        red_tile.visible = True
        manager_10x5._set_pixels_from_tiles()
        pixels = manager_10x5.pixels
        for row in pixels:
            for matrix_pixel in row:
                assert matrix_pixel == red_pixel

    def test_unsettable_attributes(self, manager_10x5):
        """
        Try setting unsettable attributes.
        """
        for unsettable in ['matrix_size', 'tiles', 'tiles_meta', 'pixels']:
            with pytest.raises(AttributeError):
                setattr(manager_10x5, unsettable, 'foo')

    def test_repr(self):
        """
        Test the repr output.
        """
        tm = TileManager(matrix_size=(3, 2), led_pin=18)
        assert repr(tm) == (
            'TileManager(matrix_size=MatrixSize(cols=3, rows=2), led_pin=18, '
            'led_freq_hz=800000, led_dma=5, led_brightness=64, '
            'led_invert=False, strip_type=ws.WS2811_STRIP_GRB)'
        )

    def test_str(self):
        """
        Test the stringified output.
        """
        # Test default (no tile).
        tm = TileManager(matrix_size=(3, 2), led_pin=18)
        assert str(tm) == (
            '[ 0]   0,  0,  0,  0  [ 1]   0,  0,  0,  0  [ 2]   0,  0,  0,  0  \n'
            '[ 3]   0,  0,  0,  0  [ 4]   0,  0,  0,  0  [ 5]   0,  0,  0,  0'
        )

        # Test with RGB.
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        tm.register_tile(tile=red_tile, size=(3, 2), root=(0, 0))
        assert str(tm) == (
            '[ 0] 128,  0,  0  [ 1] 128,  0,  0  [ 2] 128,  0,  0  \n'
            '[ 3] 128,  0,  0  [ 4] 128,  0,  0  [ 5] 128,  0,  0'
        )

        # Test with RGBW.
        red_tile = Tile(default_color=PixelColor(128, 1, 2, 3))
        tm.register_tile(tile=red_tile, size=(3, 2), root=(0, 0))
        assert str(tm) == (
            '[ 0] 128,  1,  2,  3  [ 1] 128,  1,  2,  3  [ 2] 128,  1,  2,  3  \n'
            '[ 3] 128,  1,  2,  3  [ 4] 128,  1,  2,  3  [ 5] 128,  1,  2,  3'
        )

        # Test normalized RGB.
        red_tile = Tile(default_color=PixelColor(1.0, 0, 0.5))
        tm.register_tile(tile=red_tile, size=(3, 2), root=(0, 0))
        assert str(tm) == (
            '[ 0] 255,  0,127  [ 1] 255,  0,127  [ 2] 255,  0,127  \n'
            '[ 3] 255,  0,127  [ 4] 255,  0,127  [ 5] 255,  0,127'
        )
