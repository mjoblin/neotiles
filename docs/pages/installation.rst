Installation
============

Installation is done with pip: ::

    pip install neotiles

There's a few additional things to contend with though:

#. neotiles depends on additional libraries (used to drive the neopixel and RGB matrixes) which need to be manually installed.
#. You may need to disable audio on your Raspberry Pi.
#. Any scripts running neotiles need to be run as root so the hardware can be accessed properly.

Installing additional libraries
-------------------------------

You'll need to follow the instructions for installing the `neopixel libraries`_
and/or the `RGB matrix libraries`_ before you can run any neotiles code.

Disabling audio
---------------

You may need to disable audio on the Raspberry Pi 3 otherwise it interferes
with the PWM magic that the matrix libraries are doing.  Edit
``/boot/config.txt`` on your Pi, comment out the following line, and reboot: ::

    # Enable audio (loads snd_bcm2835)
    #dtparam=audio=on

See more details on the `rpi_ws281x issues page`_.

Running code as root
--------------------

To run your code as root just execute it like this: ::

    sudo ./my_code.py

If you've installed neotiles and/or its dependencies into a virtualenv then
the above will not work because ``sudo`` starts a new shell process which will
not inherit the environment of your virtualenv.  If you're using a virtualenv
then you may need to become root before setting the environment: ::

    sudo su -
    source /path/to/virtualenv/bin/activate
    python ./my_code.py

Take precautions with that shell environment though as it's owned by root.

Testing the install
-------------------

To test that everything is working you can run an example script provided with
neotiles: ::

    git clone https://github.com/mjoblin/neotiles.git
    cd neotiles/examples
    python ./speckled_tiles.py

You'll probably need to edit the example scripts and make some minor changes
before they will work on your hardware.  See the
`examples page <examples.html>`_ for more information.


.. _neopixel libraries: https://learn.adafruit.com/neopixels-on-raspberry-pi/software
.. _RGB matrix libraries: https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/python
.. _rpi_ws281x issues page: https://github.com/jgarff/rpi_ws281x/issues/103
