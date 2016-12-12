from collections import namedtuple

from neopixel import Adafruit_NeoPixel, Color, ws

from .tilecolor import TileColor


TilePosition = namedtuple('TilePosition', 'x y')
TileSize = namedtuple('TileSize', 'cols rows')


class NeoTiles:
    """
    Manages all the tiles being displayed in a neopixel matrix.

    Example usage (an 8x2 tile on top of an 8x6 tile): ::

        from neotiles import NeoTiles, TileHandler

        tiles = NeoTiles(size=(8, 8))

        tiles.register_tile(
            size=(8, 2), root=(0, 0), handler=TileHandler())
        tiles.register_tile(
            size=(8, 6), root=(2, 0), handler=TileHandler())

        # Display the pixel values on the neopixel matrix.
        tiles.draw()

        # Display the pixel values in the console.
        print(tiles)

    :param size: (:class:`TileSize`) Size (as the number of columns and rows)
        of the neopixel matrix.
    :param intensity: (float) Intensity of the matrix display.  0.5 will
        display all pixels at half intensity of whatever the tile handlers
        are setting each pixel to.
    """
    def __init__(self, size=None, intensity=1.0):
        if size is None:
            raise ValueError('size must be specified')

        self._size = TileSize(*size)
        self._intensity = intensity
        self._led_count = self._size.cols * self._size.rows

        # List of tiles we'll be displaying inside the matrix.
        self._tiles = []

        # Initialize the matrix.
        # TODO: Make these accessible from constructor.
        led_pin = 18
        led_freq_hz = 800000
        led_dma = 5
        led_brightness = 8
        led_invert = False
        strip_type = ws.WS2811_STRIP_GRB

        self.hardware_matrix = Adafruit_NeoPixel(
            self._led_count, led_pin, freq_hz=led_freq_hz, dma=led_dma,
            invert=led_invert, brightness=led_brightness, strip_type=strip_type
        )

        self.hardware_matrix.begin()

    def __repr__(self):
        return '<{}(size=({}, {}))>'.format(
            self.__class__.__name__, self._size.cols, self._size.rows)

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
        return tuple([int(i * self.intensity) for i in color.rgbw_denormalized])

    def _genenerate_empty_matrix(self):
        matrix = [
            [TileColor(0, 0, 0) for col in range(self._size.cols)]
            for row in range(self._size.rows)
        ]

        return matrix

    def _generate_matrix(self):
        """
        Create a 2D matrix representing the entire pixel matrix, made up of
        each of the individual tiles.

        :return: ()
        """
        matrix = self._genenerate_empty_matrix()

        # Set the matrix pixels to the colors of each tile in turn.  If any
        # tiles happen to overlap then the last one processed will win.
        for tile in self._tiles:
            tile_matrix = tile['handler'].pixels
            for tile_row_num in range(len(tile_matrix)):
                for tile_col_num in range(len(tile_matrix[tile_row_num])):
                    pixel_color = tile_matrix[tile_row_num][tile_col_num]
                    matrix_row = tile['root'].y + tile_row_num
                    matrix_col = tile['root'].x + tile_col_num
                    matrix[matrix_row][matrix_col] = pixel_color

        return matrix

    @property
    def intensity(self):
        """
        The intensity (between 0 and 1) of the matrix display.  Read/write.
        """
        return self._intensity

    @intensity.setter
    def intensity(self, val):
        try:
            if val >= 0.0 and val <= 1.0:
                self._intensity = val
        except TypeError:
            pass

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
        """
        return [tile['handler'] for tile in self._tiles]

    def register_tile(self, size=None, root=None, handler=None):
        """
        Registers a tile.

        :param size: (:class:`TileSize`) Size of the tile (in cols and rows).
        :param root: (:class:`TilePosition`) Position of the top left corner
            of the tile within the neopixel matrix.
        :param handler: (:class:`TileHandler`) Handles the tile behavior.
        """
        # TODO: Consider making _tiles an ordered dict; or a different
        #   structure that allows for removal and insertion.
        handler.size = TileSize(*size)
        handler.clear()

        self._tiles.append({
            'size': handler.size,
            'root': TilePosition(*root),
            'handler': handler,
        })

    def data(self, in_data):
        """
        Takes the ``in_data`` and sends it to all the registered tiles.

        All tiles which receive the incoming data are expected to set their
        pixel colors appropriately.

        :param in_data: (any) Input data.
        """
        for tile in self._tiles:
            tile.handler.data(in_data)

    def draw(self):
        """
        Displays the current pixel values of all tiles on the neopixel matrix.
        """
        matrix = self._generate_matrix()

        # Walk through the matrix from the top left to the bottom right,
        # painting pixels as we go.
        pixel_num = 0
        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]
                self.hardware_matrix.setPixelColorRGB(
                    pixel_num, *self._display_color(color))
                pixel_num += 1

        self.hardware_matrix.show()

    def clear(self, show=True):
        """
        Clears the matrix (sets all pixels to ``TileColor(0, 0, 0, 0)``).

        :param show: (bool) Whether to draw the cleared pixels to the
            neopixel matrix.
        """
        for pixel_num in range(self._led_count):
            self.hardware_matrix.setPixelColor(pixel_num, 0)

        if show:
            self.hardware_matrix.show()

