.. automodule:: neotiles

API
===

The following classes are exposed by the API.  Note that methods and properties
which expect a :class:`~TilePosition`, :class:`~TileSize`, or
:class:`~PixelPosition` as input will also accept a plain tuple as input so
long as the element order is the same.

Main classes:

* :class:`TileManager` - Manages all the tiles being displayed on a neopixel matrix.
* :class:`Tile` - Handles the data and pixel-coloring needs of a single tile.
* :class:`PixelColor` - The color of a single neopixel.

Supporting classes:

* :class:`TilePosition` - The position of a tile inside the larger hardware neopixel matrix.
* :class:`TileSize` - The size of a tile (cols, rows).
* :class:`PixelPosition` - The position of a neopixel inside a tile (x, y).
* :class:`exceptions.NeoTilesError` - Exception raised when neotiles encounters a problem.

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

Supporting classes
------------------

The following supporting classes can be useful but you don't need to use them.

TilePosition
^^^^^^^^^^^^

.. autoclass:: TilePosition
   :members:

TileSize
^^^^^^^^

.. autoclass:: TileSize
   :members:

PixelPosition
^^^^^^^^^^^^^

.. autoclass:: PixelPosition
   :members:

neotiles.NeoTilesError
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: neotiles.exceptions.NeoTilesError
   :members:

Development
-----------

Development is best done in a virtualenv: ::

   virtualenv neotiles --python=python3.4
   source neotiles/bin/activate

Then from the project directory, install the development dependencies: ::

   pip install .[dev]

Run unit tests (will only work in an environment with the Adafruit neopixel
library installed): ::

   pytest

Check PEP8 linting: ::

   flake8

Generate documentation: ::

   cd docs
   make html

The documentation can then be found in ``docs/_build/html/index.html``.
