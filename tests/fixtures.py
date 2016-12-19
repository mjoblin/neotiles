import pytest

from neotiles import TileManager, TileHandler


@pytest.fixture
def default_handler():
    return TileHandler()

@pytest.fixture
def manager_10x5():
    return TileManager(led_pin=18, size=(10, 5))

