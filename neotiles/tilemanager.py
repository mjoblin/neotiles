from collections import namedtuple
import threading
import time

import wrapt

from neotiles.exceptions import NeoTilesError
from neotiles.pixelcolor import PixelColor


MatrixSize = namedtuple('MatrixSize', 'cols rows')
TileSize = namedtuple('TileSize', 'cols rows')
TilePosition = namedtuple('TilePosition', 'x y')
PixelPosition = namedtuple('PixelPosition', 'x y')


class StoppableThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check regularly
    for the stopped() condition.

    http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
    """
    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_requested = threading.Event()

    def stop(self):
        self._stop_requested.set()

    def stopped(self):
        return self._stop_requested.isSet()


class TileManager(object):
    """
    Manages all the tiles displayed on a hardware matrix (either a neopixel
    matrix or an RGB matrix).

    TileManager is the only class in neotiles which affects the actual hardware
    matrix.

    Example usage: ::

        from neotiles import TileManager
        from neotiles.matrixes import NTNeoPixelMatrix

        tiles = TileManager(NTNeoPixelMatrix(size=(8, 8), led_pin=18))

    Or with an RGB matrix: ::

        from neotiles import TileManager
        from neotiles.matrixes import NTRGBMatrix

        tiles = TileManager(NTRGBMatrix(rows=32, chain=2))

    **Animation**:

    The ``draw_fps`` (draw frames per second) parameter controls how many times
    per second the animation loop -- which runs in a separate thread -- will
    call :meth:`draw_hardware_matrix` which in turn calls all the tiles'
    :meth:`Tile.draw` methods.  If ``draw_fps=None`` then the matrix will not
    be drawn automatically and you must call :meth:`draw_hardware_matrix`
    manually.

    The animation loop will attempt to re-draw the matrix at a rate of
    ``draw_fps`` times per second.  This rate may or may not be achieved
    depending on whatever else the CPU is doing, including the compute load
    created by the tiles' :meth:`Tile.draw` methods.

    The animation loop assumes that something else will be sending data to the
    tiles via the :attr:`Tile.data` attribute or the
    :meth:`TileManager.send_data_to_tiles` method.  If that isn't happening
    then the animation loop will likely keep re-drawing the matrix with the
    same unchanging pixel colors.

    :param matrix: (:class:`~neotiles.matrixes.NTNeoPixelMatrix` |
        :class:`~neotiles.matrixes.NTRGBMatrix`) The matrix being managed.
    :param draw_fps: (int|None) The frame rate for the drawing animation loop.
    """
    def __init__(self, matrix, draw_fps=10):
        self.hardware_matrix = matrix
        self._draw_fps = draw_fps

        self._animation_thread = None
        self._pixels = None
        self._clear_pixels()

        # List of tiles we'll be displaying inside the matrix.
        self._managed_tiles = []

    def __repr__(self):
        return '{}(matrix={}, draw_fps={})'.format(
            self.__class__.__name__,
            repr(self.hardware_matrix),
            self._draw_fps
        )

    def __str__(self):
        matrix = self.pixels

        matrix_string = ''
        pixel_num = 0

        # Do a scan to see if any pixels have a white component.  If any do
        # then we'll display the white component for all of them; otherwise
        # we'll suppress it in the interest of space.
        display_white = False
        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]
                if color.white is not None:
                    display_white = True

        # Display a 2-dimensional grid of pixel values.
        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]
                denormalized = color.hardware_components

                if len(denormalized) == 3 and display_white:
                    display_components = denormalized + 0
                else:
                    display_components = denormalized

                if display_white:
                    matrix_string += (
                        '[{:2d}] {:-3d},{:-3d},{:-3d},{:-3d}  '.format(
                            pixel_num, *display_components)
                    )
                else:
                    matrix_string += '[{:2d}] {:-3d},{:-3d},{:-3d}  '.format(
                        pixel_num, *display_components)

                pixel_num += 1

            matrix_string += '\n'

        return matrix_string.rstrip()

    def _clear_pixels(self):
        """
        Generate a 2D matrix for the given size of the neopixel matrix where
        all the pixels are set to off (0, 0, 0).

        :return: ([[:class:`PixelColor`]]) 2D matrix of PixelColor objects all
            set to (0, 0, 0, 0).
        """
        self._pixels = [
            [PixelColor(0, 0, 0, 0) for col in range(self.matrix_size.cols)]
            for row in range(self.matrix_size.rows)
        ]

    @wrapt.synchronized
    def _set_pixels_from_tiles(self):
        """
        Create a 2D matrix representing the entire pixel matrix, made up of
        each of the individual tiles' colors for each tile pixel.

        :return: ([[matrix]]) 2D list of :class:`PixelColor` objects.
        :raises: :class:`NeoTilesError` if an attempt is made to render a
            pixel outside of the neopixel matrix's dimensions.
        """
        self._clear_pixels()

        # Set the matrix pixels to the colors of each tile in turn.  If any
        # tiles happen to overlap then the last one processed will win.
        for managed_tile in self._managed_tiles:
            tile_object = managed_tile['tile_object']
            if not tile_object.visible:
                continue

            # Call the draw() method of any tile which is flagged as animating.
            if tile_object.animate:
                tile_object.draw()

            # Retrieve the pixel colors of the tile.
            tile_matrix = tile_object.pixels

            # Draw the tile's pixels in the right place on the matrix
            # (determined by the tile's root position).
            for tile_row_num in range(len(tile_matrix)):
                for tile_col_num in range(len(tile_matrix[tile_row_num])):
                    pixel_color = tile_matrix[tile_row_num][tile_col_num]
                    matrix_row = managed_tile['root'].y + tile_row_num
                    matrix_col = managed_tile['root'].x + tile_col_num

                    try:
                        self._pixels[matrix_row][matrix_col] = pixel_color
                    except IndexError:
                        raise NeoTilesError(
                            'Cannot render tile {}: pixel position ({}, {}) '
                            'is invalid for {}x{} matrix'.format(
                                managed_tile, matrix_col, matrix_row,
                                self.matrix_size.cols, self.matrix_size.rows
                            ))

    @wrapt.synchronized
    def _draw_hardware_matrix(self):
        """
        Displays the current state of the matrix pixels on the neopixel
        hardware.
        """
        pixels = self.pixels

        # Walk through the matrix from the top left to the bottom right,
        # painting pixels as we go.
        for row_num in range(len(pixels)):
            for col_num in range(len(pixels[row_num])):
                color = pixels[row_num][col_num]
                self.hardware_matrix.setPixelColor(col_num, row_num, color)

        self.hardware_matrix.show()

    def _animate(self):
        """
        Internal animation method.  Spawns a new thread to manage the drawing
        of the matrix at the (hoped-for) frame rate.
        """
        frame_delay_millis = int(1000 / self._draw_fps)
        current_time = int(round(time.time() * 1000))
        next_frame_time = current_time + frame_delay_millis

        # Draw the first frame.  Not really necessary except perhaps for super
        # slow frame rates.
        self._set_pixels_from_tiles()
        self._draw_hardware_matrix()

        while True:
            current_time = int(round(time.time() * 1000))
            if current_time > next_frame_time:
                next_frame_time = current_time + frame_delay_millis
                self._set_pixels_from_tiles()
                self._draw_hardware_matrix()

            # The sleep time needs to be long enough that we're not churning
            # through CPU cycles checking whether it's time to render the next
            # frame or not; but short enough to allow us to render the next
            # frame as soon as possible once we're past our next-frame wait
            # time.  This is a bit of a cheap-and-cheerful animation loop, and
            # this sleep duration may not be ideal.
            time.sleep(0.005)

            if self._animation_thread.stopped():
                return

    def register_tile(
            self, tile, size=None, root=None):
        """
        Registers a tile with the TileManager.  Registering a tile allows
        its pixels to be drawn by the TileManager to the hardware matrix.

        :param tile: (:class:`Tile`) The tile to register.
        :param size: (:class:`TileSize`) Size of the tile (in cols and rows).
        :param root: (:class:`TilePosition`) Position of the top left corner
            of the tile within the hardware matrix.
        """
        tile.size = TileSize(*size)

        self._managed_tiles.append({
            'root': TilePosition(*root),
            'tile_object': tile,
        })

        # Set the tile manager's pixels based on this new tile.  A future
        # optimization would be to only render the new tile onto the manager's
        # pixels.
        self._set_pixels_from_tiles()

    def deregister_tile(self, tile):
        """
        Deregisters a tile from the tile manager.  Deregistered tiles will
        no longer be drawn to the hardware matrix.

        If deregistering the tile results in no tiles being registered with
        the manager then the matrix-drawing animation loop will be stopped
        automatically.

        :param tile: (:class:`Tile`) The tile being deregistered.
        :return: (int) The number of tiles removed.
        """
        removed = 0

        for i, managed_tile in enumerate(self._managed_tiles):
            if managed_tile['tile_object'] == tile:
                del self._managed_tiles[i]
                removed += 1

        if len(self._managed_tiles) == 0:
            self.draw_stop()

        return removed

    def send_data_to_tiles(self, data):
        """
        Sends ``data`` to all registered tiles.  The data will not be sent to
        any tile which has its :attr:`Tile.is_accepting_data` attribute set to
        ``False``.

        :param data: (any) Input data.
        """
        for managed_tile in self._managed_tiles:
            tile_object = managed_tile['tile_object']

            if tile_object.is_accepting_data:
                tile_object.data = data

    def draw_hardware_matrix(self):
        """
        Calls each tile's :meth:`Tile.draw` method to ensure that each tile's
        pixels are up to date, with the result being displayed on the hardware
        matrix.

        If the TileManager's ``draw_fps`` is not ``None`` then this method will
        also trigger the animation loop if it's not already running.  This
        means that you only need to call ``draw_hardware_matrix`` once if
        you've enabled animation, as the animation loop will ensure that the
        matrix is updated via each tile's :meth:`Tile.draw` method once per
        animation frame.
        """
        if self._draw_fps is None:
            self._set_pixels_from_tiles()
            self._draw_hardware_matrix()
            return

        if self._animation_thread is None:
            self._animation_thread = StoppableThread(target=self._animate)
            self._animation_thread.start()

    def draw_stop(self):
        """
        Stop the matrix-drawing animation loop.
        """
        if self._animation_thread is not None:
            self._animation_thread.stop()
            self._animation_thread.join()
            self._animation_thread = None

    def clear_hardware_matrix(self):
        """
        Clears the hardware matrix (sets all pixels to
        ``PixelColor(0, 0, 0, 0)``).
        """
        pixels = self.pixels
        black_pixel = PixelColor(0, 0, 0)

        for row_num in range(len(pixels)):
            for col_num in range(len(pixels[row_num])):
                self.hardware_matrix.setPixelColor(
                    col_num, row_num, black_pixel)

        self.hardware_matrix.show()

    @property
    def brightness(self):
        """
        (int) Get or set the brightness of the matrix display.  Range of
            acceptable values will depend on the matrix type.
        """
        return self.hardware_matrix.brightness

    @brightness.setter
    def brightness(self, val):
        self.hardware_matrix.brightness = val

    @property
    def matrix_size(self):
        """
        (:class:`MatrixSize`) Get the size of the matrix.
        """
        return self.hardware_matrix.size

    @property
    def tiles(self):
        """
        Get all registered tiles as a list of :class:`Tile` objects.
        """
        return [tile['tile_object'] for tile in self._managed_tiles]

    @property
    def tiles_meta(self):
        """
        Get all information on all registered tiles.

        Tile information is returned as a list of dictionaries which contain
        the ``root`` and ``tile_object`` keys (:class:`TilePosition` and
        :class:`Tile` objects respectively).

        If you just want the registered Tile instances then use :attr:`tiles`
        instead.
        """
        return self._managed_tiles

    @property
    def pixels(self):
        """
        Get the tile manager's current pixel colors, which is a combination of
        the current pixel colors of all the tiles being managed by the
        TileManager.

        The colors are returned as a two-dimensional list (with the same
        dimensions as :attr:`matrix_size`) of :class:`~PixelColor` objects.
        """
        return self._pixels
