import pytest

from neotiles import TileHandler


@pytest.fixture
def default_handler():
    return TileHandler()

