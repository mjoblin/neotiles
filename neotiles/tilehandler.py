import random


class TileHandler:
    # TODO: replace size getter with num_cols and num_rows
    """

    :param size:
    """
    def __init__(self, size=None):
        self._data = None
        self._default_color = (
            random.random(), random.random(), random.random())

        # Set tile size as a tuple of (cols, rows)
        if size is None:
            self._size = (1, 1)
        else:
            self.size = size

        self._init_pixels()

    def _init_pixels(self, color=None):
        # A two-dimension array of pixel colors for the tile.
        display_color = self._default_color if color is None else color

        self._pixels = [
            [display_color for col in range(self._size[0])]
            for row in range(self._size[1])
        ]

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if not type(value) is tuple or len(value) != 2:
            raise ValueError('size must be a tuple of (cols, rows)')

        self._size = value
        self._init_pixels()

    @property
    def pixels(self):
        return self._pixels

    def data(self, in_data):
        self._data = in_data

    def clear(self):
        self._init_pixels(color=(0, 0, 0))

    def set_pixel(self, pos, color):
        if not type(pos) is tuple or len(pos) != 2:
            raise ValueError('pos must be a tuple of (col, row)')

        # pos[0] is the column index and pos[1] is the row index.  Our pixel
        # matrix is indexed by row number first, then column within the row.
        self._pixels[pos[1]][pos[0]] = color

