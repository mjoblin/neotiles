import random

import wrapt

from .pixelcolor import PixelColor
from .tilemanager import PixelPosition, TileSize


class Tile(object):
    """
    Handles the data processing and pixel coloring for a single tile.

    This class by default displays a random RGBW color inside the tile and
    ignores any incoming data on the :attr:`data` attribute.

    **This class will normally be subclassed to implement more useful
    data-based pixel coloring.**  Subclasses will usually override the
    :meth:`draw` method to process the data last sent to the tile and then call
    the :meth:`set_pixel` method to set the color of each pixel in the tile.

    Subclassing example, overriding the draw method: ::

        from neotiles import PixelColor, Tile

        # Define our own MyRGBTile class.
        class MyRGBTile(Tile):
            def draw(self):
                # Determine our display color based on the tile's data
                # We expect the data to be one of 'red', 'green', 'blue'.
                if self.data == 'red':
                    display_color = PixelColor(255, 0, 0, 0)
                elif self.data == 'green':
                    display_color = PixelColor(0, 255, 0, 0)
                elif self.data == 'blue':
                    display_color = PixelColor(0, 0, 255, 0)
                else:
                    display_color = PixelColor(0, 0, 0, 0)

                # Set every pixel in the tile to the display color.
                for row in range(self.size.rows):
                    for col in range(self.size.cols):
                        self.set_pixel((col, row), display_color)

    **Animating tiles:**

    If ``animate=True`` then the tile's :meth:`draw` method will be called for
    every frame by the :class:`~TileManager` that the tile is registered with.
    Tiles will only animate if ``animate=True`` and if the tile's TileManager
    has set its ``anim_fps`` to a non-None integer value.

    **Tile size:**

    Subclasses can access their tile size via the :attr:`size` attribute
    (a :class:`TileSize` object).  This is useful when drawing the tile as
    the :meth:`draw` method needs to know the dimensions of the tile.

    Tiles are assigned their :attr:`size` by the TileManager object that
    they're registered with (see :meth:`TileManager.register_tile`).  Tiles are
    responsible for determining the color of each of their pixels, usually
    based on incoming :attr:`data` which can be set manually or be provided by
    the TileManager object via :meth:`TileManager.send_data_to_tiles`.

    :param default_color: (:class:`PixelColor`) Default color for all pixels in
        the tile.
    """
    def __init__(self, default_color=None, animate=True):
        # Set the default color to something random if we're not a subclass
        # of Tile.  This is intended to be helpful in the super simple case
        # where Tile isn't being subclassed and we want to as least see
        # *something* being displayed with as little setup as possible.  If we
        # don't do this then subclasses will flash a random color before they
        # start rendering their own pixels, and being forced to call clear() is
        # a bit messy.
        if self.__class__.__name__ == 'Tile':
            self._default_color = PixelColor(
                red=random.random(),
                green=random.random(),
                blue=random.random(),
                white=random.random()
            )
        else:
            self._default_color = PixelColor(0, 0, 0, 0)

        if default_color:
            self._default_color = default_color

        self._animate = True
        self._is_accepting_data = True
        self._size = None
        self._data = None
        self._pixels = None

        self.animate = animate
        self.size = TileSize(1, 1)

    def __repr__(self):
        return '{}(default_color={})'.format(
            self.__class__.__name__,
            self._default_color
        )

    @wrapt.synchronized
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

    def clear(self):
        """
        Clears the tile by setting all the tile's pixels to
        ``PixelColor(0, 0, 0, 0)``.  This does not update the pixels on the
        hardware neopixel matrix.
        """
        self._init_pixels(color=PixelColor(0, 0, 0, 0))

    def draw(self):
        """
        Sets the pixel color of all the pixels in the tile, usually based on
        the data currently associated with the tile.

        Note that setting the pixel colors for the tile does not affect the
        pixels on the hardware neopixel matrix.  See :meth:`set_pixel` for more
        information.

        **This method is usually overridden by subclasses and is called
        automatically by the TileManager object that the tile is registered
        with.**

        It's usually a good idea to break out of the draw method if the tile's
        data is ``None`` as that usually means there's no data to process yet
        (unless data of ``None`` means something in your case): ::

            def draw(self):
                if self.data is None:
                    return

                # Draw something...
        """
        self._init_pixels()

    @wrapt.synchronized
    def set_pixel(self, pos, color):
        """
        Sets the pixel at the given ``pos`` in the tile to the given ``color``.

        This is only updating the pixel color of a virtual pixel within the
        tile and is not updating the actual neopixel hardware.  The neopixel
        hardware is updated separately by
        :meth:`TileManager.draw_hardware_matrix`.

        :param pos: (:class:`~PixelPosition`) Tile pixel to set the color of.
        :param color: (:class:`~PixelColor`) Color to assign.
        """
        pos = PixelPosition(*pos)

        try:
            self._pixels[pos.y][pos.x] = color
        except IndexError:
            pass

    @property
    def animate(self):
        """
        (bool) Get or set whether the tile will be included in the
        TileManager's animation loop.

        Setting this attribute to True will result in the TileManager calling
        the tile's :meth:`draw` method for every frame it its animation loop.
        """
        return self._animate

    @animate.setter
    @wrapt.synchronized
    def animate(self, val):
        if val is not True and val is not False:
            raise ValueError('animate must be set to True or False')

        self._animate = val

    @property
    def data(self):
        """
        Get or set the data associated with the tile.

        This attribute can either be set manually, or will be set automatically
        via :meth:`TileManager.send_data_to_tiles` on the TileManager object
        the tile is registered with.

        The data assigned to the ``data`` attribute can be anything, so long as
        the tile knows how to interpret it (which is usually done in the
        :meth:`draw` method).

        Note that a this does not make a copy of the data.  This means that if
        you assign (say) a list or a dictionary to the ``data`` attribute then
        the tile is sharing that data with whatever initially created it.
        """
        return self._data

    @data.setter
    @wrapt.synchronized
    def data(self, in_data):
        if self._is_accepting_data:
            self._data = in_data

    @property
    def default_color(self):
        """
        (:class:`~PixelColor`) Get or set the default color for the tile.  This
        is usually ignored, assuming the tile is painting its own pixel colors.
        """
        return self._default_color

    @default_color.setter
    def default_color(self, color):
        self._default_color = color

    @property
    def is_accepting_data(self):
        """
        (bool) Get or set whether the tile is accepting data.

        You can set this attribute to False if you want your tile to ignore
        any attempts to update its data before it has finished any longer-term
        rendering task it might be working on.
        """
        return self._is_accepting_data

    @is_accepting_data.setter
    @wrapt.synchronized
    def is_accepting_data(self, val):
        if val is not True and val is not False:
            raise ValueError('is_accepting_data must be set to True or False')

        self._is_accepting_data = val

    @property
    def pixels(self):
        """
        Get the tile's current pixel colors.

        The colors are returned as a two-dimensional list (with the same
        dimensions as :attr:`size`) of :class:`~PixelColor` objects.
        """
        return self._pixels

    @property
    def size(self):
        """
        (:class:`TileSize`) Get or set the size of the tile.

        This attribute will be set automatically by the TileManager object the
        tile is registered with.
        """
        return self._size

    @size.setter
    @wrapt.synchronized
    def size(self, value):
        self._size = TileSize(*value)
        self._init_pixels()
