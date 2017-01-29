try:
    from neopixel import Adafruit_NeoPixel, ws
    DEFAULT_STRIP_TYPE = ws.WS2811_STRIP_GRB
except ImportError:
    DEFAULT_STRIP_TYPE = None

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except ImportError:
    pass

from neotiles import MatrixSize
from neotiles.exceptions import NeoTilesError

__all__ = ['NTMatrix', 'NTNeoPixelMatrix', 'NTRGBMatrix']


class NTMatrix(object):
    """
    Base class for the Neotiles Matrix interface.
    """
    def __init__(self):
        self._size = None
        self._brightness = None

    def setPixelColor(self, x, y, color):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, val):
        self._brightness = val

    @property
    def size(self):
        return self._size


class NTNeoPixelMatrix(NTMatrix):
    """
    Represents a NeoPixel matrix.

    You must specify a ``size`` matching your neopixel matrix (e.g. ``(8, 8)``)
    as well as the ``led_pin`` you're using to talk to it (e.g. ``18``). The
    other parameters can usually be left at their defaults.  For more
    information on the other parameters look at the ``Adafruit_NeoPixel``
    class in the
    `neopixel <https://github.com/jgarff/rpi_ws281x/tree/master/python>`_
    module.

    If your RGB values appear to be mixed up (e.g. red is showing as green)
    then try using a different ``strip_type``.  You can see a list of valid
    strip type constants here (look for ``_STRIP_`` in the constant name):
    https://docs.rs/ws281x/0.1.0/ws281x/ffi/index.html.  Specify a strip type
    like this: ``strip_type=ws.WS2811_STRIP_GRB``.  For this to work you'll
    need to ``import ws`` (which comes with the ``neopixel`` module) into your
    code.

    :param size: (:class:`MatrixSize`) Size of the neopixel matrix.
    :param led_pin: (int) The pin you're using to talk to your neopixel matrix.
    :param led_freq_hz: (int) LED frequency.
    :param led_dma: (int) LED DMA.
    :param led_brightness: (int) Brightness of the matrix display (0-255).
    :param led_invert: (bool) Whether to invert the LEDs.
    :param strip_type: (int) Neopixel strip type.
    :raises: :class:`exceptions.NeoTilesError` if ``matrix_size`` or
        ``led_pin`` are not specified.
    """
    def __init__(
            self, size=None, led_pin=None,
            led_freq_hz=800000, led_dma=5, led_brightness=64, led_invert=False,
            strip_type=DEFAULT_STRIP_TYPE):

        super(NTNeoPixelMatrix, self).__init__()

        if size is None or led_pin is None:
            raise NeoTilesError('size and led_pin must be specified')

        self._size = MatrixSize(*size)

        self._led_pin = led_pin
        self._led_freq_hz = led_freq_hz
        self._led_dma = led_dma
        self._brightness = led_brightness
        self._led_invert = led_invert
        self._strip_type = strip_type

        self._led_count = self.size.cols * self.size.rows

        self.hardware_matrix = Adafruit_NeoPixel(
            self._led_count, self._led_pin, freq_hz=self._led_freq_hz,
            dma=self._led_dma, invert=self._led_invert,
            brightness=self.brightness, strip_type=self._strip_type
        )

        self.hardware_matrix.begin()

    def __repr__(self):
        strip_name = self._strip_type

        # Convert strip name from strip type integer to associated attribute
        # name from ws module (if we can find it).
        for strip_check in [attr for attr in dir(ws) if '_STRIP_' in attr]:
            if getattr(ws, strip_check) == self._strip_type:
                strip_name = 'ws.{}'.format(strip_check)

        return (
            '{}(size={}, led_pin={}, led_freq_hz={}, led_dma={}, '
            'led_brightness={}, led_invert={}, strip_type={})'
        ).format(
            self.__class__.__name__, self.size, self._led_pin,
            self._led_freq_hz, self._led_dma, self.brightness,
            self._led_invert, strip_name
        )

    def setPixelColor(self, x, y, color):
        pixel_num = (y * self.size.cols) + x
        self.hardware_matrix.setPixelColor(pixel_num, color.hardware_int)

    def show(self):
        self.hardware_matrix.show()

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, val):
        error_msg = 'Brightness must be between 0 and 255'

        try:
            if val >= 0 and val <= 255:
                self._brightness = val
                self.hardware_matrix.setBrightness(self._brightness)
            else:
                raise ValueError(error_msg)
        except TypeError:
            raise ValueError(error_msg)


class NTRGBMatrix(NTMatrix):
    """
    Represents an RGB Matrix.

    If no options are passed in then the matrix will be initialized with
    default options.  These options can be overridden either with ``options``
    (which should be an ``RGBMatrixOptions`` object as provided by the
    ``rgbmatrix`` module); or individual options can be passed into the
    constructor.

    For example, the following are equivalent: ::

        from rgbmatrix import RGBMatrixOptions

        options = RGBMatrixOptions()
        options.chain_length = 2
        options.gpio_slowdown = 3

        NTRGBMatrix(options=options)

    and: ::

        NTRGBMatrix(chain_length=2, gpio_slowdown=3)

    :param options: (RGBMatrixOptions) Matrix options.
    :param kwargs: (*) Individual matrix options.
    """
    def __init__(self, options=None, **kwargs):
        super(NTRGBMatrix, self).__init__()

        if options is None:
            options = RGBMatrixOptions()
            for kwarg in kwargs:
                setattr(options, kwarg, kwargs[kwarg])

        self._size = MatrixSize(
            options.rows * options.chain_length, options.rows)

        self.options = options
        self.hardware_matrix = RGBMatrix(options=options)
        self.frame_canvas = self.hardware_matrix.CreateFrameCanvas()

    def __repr__(self):
        options = [
            attr for attr in dir(self.options) if
            not callable(getattr(self.options, attr)) and
            not attr.startswith('_')
        ]

        options_string = ', '.join([
            '{}={}'.format(option, getattr(self.options, option))
            for option in sorted(options)
        ])

        return '{}({})'.format(self.__class__.__name__, options_string)

    def setPixelColor(self, x, y, color):
        cd = color.components_denormalized
        self.frame_canvas.SetPixel(x, y, cd[0], cd[1], cd[2])

    def show(self):
        self.frame_canvas = self.hardware_matrix.SwapOnVSync(self.frame_canvas)

    @property
    def brightness(self):
        return self.hardware_matrix.brightness

    @brightness.setter
    def brightness(self, val):
        error_msg = 'Brightness must be between 0 and 100'

        try:
            if val >= 0 and val <= 100:
                self._brightness = val
                self.hardware_matrix.brightness = val
            else:
                raise ValueError(error_msg)
        except TypeError:
            raise ValueError(error_msg)
