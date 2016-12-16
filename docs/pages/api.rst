.. automodule:: neotiles

API
===

The following classes are exposed by the API.  Note that methods and properties
which expect a :class:`~TilePosition` or :class:`~TileSize` as input will
also accept a plain tuple as input so long as the element order is the same.

* :class:`~TileManager` - Manages all the tiles being displayed on a neopixel matrix.
* :class:`~TileHandler` - Handles the data and pixel-coloring needs of a single tile.
* :class:`~TilePosition` - The position of a tile inside the larger neopixel matrix.
* :class:`~TileSize` - The size of a tile (in cols and rows).
* :class:`~NPColor` - The color of a single neopixel.

TileManager
-----------

.. autoclass:: TileManager
   :members:

TileHandler
-----------

.. autoclass:: TileHandler
   :members:

TilePosition
------------

.. autoclass:: TilePosition
   :members:

TileSize
--------

.. autoclass:: TileSize
   :members:

NPColor
-------

.. autoclass:: NPColor
   :members:

