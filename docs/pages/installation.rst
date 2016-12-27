Installation
============

Installation is done with pip: ::

    pip install neotiles


There's a couple of quirks to contend with though:

#. neotiles depends on the `rpi_ws281x`_ library and its included Python bindings (which exposes the *neopixel* module), and these are not pip-installable.
#. Any scripts running neotiles need to be run as root so that the hardware can be accessed properly.

With that in mind you can choose to install everything into either a
`virtualenv`_ or into the main system Python.

(These instructions have been pulled in part from the
`Adafruit learning site`_.)

Regardless of which approach you choose, you first need to install some system
dependencies on your Raspberry Pi first: ::

    sudo apt-get update
    sudo apt-get install build-essential python-dev git scons swig


Now choose one of the following two options...

1. Installing into a virtualenv
-------------------------------

For this approach we'll be doing everything as root.  The downside is that
you'll be logged in as root which can be dangerous if you're not careful.  On
the upside, you can more easily specify a Python version; you don't have to
pollute your system Python; and you don't have to remember to run your neotiles
scripts with sudo.

Here's the steps: ::

    # Become root.
    sudo su -

    # Install virtualenv if it's not already installed.
    pip install virtualenv

    # Create a virtualenv to install the neopixel library. This forces
    # Python 3.4.  Remove '--python=python3.4' to use default Python
    # (usually Python 2.7).
    virtualenv venv_neotiles --python=python3.4
    source venv_neotiles/bin/activate

    # Download the neopixel code from github.
    git clone https://github.com/jgarff/rpi_ws281x.git
    cd rpi_ws281x

    # Install the neopixel library's dependency.
    scons

    # Install the neopixel library.
    cd python
    python ./setup.py install

    # Install neotiles.
    pip install neotiles

2. Installing into the system Python
------------------------------------

Installing into the system Python is safer as you won't be logged in as root,
but you'll be polluting your system Python with the neotiles module and its
dependencies and it can be more difficult to control which Python version is
running.

Here's the steps (see the previous section for more info on what each step is
doing): ::

    git clone https://github.com/jgarff/rpi_ws281x.git
    cd rpi_ws281x
    scons
    cd python
    sudo python setup.py install
    sudo pip install neotiles


Another step: disabling audio
-----------------------------

You may also need to disable audio on the Raspberry Pi 3, otherwise it
interferes with the PWM magic that the rpi_ws281x library is doing.  Edit
``/boot/config.txt`` on your Pi, comment out the following line, and reboot: ::

    # Enable audio (loads snd_bcm2835)
    #dtparam=audio=on

See more details on the `rpi_ws281x issues page`_.

Prepare the hardware
--------------------

You also need to have your neopixel matrix `wired up`_ and ready to go.

Testing the install
-------------------

To test that everything is working you can run an example script (e.g.
``speckled_tiles.py``) from the git repository.  Note that ``text_scroller.py``
won't work without an additional install -- see the
`examples page <examples.html>`_ for more. ::

    git clone https://github.com/mjoblin/neotiles.git
    cd neotiles/examples

You'll need to edit the script to set ``MATRIX_SIZE``, ``LED_PIN``,
and ``STRIP_TYPE`` appropriately for your hardware, and then run it: ::

    # In a virtualenv (as root)
    python ./speckled_tiles.py

    # Not in a virtualenv
    sudo python ./speckled_tiles.py

If your neopixel matrix is showing colors but they look a bit messed up, try
changing the ``STRIP_TYPE``.

.. _Adafruit learning site: https://learn.adafruit.com/neopixels-on-raspberry-pi/software
.. _rpi_ws281x: https://github.com/jgarff/rpi_ws281x
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _rpi_ws281x issues page: https://github.com/jgarff/rpi_ws281x/issues/103
.. _wired up: https://learn.adafruit.com/neopixels-on-raspberry-pi/wiring
