import random

from .tilecolor import TileColor
from .neotiles import TileSize, TilePosition


class TileHandler:
    """
    Handles the data processing and pixel display for a single tile.

    This class by default displays a random color inside the tile and ignores
    any incoming data on the :attr:`~data` property.  This class will normally
    be subclassed to implement more useful data-based pixel coloring.

    Tiles are assigned a ``size`` from the :class:`NeoTiles` object that
    they're registered with (see :meth:`NeoTiles.register_tile`).  Tiles
    are responsible for determining the color of each of their pixels (usually
    based on incoming :meth:`data` which is also provided by the NeoTiles
    object they're registered with).

    :param default_color: (:class:`TileColor`) Default color for the tile.
    """
    def __init__(self, default_color=None):
        self._default_color = TileColor(
            red=random.random(),
            green=random.random(),
            blue=random.random(),
            white=random.random()
        )

        if default_color:
            self.default_color = TileColor(*default_color)

        self._size = TileSize(1, 1)
        self._data = None
        self._init_pixels()

    def _init_pixels(self, color=None):
        """
        Initialize all pixels in the tile to the given ``color``.

        :param color: (:class:`TileColor`) Color to initialize the pixels to.
        """
        # A two-dimension array of pixel colors for the tile.
        display_color = self._default_color if color is None else color

        self._pixels = [
            [display_color for col in range(self._size.cols)]
            for row in range(self._size.rows)
        ]

    @property
    def data(self):
        """
        The most recent data.
        """
        return self._data

    @data.setter
    def data(self, in_data):
        """
        Sets the data.

        :param in_data: (all) The data.
        """
        self._data = in_data

    @property
    def default_color(self):
        return self._default_color

    @default_color.setter
    def default_color(self, color):
        self._default_color = TileColor(*color)

    @property
    def pixels(self):
        return self._pixels

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = TileSize(*value)
        self._init_pixels()

    def clear(self):
        """
        Clears the tile (sets all pixels to ``TileColor(0, 0, 0, 0)``).
        """
        self._init_pixels(color=TileColor(0, 0, 0, 0))

    def set_pixel(self, pos, color):
        """
        Sets the pixel at the given ``pos`` to the given ``color``.

        :param pos: (:class:`~TilePosition`) Pixel to set the color of.
        :param color: (:class:`~TileColor`) Color to assign.
        """
        # Our pixel matrix is indexed by row number first, then column within
        # the row.
        pos = TilePosition(*pos)
        self._pixels[pos.y][pos.x] = color

