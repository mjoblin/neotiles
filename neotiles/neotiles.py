from collections import namedtuple

from neopixel import Adafruit_NeoPixel, Color, ws


Pos = namedtuple('Pos', 'x y')
Size = namedtuple('Size', 'cols rows')


class NeoTiles:
    """

    :param size:
    """
    def __init__(self, size=None, max_intensity=255):
        self._size = size
        self._max_intensity = max_intensity
        self._led_count = size[0] * size[1]

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
            self.__class__.__name__, self._size[0], self._size[1])

    def __str__(self):
        matrix = self._generate_matrix()

        matrix_string = ''
        pixel_num = 0

        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]
                matrix_string += '[{:2d}] {:3.0f},{:3.0f},{:3.0f}  '.format(
                    pixel_num, *self._normalized_to_display_color(color))
                pixel_num += 1

            matrix_string += '\n'

        return matrix_string.rstrip()

    @property
    def tiles(self):
        return self._tiles

    @property
    def tile_handlers(self):
        return [tile['handler'] for tile in self._tiles]

    def _normalized_to_display_color(self, normalized):
        return tuple([int(i * self._max_intensity) for i in normalized])

    def _genenerate_black_matrix(self):
        # TODO: rethink this vs. the clear() method
        matrix = [[(0, 0, 0) for col in range(self._size[0])]
                  for row in range(self._size[1])]

        return matrix

    def _generate_matrix(self):
        """
        Create a 2D matrix representing the entire pixel matrix, made up of
        each of the individual tiles.

        :return:
        """
        matrix = self._genenerate_black_matrix()

        # Set the matrix pixels to the colors of each tile in turn.  If any
        # tiles happen to overlap then the last one processed will win.
        for tile in self._tiles:
            tile_matrix = tile['handler'].pixels
            for tile_row_num in range(len(tile_matrix)):
                for tile_col_num in range(len(tile_matrix[tile_row_num])):
                    pixel_color = tile_matrix[tile_row_num][tile_col_num]
                    matrix_row = tile['root'][1] + tile_row_num
                    matrix_col = tile['root'][0] + tile_col_num
                    matrix[matrix_row][matrix_col] = pixel_color

        return matrix

    def register_tile(self, size=None, root=None, handler=None):
        """

        :param size:
        :param root:
        :param handler:
        :return:
        """
        # TODO: Consider making _tiles an ordered dict; or a different
        #   structure that allows for removal and insertion.
        handler.size = size

        self._tiles.append({
            'size': size,
            'root': root,
            'handler': handler,
        })

    def data(self, in_data):
        """

        :param in_data:
        :return:
        """
        for tile in self._tiles:
            tile.handler.data(in_data)

    def draw(self):
        """

        :return:
        """
        matrix = self._generate_matrix()

        # Walk through the matrix from the top left to the bottom right,
        # painting pixels as we go.
        pixel_num = 0
        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]

                color_display = self._normalized_to_display_color(color)
                print('{:-2d}: {:.3f} {:.3f} {:.3f} -> {:-3d} {:-3d} {:-3d}'.format(
                    pixel_num,
                    color[0], color[1], color[2],
                    color_display[0], color_display[1], color_display[2]
                ))

                #self.hardware_matrix.setPixelColorRGB(
                #    pixel_num, *self._normalized_to_display_color(color))
                self.hardware_matrix.setPixelColorRGB(
                    pixel_num, color_display[0], color_display[1], color_display[2])
                pixel_num += 1

        print()
        self.hardware_matrix.show()

    def clear(self):
        """

        :return:
        """
        for pixel_num in range(self._led_count):
            self.hardware_matrix.setPixelColor(pixel_num, 0)

        self.hardware_matrix.show()

