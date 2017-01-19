import pytest

from neotiles import (
    MatrixSize, PixelColor, Tile, TileManager, TilePosition)
from neotiles.matrixes import NTNeoPixelMatrix, NTRGBMatrix

from .fixtures import manager_neopixel, manager_rgb


class TestTileManager:
    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_instantiate(self, manager):
        """
        Test instantiations.
        """
        cols = manager.matrix_size.cols
        rows = manager.matrix_size.rows

        # Check default properties.
        assert isinstance(manager.matrix_size, MatrixSize) is True
        assert manager.matrix_size == (cols, rows)
        assert len(manager.tiles_meta) == 0
        assert len(manager.tiles) == 0

        pixels = manager.pixels
        assert len(pixels) == rows
        for row in pixels:
            assert len(row) == cols

    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_register_tile(self, manager):
        """
        Test tile registration.
        """
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        grn_tile = Tile(default_color=PixelColor(0, 128, 0))

        # Register two tiles, making sure the tiles length looks good.
        manager.register_tile(
            tile=red_tile, size=(4, 4), root=(0, 0))
        assert len(manager.tiles_meta) == 1

        manager.register_tile(
            tile=grn_tile, size=(4, 4), root=(4, 0))
        assert len(manager.tiles_meta) == 2

        # Check that the tiles dict looks good.
        tiles = manager.tiles_meta
        assert sorted(tiles[0].keys()) == ['root', 'tile_object']
        assert tiles[0]['tile_object'] == red_tile
        assert isinstance(tiles[0]['root'], TilePosition) is True
        assert tiles[0]['root'] == (0, 0)

        # Check that the tile_objects list looks OK.
        assert len(manager.tiles) == 2
        assert isinstance(manager.tiles[0], Tile) is True
        assert isinstance(manager.tiles[1], Tile) is True

    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_deregister_tile(self, manager):
        """
        Test tile deregistration.
        """
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        grn_tile = Tile(default_color=PixelColor(0, 128, 0))

        # Register two tiles, making sure the tiles length looks good.
        manager.register_tile(
            tile=red_tile, size=(4, 4), root=(0, 0))
        assert len(manager.tiles_meta) == 1

        manager.register_tile(
            tile=grn_tile, size=(4, 4), root=(4, 0))
        assert len(manager.tiles_meta) == 2

        # Deregister each tile.
        manager.deregister_tile(red_tile)
        assert len(manager.tiles_meta) == 1

        manager.deregister_tile(grn_tile)
        assert len(manager.tiles_meta) == 0

    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_data(self, manager):
        """
        Test sending data to the tile objects.
        """
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        grn_tile = Tile(default_color=PixelColor(0, 128, 0))

        manager.register_tile(
            tile=red_tile, size=(4, 4), root=(0, 0))
        manager.register_tile(
            tile=grn_tile, size=(4, 4), root=(4, 0))

        data = 'some data'
        manager.send_data_to_tiles(data)
        for tile_object in manager.tiles:
            assert tile_object._data == data

    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_brightness(self, manager):
        """
        Test setting the brightness attribute.
        """
        manager.brightness = 100
        assert manager.brightness == 100

        with pytest.raises(ValueError):
            manager.brightness = -1
        with pytest.raises(ValueError):
            manager.brightness = 256
        with pytest.raises(ValueError):
            manager.brightness = 'string'
        with pytest.raises(ValueError):
            manager.brightness = [50]

    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_pixels(self, manager):
        """
        Test retrieving the pixel colors.
        """
        cols = manager.matrix_size.cols
        rows = manager.matrix_size.rows

        red_pixel = PixelColor(128, 0, 0, 0)
        red_tile = Tile(default_color=red_pixel)
        manager.register_tile(
            tile=red_tile, size=(cols, rows), root=(0, 0))

        # Ensure we have the right number of cols and rows, and ensure that
        # each pixel is correct.
        pixels = manager.pixels
        assert len(pixels) == rows
        for row in pixels:
            assert len(row) == cols
            for matrix_pixel in row:
                assert matrix_pixel == red_pixel

    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_tile_visibility(self, manager):
        """
        Test that an invisible tile does not have its pixels drawn to the
        virtual matrix.
        """
        cols = manager.matrix_size.cols
        rows = manager.matrix_size.rows

        red_pixel = PixelColor(128, 0, 0, 0)
        red_tile = Tile(default_color=red_pixel)
        red_tile.visible = False

        manager.register_tile(
            tile=red_tile, size=(cols, rows), root=(0, 0))

        manager._set_pixels_from_tiles()
        pixels = manager.pixels
        for row in pixels:
            for matrix_pixel in row:
                # Default pixel color is 0, 0, 0, 0
                assert (matrix_pixel.red == matrix_pixel.green ==
                        matrix_pixel.blue == matrix_pixel.white == 0)

        # With tile visibility enabled, the red pixels should get drawn to the
        # virtual matrix.
        red_tile.visible = True
        manager._set_pixels_from_tiles()
        for row in manager.pixels:
            for matrix_pixel in row:
                assert matrix_pixel == red_pixel

    @pytest.mark.parametrize('manager', [manager_neopixel(), manager_rgb()])
    def test_unsettable_attributes(self, manager):
        """
        Try setting unsettable attributes.
        """
        for unsettable in ['matrix_size', 'tiles', 'tiles_meta', 'pixels']:
            with pytest.raises(AttributeError):
                setattr(manager, unsettable, 'foo')

    @pytest.mark.parametrize('matrix', [
        NTNeoPixelMatrix(size=(3, 3), led_pin=18),
        NTRGBMatrix()
    ])
    def test_repr(self, matrix):
        """
        Test the repr output for the different matrix types.
        """
        tm = TileManager(matrix)
        assert repr(tm) == (
            'TileManager(matrix={}, draw_fps=10)'.format(repr(matrix))
        )

    @pytest.mark.parametrize('matrix', [
        NTNeoPixelMatrix(size=(3, 3), led_pin=18),
    ])
    def test_str(self, matrix):
        """
        Test the stringified output.
        """
        # Test default (no tile).
        tm = TileManager(matrix)
        assert str(tm) == (
            '[ 0]   0,  0,  0,  0  [ 1]   0,  0,  0,  0  [ 2]   0,  0,  0,  0  \n'
            '[ 3]   0,  0,  0,  0  [ 4]   0,  0,  0,  0  [ 5]   0,  0,  0,  0  \n'
            '[ 6]   0,  0,  0,  0  [ 7]   0,  0,  0,  0  [ 8]   0,  0,  0,  0'
        )

        # Test with RGB.
        red_tile = Tile(default_color=PixelColor(128, 0, 0))
        tm.register_tile(tile=red_tile, size=(3, 3), root=(0, 0))
        assert str(tm) == (
            '[ 0] 128,  0,  0  [ 1] 128,  0,  0  [ 2] 128,  0,  0  \n'
            '[ 3] 128,  0,  0  [ 4] 128,  0,  0  [ 5] 128,  0,  0  \n'
            '[ 6] 128,  0,  0  [ 7] 128,  0,  0  [ 8] 128,  0,  0'
        )

        # Test with RGBW.
        red_tile = Tile(default_color=PixelColor(128, 1, 2, 3))
        tm.register_tile(tile=red_tile, size=(3, 3), root=(0, 0))
        assert str(tm) == (
            '[ 0] 128,  1,  2,  3  [ 1] 128,  1,  2,  3  [ 2] 128,  1,  2,  3  \n'
            '[ 3] 128,  1,  2,  3  [ 4] 128,  1,  2,  3  [ 5] 128,  1,  2,  3  \n'
            '[ 6] 128,  1,  2,  3  [ 7] 128,  1,  2,  3  [ 8] 128,  1,  2,  3'
        )

        # Test normalized RGB.
        red_tile = Tile(default_color=PixelColor(1.0, 0, 0.5))
        tm.register_tile(tile=red_tile, size=(3, 3), root=(0, 0))
        assert str(tm) == (
            '[ 0] 255,  0,127  [ 1] 255,  0,127  [ 2] 255,  0,127  \n'
            '[ 3] 255,  0,127  [ 4] 255,  0,127  [ 5] 255,  0,127  \n'
            '[ 6] 255,  0,127  [ 7] 255,  0,127  [ 8] 255,  0,127'
        )
