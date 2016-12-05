import logging
import random


# ----------------------------------------------------------------------------
class NeoTiles:
    def __init__(self, size=None):
        self._size = size
        self._tiles = []

    def register_tile(self, size=None, root=None, handler=None):
        handler.size = size

        self._tiles.append({
            'size': size,
            'root': root,
            'handler': handler,
        })

    @property
    def tiles(self):
        return self._tiles

    @property
    def tile_handlers(self):
        return [tile['handler'] for tile in self._tiles]

    def data(self, in_data):
        for tile in self._tiles:
            tile.handler.data(in_data)

    def draw(self):
        # Create a 2D matrix representing the entire pixel matrix, made up of
        # each of the individual tiles.

        # Init the matrix to black.
        matrix = [[(0, 0, 0) for col in range(self._size[0])]
                  for row in range(self._size[1])]

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

        # Walk through the matrix from the top left to the bottom right,
        # painting pixels as we go.
        pixel_num = 0
        for row_num in range(len(matrix)):
            for col_num in range(len(matrix[row_num])):
                color = matrix[row_num][col_num]
                print('[{:2d}] : {:7.3f}, {:7.3f}, {:7.3f}  '.format(
                    pixel_num, color[0], color[1], color[2]), end='')
                pixel_num += 1

            print()


# ----------------------------------------------------------------------------
class TileHandler:
    # TODO: replace size getter with num_cols and num_rows
    def __init__(self, size=None):
        self._data = None
        self._default_color = (
            random.random(), random.random(), random.random())

        # Set tile size as a tuple of (cols, rows)
        if size is None:
            self._size = (1, 1)
        else:
            self.size = size

        self._pixels = [[]]
        self._init_pixels()

    def _init_pixels(self):
        # A two-dimension array of pixel colors for the tile.
        self._pixels = [
            [self._default_color for col in range(self._size[0])]
            for row in range(self._size[1])
        ]

    def data(self, in_data):
        self._data = in_data

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if not type(value) is tuple or len(value) != 2:
            raise ValueError('size must be a tuple of (cols, rows)')

        self._size = value
        self._init_pixels()

    def set_pixel(self, pos, color):
        if not type(pos) is tuple or len(pos) != 2:
            raise ValueError('pos must be a tuple of (col, row)')

        # pos[0] is the column index and pos[1] is the row index.  Our pixel
        # matrix is indexed by row number first, then column within the row.
        self._pixels[pos[1]][pos[0]] = color

    @property
    def pixels(self):
        return self._pixels


# ----------------------------------------------------------------------------
class PacketCountHandler(TileHandler):
    def __init__(self, protocol='TCP'):
        super().__init__()
        self._protocol = protocol

    def data(self, in_data):
        packet_count = 0

        try:
            packet_count = in_data['payload']['packet_counts'][self._protocol]
        except KeyError as e:
            logging.warning('protocol {} not found in data: {}'.format(
                self._protocol, e))
            return


if __name__ == '__main__':
    #tcp_packets = PacketCountHandler(protocol='TCP')
    #udp_packets = PacketCountHandler(protocol='UDP')
    tcp_packets = TileHandler()
    udp_packets = TileHandler()

    tiles = NeoTiles(size=(3, 7))

    tiles.register_tile(size=(2, 7), root=(0, 0), handler=tcp_packets)
    tiles.register_tile(size=(1, 7), root=(2, 0), handler=udp_packets)

    tiles.draw()
