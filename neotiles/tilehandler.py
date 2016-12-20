import random

from .pixelcolor import PixelColor
from .tilemanager import PixelPosition, TileSize


class TileHandler(object):
    """
    Handles the data processing and pixel coloring for a single tile.

    This class by default displays a random RGBW color inside the tile and
    ignores any incoming data on the :meth:`data` method.

    **This class will normally be subclassed to implement more useful
    data-based pixel coloring.**  Subclasses will usually override the
    :meth:`data` method to process the incoming data and then call the
    :meth:`set_pixel` method to set the color of each pixel in the tile.
    Subclasses can access their tile size via the :attr:`size` attribute
    (a :class:`TileSize` object).

    Tiles are assigned their :attr:`size` from the :class:`~TileManager` object
    that they're registered with (see :meth:`TileManager.register_tile`).
    Tiles are responsible for determining the color of each of their pixels,
    usually based on incoming :meth:`data` which can be called manually or be
    provided by the TileManager object they're registered with.

    :param default_color: (:class:`PixelColor`) Default color for all pixels in
        the tile.
    """
    def __init__(self, default_color=None):
        self._default_color = PixelColor(
            red=random.random(),
            green=random.random(),
            blue=random.random(),
            white=random.random()
        )

        if default_color:
            self.default_color = default_color

        self._size = None
        self._pixels = None
        self._data = None

        self.size = TileSize(1, 1)

    def __repr__(self):
        return '{}(default_color={})'.format(
            self.__class__.__name__,
            self._default_color
        )

    def _init_pixels(self, color=None):
        """
        Initialize all pixels in the tile to the given ``color``.

        :param color: (:class:`PixelColor`) Color to initialize the pixels to.
        """
        display_color = self._default_color if color is None else color

        # A two-dimension array of pixel colors for the tile.
        self._pixels = [
            [display_color for col in range(self._size.cols)]
            for row in range(self._size.rows)
        ]

    def data(self, in_data):
        """
        Sends new data to the tile.

        This method can either be called manually, or will be called
        automatically via the :meth:`TileManager.data` method on the
        TileManager object the tile is registered with.

        The value of ``in_data`` can be anything, so long as the TileHandler
        object knows how to interpret it.

        The data() method will normally take care of painting all the pixels
        in the tile.  For example: ::

            class MyRGBTile(TileHandler):
                def data(self, in_data):
                    super(MyRGBTile, self).data(in_data)

                    # Determine our display color based on in_data. We
                    # expect in_data to be one of 'red', 'green', 'blue'.
                    if in_data == 'red':
                        display_color = PixelColor(255, 0, 0, 0)
                    elif in_data == 'green':
                        display_color = PixelColor(0, 255, 0, 0)
                    elif in_data == 'blue':
                        display_color = PixelColor(0, 0, 255, 0)
                    else:
                        display_color = PixelColor(0, 0, 0, 0)

                    # Set every pixel in the tile to the display color.
                    for row in range(self.size.rows):
                        for col in range(self.size.cols):
                            self.set_pixel((col, row), display_color)

        :param in_data: (all) The data to send to the tile.
        """
        self._data = in_data

    def set_pixel(self, pos, color):
        """
        Sets the pixel at the given ``pos`` in the tile to the given ``color``.

        :param pos: (:class:`~PixelPosition`) Tile pixel to set the color of.
        :param color: (:class:`~PixelColor`) Color to assign.
        """
        pos = PixelPosition(*pos)
        self._pixels[pos.y][pos.x] = color

    def clear(self):
        """
        Clears the tile (sets all tile pixels to ``PixelColor(0, 0, 0, 0)``).
        """
        self._init_pixels(color=PixelColor(0, 0, 0, 0))

    @property
    def default_color(self):
        """
        The default color for the tile.  This is usually ignored, assuming the
        tile is painting its own pixel colors.

        :getter: (:class:`~PixelColor`) Returns the default tile color.
        :setter: (:class:`~PixelColor`) Sets the default tile color.
        """
        return self._default_color

    @default_color.setter
    def default_color(self, color):
        self._default_color = color

    @property
    def pixels(self):
        """
        A two-dimensional list which contains the color of each neopixel in the
        tile.

        :getter: ([[:class:`~PixelColor`, ...], ...]) Returns a two-dimensional
            list of tile pixel colors.
        """
        return self._pixels

    @property
    def size(self):
        """
        The size of the tile (in columns and rows).

        :getter: (:class:`~TileSize`) Returns the size of the tile.
        :setter: (:class:`~TileSize`) Sets the size of the tile.  This will be
            set automatically by the :class:`~TileManager` object the tile is
            registered with.
        """
        return self._size

    @size.setter
    def size(self, value):
        self._size = TileSize(*value)
        self._init_pixels()
