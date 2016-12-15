.. automodule:: neotiles

neotiles
========

A Python library which allows you to split a `neopixel matrix`_ into multiple
virtual tiles for independent rendering based on input data.

A neopixel matrix contains RGB(W) LED pixels.  Here's what one looks like:

.. image:: _static/adafruit_8x8_blank.jpg
   :width: 45 %

.. image:: _static/adafruit_8x8_color.jpg
   :width: 45 %

neotiles has been tested on a Raspberry Pi 3 with the above 8x8 neopixel RGB
matrix and Python 3.4.  It would be surprising if it worked on
micropython-based hardware.

What it does
------------

Normally you control all the pixels in a neopixel matrix via their unique pixel
number, like this:

.. image:: _static/neotiles_matrix.svg
   :width: 300
   :align: center

This works great, but can become a little unwieldy if you want to display
multiple things on your matrix at the same time; things which are based on
input data (perhaps from a few sensors), and which might be updating regularly
over time.

For example, if you wanted to display the readings from three temperature
sensors in the three blocks shown above (top-left in red, top-right in green,
and bottom in blue; with color intensity representing the sensor value) then
you'd need to take the sensor data, process it, and assign all the pixel colors
appropriately.

neotiles simplifies this by splitting your matrix into tiles.  Each tile is
given the input data, from which it can extract the piece it needs and set the
color of its own pixels as desired.

The above example can now be treated as 3 separate tiles, each with its own
mini-matrix of pixels always starting at (0, 0):

.. image:: _static/neotiles_tiles.svg
   :width: 300
   :align: center

All you need to do is:

* Create a :class:`~TileManager` object and give it the size of your matrix.
* Create your own subclass of :class:`~TileHandler` and implement the :meth:`~TileHandler.data` method, which receives incoming data and sets pixel colors appropriately.
* Register your TileHandler subclass instances with the TileManager object.
* Send data to the TileManager object.  The data can be anything in any format, so long as your TileHandlers know how to interpret it.
* Watch the neopixel matrix display the results.  Taco earned.

Example
-------

Below is a simple example which takes an 8x8 matrix and renders (without input
data or animation) three tiles inside of it: a top-left 4x4 tile (in red), a
top-right 4x4 tile (in green), and an 8x4 bottom tile (in blue): ::

    from neotiles import NeoTiles, TileColor, TileHandler

    # Initialize an 8x8 matrix.
    tiles = NeoTiles(size=(8, 8))

    # Create three tile handlers.  Handlers are told their dimensions
    # later.
    red_handler = TileHandler(default_color=TileColor(128, 0, 0))
    grn_handler = TileHandler(default_color=TileColor(0, 128, 0))
    blu_handler = TileHandler(default_color=TileColor(0, 0, 128))

    # Assign the 3 tile handlers to the matrix.  This is when the
    # tiles will be given their dimensions.
    tiles.register_tile(size=(4, 4), root=(0, 0), handler=red_handler)
    tiles.register_tile(size=(4, 4), root=(4, 0), handler=grn_handler)
    tiles.register_tile(size=(8, 4), root=(0, 4), handler=blu_handler)

    # Display each tile's pixel colors on the neopixel matrix.
    tiles.draw()

This example relies on the default TileHandler class's ``default_color``
parameter to set its color.  Normally you'll write your own subclass of
TileHandler which will (via your override of the data() method) set the tile's
pixels to more interesting colors.

More information
----------------

.. toctree::
   :maxdepth: 1

   pages/installation
   pages/api
   pages/examples


.. _neopixel matrix: https://www.adafruit.com/?q=neopixel%20matrix
