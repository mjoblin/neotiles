from collections import namedtuple
import threading
import time

from neopixel import Adafruit_NeoPixel, ws

from .exceptions import NeoTilesError
from .pixelcolor import PixelColor


TilePosition = namedtuple('TilePosition', 'x y')
TileSize = namedtuple('TileSize', 'cols rows')
PixelPosition = namedtuple('PixelPosition', 'x y')

# TODO: Consider moving animate() to animate=True on constructor
# TODO: Quietly ignore pixels outside the matrix boundary?  (Might allow for
#   animation of the tiles themselves).
# TODO: Change getter/setter docs.
# TODO: Check other docs for completeness.


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
    Manages all the tiles displayed in a neopixel matrix.

    You must specify a ``size`` (e.g. ``(8, 8)``) and ``led_pin`` (e.g.
    ``18``).  The other parameters can usually be left at their defaults.  For
    more information on the other parameters look at the ``Adafruit_NeoPixel``
    class in the ``neopixel`` module.

    If your RGB values appear to be mixed up (for example, red is showing as
    green) then try using a different ``strip_type``.  You can see a list of
    valid strip type constants here (look for ``_STRIP_`` in the constant
    name): https://docs.rs/ws281x/0.1.0/ws281x/ffi/index.html

    Specify a strip type like this: ``strip_type=ws.WS2811_STRIP_GRB``.  For
    this to work you'll need to ``import ws`` (which comes with the
    ``neopixel`` module) into your code.

    **Animation**:

    The ``draw_fps`` (draw frames per second) parameter controls how many times
    per second the animation loop (which runs in a separate thread) will call
    :meth:`draw_matrix`.  If ``draw_fps=None`` then the matrix will not be
    drawn automatically and you must call :meth:`draw_matrix` manually.

    The animation loop will attempt to re-draw the matrix at a rate of
    ``draw_fps`` times per second.  This rate may or may not be achieved
    depending on what else the CPU is doing, including the compute load created
    by the tile handlers' :meth:`TileHandler.data` methods.

    The animation loop assumes that something else will be sending data to the
    tile handlers (via the :meth:`TileHandler.data` or :meth:`TileManager.data`
    methods), which are then updating their tile's pixel colors.  If that isn't
    happening then the animation loop will likely keep re-drawing the matrix
    with the same pixel colors.

    :param size: (:class:`TileSize`) Size (in cols and rows) of the neopixel
        matrix.
    :param led_pin: (int) The pin you're using to talk to your neopixel matrix.
    :param draw_fps: (int) The frame rate for the drawing animation loop.
    :param led_freq_hz: (int) LED frequency.
    :param led_dma: (int) LED DMA.
    :param led_brightness: (int) Brightness of the matrix display (0-255).
    :param led_invert: (bool) Whether to invert the LEDs.
    :param strip_type: (int) Neopixel strip type.
    :raises: :class:`exceptions.NeoTilesError` if ``size`` or ``led_pin`` are
        not specified.
    """
    def __init__(
            self, size=None, led_pin=None, draw_fps=None, led_freq_hz=800000,
            led_dma=5, led_brightness=16, led_invert=False,
            strip_type=ws.WS2811_STRIP_GRB):

        if size is None or led_pin is None:
            raise NeoTilesError('size and led_pin must be specified')

        self.size = TileSize(*size)
        self._led_pin = led_pin
        self._draw_fps = draw_fps
        self._led_freq_hz = led_freq_hz
        self._led_dma = led_dma
        self._led_brightness = led_brightness
        self._led_invert = led_invert
        self._strip_type = strip_type

        self._led_count = self.size.cols * self.size.rows
        self._animation_thread = None

        # List of tiles we'll be displaying inside the matrix.
        self._tiles = []

        # Initialize the matrix.
        self.hardware_matrix = Adafruit_NeoPixel(
            self._led_count, self._led_pin, freq_hz=self._led_freq_hz,
            dma=self._led_dma, invert=self._led_invert,
            brightness=self._led_brightness, strip_type=self._strip_type
        )

        self.hardware_matrix.begin()

    def __repr__(self):
        strip_name = self._strip_type

        # Convert strip name from strip type integer to associated attribute
        # name from ws module (if we can find it).
        for strip_check in [attr for attr in dir(ws) if '_STRIP_' in attr]:
            if getattr(ws, strip_check) == self._strip_type:
                strip_name = 'ws.{}'.format(strip_check)

        return (
            '{}(size={}, led_pin={}, led_freq_hz={}, led_dma={}, '
            'led_brightness={}, led_invert={}, strip_type={})'
        ).format(
            self.__class__.__name__, self.size, self._led_pin,
            self._led_freq_hz, self._led_dma, self._led_brightness,
            self._led_invert, strip_name
        )

    def __str__(self):
        matrix = self._generate_matrix()

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

    def _generate_empty_matrix(self):
        """
        Generate a 2D matrix for the given size of the neopixel matrix where
        all the pixels are set to off (0, 0, 0).

        :return: ([[:class:`PixelColor`]]) 2D matrix of PixelColor objects all
            set to (0, 0, 0, 0).
        """
        matrix = [
            [PixelColor(0, 0, 0, 0) for col in range(self.size.cols)]
            for row in range(self.size.rows)
        ]

        return matrix

    def _generate_matrix(self):
        """
        Create a 2D matrix representing the entire pixel matrix, made up of
        each of the individual tiles' colors for each tile pixel.

        :return: ([[matrix]]) 2D list of :class:`PixelColor` objects.
        :raises: :class:`NeoTilesError` if an attempt is made to render a
            pixel outside of the neopixel matrix's dimensions.
        """
        matrix = self._generate_empty_matrix()

        # Set the matrix pixels to the colors of each tile in turn.  If any
        # tiles happen to overlap then the last one processed will win.
        for tile in self._tiles:
            tile_matrix = tile['handler'].pixels
            for tile_row_num in range(len(tile_matrix)):
                for tile_col_num in range(len(tile_matrix[tile_row_num])):
                    pixel_color = tile_matrix[tile_row_num][tile_col_num]
                    matrix_row = tile['root'].y + tile_row_num
                    matrix_col = tile['root'].x + tile_col_num

                    try:
                        matrix[matrix_row][matrix_col] = pixel_color
                    except IndexError:
                        raise NeoTilesError(
                            'Cannot render tile {}: pixel position ({}, {}) '
                            'is invalid for {}x{} matrix'.format(
                                tile, matrix_col, matrix_row, self.size.cols,
                                self.size.rows
                            ))
        return matrix

    def _draw_matrix(self):
        """
        Retrieves the current pixel colors of all registered tiles and displays
        them on the neopixel matrix.

        :raises: :class:`NeoTilesError` if an attempt is made to render a
            pixel outside of the neopixel matrix's dimensions.
        """
        matrix = self._generate_matrix()

        # Walk through the matrix from the top left to the bottom right,
        # painting pixels as we go.
        pixel_num = 0
        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]
                self.hardware_matrix.setPixelColor(
                    pixel_num, color.hardware_int)
                pixel_num += 1

        self.hardware_matrix.show()

    def _animate(self):
        """
        Internal animation method.  Spawns a new thread to manage the drawing
        of the matrix at the (hoped-for) frame rate.
        """
        frame_delay_millis = int(1000 / self._draw_fps)
        current_time = int(round(time.time() * 1000))
        next_frame_time = current_time + frame_delay_millis
        self._draw_matrix()

        while True:
            current_time = int(round(time.time() * 1000))
            if current_time > next_frame_time:
                next_frame_time = current_time + frame_delay_millis
                self._draw_matrix()

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
            self, size=None, root=None, handler=None, draw_matrix=False):
        """
        Registers a tile with the tile manager.

        :param size: (:class:`TileSize`) Size of the tile (in cols and rows).
        :param root: (:class:`TilePosition`) Position of the top left corner
            of the tile within the neopixel matrix.
        :param draw_matrix: (bool) Whether to draw the matrix after registering
            the tile.
        :param handler: (:class:`TileHandler`) Handles the tile behavior.
        """
        handler.size = TileSize(*size)

        self._tiles.append({
            'size': handler.size,
            'root': TilePosition(*root),
            'handler': handler,
        })

        if draw_matrix:
            self.draw_matrix()

    def deregister_tile(self, handler, draw_matrix=False):
        """
        Deregisters a tile from the tile manager.

        If deregistering the tile results in no tiles being registered with
        the manager, then the matrix-drawing animation loop will be stopped
        automatically.

        :param handler: (:class:`TileHandler`) The handler associated with the
            tile being deregistered.
        :param draw_matrix: (bool) Whether to draw the matrix after
            deregistering the tile.
        :return: (int) The number of handlers removed.
        """
        removed = 0

        for i, tile in enumerate(self._tiles):
            if tile['handler'] == handler:
                del self._tiles[i]
                removed += 1

        if draw_matrix:
            self.draw_matrix()

        if len(self._tiles) == 0:
            self.draw_stop()

        return removed

    def data(self, in_data):
        """
        Takes ``in_data`` and sends it to all the registered tiles.

        All tiles which receive the incoming data are expected to set their
        own pixel colors based on the data contents.

        :param in_data: (any) Input data.
        """
        for tile in self._tiles:
            tile['handler'].data(in_data)

    def draw_matrix(self):
        """
        Draw the matrix.

        If the ``draw_fps`` attribute (set at TileManager instantiation) is
        not ``None`` then this method will also trigger the animation loop (if
        it's not already running).
        """
        if self._draw_fps is None:
            self._draw_matrix()
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

    def clear(self, draw_matrix=True):
        """
        Clears the neopixel matrix (sets all pixels to
        ``PixelColor(0, 0, 0, 0)``).

        :param draw_matrix: (bool) Whether to draw the cleared pixels to the
            neopixel matrix.
        """
        for pixel_num in range(self._led_count):
            self.hardware_matrix.setPixelColor(pixel_num, 0)

        if draw_matrix:
            self.hardware_matrix.show()

    @property
    def brightness(self):
        """
        The brightness (between 0 and 255) of the matrix display.  Read/write.

        :raises: ``ValueError`` if an attempt is made to set a brightness
            outside of 0 and 255.
        """
        return self._led_brightness

    @brightness.setter
    def brightness(self, val):
        error_msg = 'Brightness must be between 0 and 255'

        try:
            if val >= 0 and val <= 255:
                self._led_brightness = val
                self.hardware_matrix.setBrightness(self._led_brightness)
            else:
                raise ValueError(error_msg)
        except TypeError:
            raise ValueError(error_msg)

    @property
    def tiles(self):
        """
        All registered tiles.  Read only.  Returned as a list of dictionaries
        which contain the ``size``, ``root``, and ``handler`` keys
        (:class:`TileSize`, :class:`TilePosition`, and :class:`TileHandler`
        objects respectively).
        """
        return self._tiles

    @property
    def tile_handlers(self):
        """
        All registered tile handlers.  Read only.

        :return: ([:class:`TileHandler`, ...]) Registered tile handlers.
        """
        return [tile['handler'] for tile in self._tiles]

    @property
    def pixels(self):
        """
        A two-dimensional list which contains the color of each neopixel in the
        matrix.
        """
        return self._generate_matrix()
