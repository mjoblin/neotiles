.. automodule:: neotiles

API
===

The following classes are exposed by the API.  Note that methods and properties
which expect a :class:`~TilePosition`, :class:`~TileSize`, or
:class:`~PixelPosition` as input will also accept a plain tuple as input so
long as the element order is the same.

Main classes:

* :class:`TileManager` - Manages all the tiles being displayed on a hardware matrix.
* :class:`Tile` - Handles the data and pixel-coloring needs of a single tile.
* :class:`PixelColor` - The color of a single matrix pixel.
* :class:`~matrixes.NTNeoPixelMatrix` - Represents a NeoPixel matrix.
* :class:`~matrixes.NTRGBMatrix` - Represents an RGB matrix.

Supporting classes:

* :class:`MatrixSize` - The size of a hardware matrix (cols, rows).
* :class:`TileSize` - The size of a tile (cols, rows).
* :class:`TilePosition` - The position of a tile inside the larger hardware matrix (x, y).
* :class:`PixelPosition` - The position of a pixel inside a tile (x, y).
* :class:`exceptions.NeoTilesError` - Exception raised when neotiles encounters a problem.

The :doc:`/pages/examples` page shows how to use these classes.

Main classes
------------

TileManager
^^^^^^^^^^^

.. autoclass:: TileManager
   :members:

Tile
^^^^

.. autoclass:: Tile
   :members:

PixelColor
^^^^^^^^^^

.. autoclass:: PixelColor
   :members:

matrixes.NTNeoPixelMatrix
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: neotiles.matrixes.NTNeoPixelMatrix
   :members:

matrixes.NTRGBMatrix
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: neotiles.matrixes.NTRGBMatrix
   :members:

Supporting classes
------------------

The following supporting classes can be useful but you don't need to use them.

MatrixSize
^^^^^^^^^^

.. autoclass:: MatrixSize
   :members:

TileSize
^^^^^^^^

.. autoclass:: TileSize
   :members:

TilePosition
^^^^^^^^^^^^

.. autoclass:: TilePosition
   :members:

PixelPosition
^^^^^^^^^^^^^

.. autoclass:: PixelPosition
   :members:

neotiles.NeoTilesError
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: neotiles.exceptions.NeoTilesError
   :members:
