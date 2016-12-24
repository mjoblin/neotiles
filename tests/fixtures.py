import pytest

from neotiles import TileManager, Tile


@pytest.fixture
def default_tile():
    return Tile()


@pytest.fixture
def manager_10x5():
    return TileManager(matrix_size=(10, 5), led_pin=18)

