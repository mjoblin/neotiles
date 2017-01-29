import pytest

from neotiles import TileManager, Tile
from neotiles.matrixes import NTNeoPixelMatrix, NTRGBMatrix


@pytest.fixture
def default_tile():
    return Tile()


@pytest.fixture
def manager_neopixel():
    return TileManager(NTNeoPixelMatrix(size=(10, 5), led_pin=18))


@pytest.fixture
def manager_rgb():
    return TileManager(NTRGBMatrix(chain_length=1))
