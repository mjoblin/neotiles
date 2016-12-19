import pytest

from neotiles import TileManager, TileSize
from neotiles.exceptions import NeoTilesError

from .fixtures import default_handler, manager_10x5


# TODO: Currently can't seem to instantiate TileManager in pytest.  Attempts
#   result in "RuntimeError: ws2811_init failed with code -7 (Unable to
#   initialize GPIO)", even when running as root.

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
