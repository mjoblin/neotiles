import pytest

from neotiles import TileManager
from neotiles.exceptions import NeoTilesError

from .fixtures import default_handler, manager_10x5


class TestTileManager:
    def test_instantiate(self):
        """
        """
        # led_pin and size are requred.
        with pytest.raises(NeoTilesError) as e:
            TileManager()
        assert 'size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            TileManager(led_pin=18)
        assert 'size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            TileManager(size=(8, 8))
        assert 'size and led_pin must be specified' in str(e)

    def test_intensity(self):
        pass

    def test_register(self):
        pass

    def test_deregister(self):
        pass

    def test_get_tiles(self):
        pass

    def test_get_handlers(self):
        pass

