.. automodule:: neotiles

API
===

The following classes are exposed by the API.  Note that methods and properties
which expect a :class:`~TilePosition` or :class:`~TileSize` as input will
also accept a plain tuple as input so long as the element order is the same.

* :class:`~NeoTiles` - Manages all the tiles in a neopixel matrix.
* :class:`~TileHandler` - Manages a single tile.
* :class:`~TileColor` - Color of a pixel.
* :class:`~TilePosition` - Position of a tile.
* :class:`~TileSize` - Size of a tile (in cols and rows).

Example usage (an 8x2 tile on top of an 8x6 tile): ::

    from neotiles import NeoTiles, TileHandler

    tiles = NeoTiles(size=(8, 8))

    tiles.register_tile(size=(8, 2), root=(0, 0), handler=TileHandler())
    tiles.register_tile(size=(8, 6), root=(2, 0), handler=TileHandler())

    # Display the pixel colors on the neopixel matrix.
    tiles.draw()

    # Display the pixel color values in the console.
    print(tiles)

NeoTiles
--------

.. autoclass:: NeoTiles
   :members:

TileHandler
-----------

.. autoclass:: TileHandler
   :members:

TileColor
---------

.. autoclass:: TileColor
   :members:

TilePosition
------------

.. autoclass:: TilePosition
   :members:

TileSize
--------

.. autoclass:: TileSize
   :members:
