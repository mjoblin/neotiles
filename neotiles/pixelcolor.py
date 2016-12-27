from __future__ import division


class PixelColor(object):
    """
    Represents a single neopixel color (either RGB or RGBW).

    The ``red``, ``blue``, ``green``, and ``white`` components can either be
    between 0 and 1 (normalized), or between 0 and 255.  PixelColor will
    attempt to determine automatically whether the components are normalized,
    but this can be forced with ``normalized``.

    All object attributes are read-only.

    :param red: (float|int) Red component.
    :param green: (float|int) Green component.
    :param blue: (float|int) Blue component.
    :param white: (float|int) White component (set to ``None`` if RGB only).
    :param normalized: (bool) Whether the color is normalized (will be guessed
        if ``None``).
    """
    def __init__(self, red=0, green=0, blue=0, white=None, normalized=None):
        self._red = red
        self._green = green
        self._blue = blue
        self._white = white
        self._normalized = normalized

        if normalized is None:
            # We're guessing whether the input is normalized (between 0 and 1)
            # or not.  If any component is greater than 1 then we assume that
            # the input is not normalized.
            white_test = 0 if white is None else white
            self._normalized = not (
                red > 1 or green > 1 or blue > 1 or white_test > 1
            )

    def __repr__(self):
        return '{}(red={}, green={}, blue={}, {}normalized={})'.format(
            self.__class__.__name__,
            self.red, self.green, self.blue,
            '' if self.is_rgb else 'white={}, '.format(self.white),
            self.is_normalized
        )

    def __str__(self):
        if self._normalized:
            formatter = ('{}(red={:.5g}, green={:.5g}, blue={:.5g}, '
                         '{}normalized={})')
        else:
            formatter = '{}(red={}, green={}, blue={}, {}normalized={})'

        white_str = ''
        if self.is_rgbw:
            white_str = (
                'white={:.5g}, '.format(self.white) if self.is_normalized
                else 'white={}, '.format(self.white)
            )

        return formatter.format(
            self.__class__.__name__,
            self.red, self.green, self.blue, white_str,
            self.is_normalized
        )

    def _normalize(self, val):
        """
        Normalizes a single color component.  Does nothing if the component
        is already normalized.

        :param val: (float|int) The component value to convert.
        :return: (int) A normalized value between 0 and 1.
        """
        if self.is_normalized:
            return val
        else:
            return float(val / 255)

    def _denormalize(self, val):
        """
        Denormalizes a single color component.  Does nothing if the component
        is already denormalized.

        :param val: (float|int) The component value to convert.
        :return: (int) A denormalized value between 0 and 255.
        """
        if self.is_normalized:
            return int(val * 255)
        else:
            return val

    def _sanitize_component(self, val):
        """
        Sanitize a component value.  Denormalized values will always be
        returned as integers.  Normalized values are clipped between 0.0 and
        1.0.

        :param val: (float|int) Component value to sanitize.
        :return: (float|int) Sanitized values.
        """
        if self.is_normalized:
            # Lock normalized values between 0 and 1.
            if val < 0:
                return 0.0
            if val > 1:
                return 1.0
            return val
        else:
            # Lock denormalized values between 0 and 255.
            if val < 0:
                return 0
            if val > 255:
                return 255
            return int(val)

    @property
    def red(self):
        """
        (float|int) The red component.
        """
        return self._sanitize_component(self._red)

    @property
    def green(self):
        """
        (float|int) The green component.
        """
        return self._sanitize_component(self._green)

    @property
    def blue(self):
        """
        (float|int) The blue component.
        """
        return self._sanitize_component(self._blue)

    @property
    def white(self):
        """
        (float|int) The white component.
        """
        if self._white is None:
            return None

        return self._sanitize_component(self._white)

    @property
    def is_normalized(self):
        """
        (bool) Whether the color is normalized.
        """
        return self._normalized

    @property
    def is_rgb(self):
        """
        (bool) Whether the color is RGB only.
        """
        return self.white is None

    @property
    def is_rgbw(self):
        """
        (bool) Whether the color is RGBW.
        """
        return self.white is not None

    @property
    def components(self):
        """
        The color as a tuple of RGB(W) component values.  Values will either be
        normalized or denormalized to match ``is_normalized``.
        """
        if self.is_rgb:
            return self.red, self.green, self.blue
        else:
            return self.red, self.green, self.blue, self.white

    @property
    def components_normalized(self):
        """
        The color as a tuple of normalized RGB(W) component values.
        """
        if self.is_rgb:
            return (
                self._normalize(self.red),
                self._normalize(self.green),
                self._normalize(self.blue),
            )
        else:
            return (
                self._normalize(self.red),
                self._normalize(self.green),
                self._normalize(self.blue),
                self._normalize(self.white),
            )

    @property
    def components_denormalized(self):
        """
        The color as a tuple of denormalized RGB(W) component values.
        """
        if self.is_rgb:
            return (
                self._denormalize(self.red),
                self._denormalize(self.green),
                self._denormalize(self.blue),
            )
        else:
            return (
                self._denormalize(self.red),
                self._denormalize(self.green),
                self._denormalize(self.blue),
                self._denormalize(self.white),
            )

    @property
    def hardware_components(self):
        """
        The color as a tuple of integers suitable for passing to
        ``Adafruit_NeoPixel.setPixelColorRGB()`` for display on neopixel
        hardware.
        """
        return self.components_denormalized

    @property
    def hardware_int(self):
        """
        The color as an integer suitable for passing to
        ``Adafruit_NeoPixel.setPixelColor()`` for display on neopixel hardware.
        """
        if self.is_rgb:
            return (
                self._denormalize(self.red) << 16 |
                self._denormalize(self.green) << 8 |
                self._denormalize(self.blue)
            )
        else:
            return (
                self._denormalize(self.white) << 24 |
                self._denormalize(self.red) << 16 |
                self._denormalize(self.green) << 8 |
                self._denormalize(self.blue)
            )
