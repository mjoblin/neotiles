Installation
============

Installation is done with pip: ::

    pip install neotiles

Note however that neotiles depends on the `rpi_ws281x`_ library and its
included Python bindings which are not pip-installable.  You can see full
instructions for installation of this dependency on the `Adafruit site`_.

The Adafruit instructions are summarized below (with the addition of a
`virtualenv`_). Perform the following steps on your Raspberry Pi: ::

    sudo apt-get update
    sudo apt-get install build-essential python-dev git scons swig

    virtualenv venv_neotiles --python=python3.4
    source venv_neotiles/bin/activate

    git clone https://github.com/jgarff/rpi_ws281x.git
    cd rpi_ws281x
    scons

    cd python
    # Make sure your virtualenv is set before installing.
    python setup.py install

You may also need to disable audio on the Raspberry Pi 3, otherwise it
interferes with the PWM magic that the rpi_ws281x library is doing.  Edit
``/boot/config.txt`` on your Pi and comment out the following line: ::

    # Enable audio (loads snd_bcm2835)
    #dtparam=audio=on

See more details on the `rpi_ws281x issues page`_.


.. _Adafruit site: https://learn.adafruit.com/neopixels-on-raspberry-pi/software
.. _rpi_ws281x: https://github.com/jgarff/rpi_ws281x
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _rpi_ws281x issues page: https://github.com/jgarff/rpi_ws281x/issues/103
