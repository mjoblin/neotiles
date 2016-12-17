from collections import namedtuple
from threading import Thread
import time

from neopixel import Adafruit_NeoPixel, Color, ws

from .exceptions import NeoTilesError
from .npcolor import NPColor


TilePosition = namedtuple('TilePosition', 'x y')
TileSize = namedtuple('TileSize', 'cols rows')
PixelPosition = namedtuple('PixelPosition', 'x y')

# TODO: Consider moving animate() to animate=True on constructor
# TODO: Support RGB and RGBW
# TODO: Check Python 2.7


class TileManager:
    """
    Manages all the tiles displayed in a neopixel matrix.

    You must specify ``size`` and ``led_pin``.  The other parameters can
    usually be left at their defaults.  For more information on the other
    parameters look at the ``Adafruit_NeoPixel`` class in the ``neopixel``
    module.

    If your RGB values appear to be mixed up (for example, red is showing as
    green) then try using a different ``strip_type``.  You can see a list of
    valid strip type constants here (look for ``_STRIP_`` in the constant name):
    https://docs.rs/ws281x/0.1.0/ws281x/ffi/index.html

    Specify a strip type like this: ``strip_type=ws.WS2811_STRIP_GRB``.  For
    this to work you'll need to ``import ws`` (which comes with the ``neopixel``
    module) into your code.

    :param size: (:class:`TileSize`) Size (in columns and rows) of the neopixel
        matrix.
    :param led_pin: (int) The pin you're using to talk to your neopixel matrix.
    :param intensity: (float) Intensity of the matrix display.  0.5 will
        display all pixels at half intensity of whatever the tile handlers
        are setting each pixel to.
    :param led_freq_hz: (int) LED frequency.
    :param led_dma: (int) LED DMA.
    :param led_brightness: (int) LED brightness.
    :param led_invert: (bool) Whether to invert the LEDs.
    :param strip_type: (int) Neopixel strip type.
    :raises: :class:`NeoTilesError` if ``size`` or ``led_pin`` are not
        specified.
    """
    def __init__(
            self, size=None, led_pin=None, intensity=1.0, led_freq_hz=800000,
            led_dma=5, led_brightness=8, led_invert=False,
            strip_type=ws.WS2811_STRIP_GRB):

        if size is None or led_pin is None:
            raise NeoTilesError('size and led_pin must be specified')

        self._size = TileSize(*size)
        self._led_pin = led_pin
        self._intensity = intensity
        self._led_freq_hz = led_freq_hz
        self._led_dma = led_dma
        self._led_brightness = led_brightness
        self._led_invert = led_invert
        self._strip_type = strip_type

        self._led_count = self._size.cols * self._size.rows
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
            '{}(size={}, led_pin={}, intensity={}, led_freq_hz={}, led_dma={}, '
            'led_brightness={}, led_invert={}, strip_type={})'
        ).format(
            self.__class__.__name__, self._size, self._led_pin, self._intensity,
            self._led_freq_hz, self._led_dma, self._led_brightness,
            self._led_invert, strip_name
        )

    def __str__(self):
        matrix = self._generate_matrix()

        matrix_string = ''
        pixel_num = 0

        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]
                matrix_string += '[{:2d}] {:-3d},{:-3d},{:-3d}  '.format(
                    pixel_num, *self._display_color(color))
                pixel_num += 1

            matrix_string += '\n'

        return matrix_string.rstrip()

    def _display_color(self, color):
        """
        Convert a pixel color coming from a tile to a color for display on the
        matrix.  This involves multiplying the color by the desired matrix
        intensity.

        :param color: (:class:`NPColor`) The pixel color from the tile.
        :return: (tuple(r, g, b)) Color values for display on the matrix.
        """
        # TODO: Allow for RGBW
        return tuple([int(i * self.intensity) for i in color.rgb_denormalized])

    def _generate_empty_matrix(self):
        """
        Generate a 2D matrix for the given size of the neopixel matrix where
        all the pixels are set to off (0, 0, 0).

        :return: ([[:class:`NPColor`]]) 2D matrix of NPColor objects all set
            to (0, 0, 0).
        """
        matrix = [
            [NPColor(0, 0, 0) for col in range(self._size.cols)]
            for row in range(self._size.rows)
        ]

        return matrix

    def _generate_matrix(self):
        """
        Create a 2D matrix representing the entire pixel matrix, made up of
        each of the individual tiles' colors for each tile pixel.

        :return: ([[matrix]]) 2D list of :class:`NPColor` objects.
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
                    except IndexError as e:
                        raise NeoTilesError(
                            'Cannot render tile {}: pixel position ({}, {}) '
                            'is invalid for {}x{} matrix'.format(
                                tile, matrix_col, matrix_row, self._size.cols,
                                self._size.rows
                            ))
        return matrix

    @property
    def intensity(self):
        """
        The intensity (between 0 and 1) of the matrix display.  Read/write.

        :raises: ``ValueError`` if an attempt is made to set an intensity
            outside of 0 and 1.
        """
        return self._intensity

    @intensity.setter
    def intensity(self, val):
        error_msg = 'Intensity must be a float between 0.0 and 1.0'

        try:
            if val >= 0.0 and val <= 1.0:
                self._intensity = val
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

    def _animate(self, max_fps=10):
        """
        Internal animation method.  Spawns a new thread to manage the drawing
        of the matrix at the (hoped-for) frame rate.

        :param max_fps: (int) The maximum frames per second.
        """
        frame_delay_millis = int(1000 / max_fps)
        current_time = int(round(time.time() * 1000))
        next_frame_time = current_time + frame_delay_millis
        self.draw()

        while True:
            current_time = int(round(time.time() * 1000))
            if current_time > next_frame_time:
                next_frame_time = current_time + frame_delay_millis
                self.draw()

            # The sleep time needs to be long enough that we're not churning
            # through CPU cycles checking whether it's time to render the next
            # frame or not; but short enough to allow us to render the next
            # frame as soon as possible once we're past our next-frame wait
            # time.  This is a bit of a cheap-and-cheerful animation loop, and
            # this sleep duration may not be ideal.
            time.sleep(0.005)

    def animate(self, max_fps=10):
        """
        Start the animation loop.

        The animation loop will attempt to re-draw the matrix at a rate of
        ``max_fps`` times per second.  This rate may or may not be achieved
        depending on what else the CPU is doing, including the compute load
        created by the tile handlers.

        The animation loop assumes that something else will be sending data to
        the tile handlers (via the :meth:`TileHandler.data` or
        :meth:`TileManager.data` methods), which are then updating their
        pixel colors.  If that isn't happening then the animation loop will
        likely keep re-drawing the matrix with the same pixel colors.

        :param max_fps: (int) The maximum frames per second.
        """
        # TODO: Add a stop_animation method.
        self._animation_thread = Thread(target=self._animate, args=(max_fps,))
        self._animation_thread.daemon = True
        self._animation_thread.start()

    def clear(self, show=True):
        """
        Clears the neopixel matrix (sets all pixels to
        ``NPColor(0, 0, 0, 0)``).

        :param show: (bool) Whether to draw the cleared pixels to the
            neopixel matrix.
        """
        for pixel_num in range(self._led_count):
            self.hardware_matrix.setPixelColor(pixel_num, 0)

        if show:
            self.hardware_matrix.show()

    def data(self, in_data):
        """
        Takes the ``in_data`` and sends it to all the registered tiles.

        All tiles which receive the incoming data are expected to set their
        own pixel colors based on the data contents.

        :param in_data: (any) Input data.
        """
        for tile in self._tiles:
            tile['handler'].data(in_data)

    def draw(self):
        """
        Retrieves the the current pixel colors of all tiles and displays them
        on the neopixel matrix.

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
                # TODO: Allow for RGBW
                self.hardware_matrix.setPixelColorRGB(
                    pixel_num, *self._display_color(color))
                pixel_num += 1

        self.hardware_matrix.show()

    def register_tile(self, size=None, root=None, handler=None, draw=False):
        """
        Registers a tile.

        :param size: (:class:`TileSize`) Size of the tile (in cols and rows).
        :param root: (:class:`TilePosition`) Position of the top left corner
            of the tile within the neopixel matrix.
        :param draw: (bool) Whether to draw the matrix after registering the
            tile.
        :param handler: (:class:`TileHandler`) Handles the tile behavior.
        """
        handler.size = TileSize(*size)

        self._tiles.append({
            'size': handler.size,
            'root': TilePosition(*root),
            'handler': handler,
        })

        if draw:
            self.draw()

    def deregister_tile(self, handler, draw=False):
        """
        Deregisters a tile.

        :param handler: (:class:`TileHandler`) The handler associated with the
            tile being deregistered.
        :param draw: (bool) Whether to draw the matrix after deregistering the
            tile.
        :return: (int) The number of handlers removed.
        """
        removed = 0

        for i, tile in enumerate(self._tiles):
            if tile['handler'] == handler:
                del self._tiles[i]
                removed += 1

        if draw:
            self.draw()

        return removed

