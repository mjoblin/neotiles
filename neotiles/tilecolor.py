class TileColor:
    # TODO: Add __repr__ and __str__
    # TODO: Rename to NPColor.
    """
    Represents a single neopixel color.

    The ``red``, ``blue``, ``green``, and ``white`` components can either be
    between 0 and 1 (normalized), or between 0 and 255.  TileColor will attempt
    to determine automatically whether the components are normalized, but this
    can be forced with ``normalized`` (setting ``normalized=True`` will not
    force the components to be between 0 and 1, but will instead force
    TileColor to assume that they are).

    The ``white`` component will only have an effect on neopixels which
    support RGBW.

    :param red: (float|int) Red component.
    :param green: (float|int) Green component.
    :param blue: (float|int) Blue component.
    :param white: (float|int) White component.
    :param normalized: (bool) Whether the color is normalized.
    """
    def __init__(self, red=0, green=0, blue=0, white=0, normalized=None):
        self._red = red
        self._green = green
        self._blue = blue
        self._white = white
        self._normalized = normalized

        if normalized is None:
            # We're guessing whether the input is normalized (between 0 and 1)
            # or not.  If any component is greater than 1 then we assume that
            # the input is not normalized.
            self._normalized = not (
                red > 1 or green > 1 or blue > 1 or white > 1
            )

    @property
    def red(self):
        """
        The red component.  Read only.
        """
        return self._red

    @property
    def green(self):
        """
        The green component.  Read only.
        """
        return self._green

    @property
    def blue(self):
        """
        The blue component.  Read only.
        """
        return self._blue

    @property
    def white(self):
        """
        The white component.  Read only.
        """
        return self._white

    @property
    def is_normalized(self):
        """
        Whether the color is normalized or not.  When normalized, the different
        color component values are expected to be between 0 and 1.  Read only.
        """
        return self._normalized

    @property
    def int(self):
        """
        The color as an integer.  Read only.
        """
        return (
            self._denormalize(self._white) << 24 |
            self._denormalize(self._red) << 16 |
            self._denormalize(self._green) << 8 |
            self._denormalize(self._blue)
        )

    @property
    def rgb(self):
        """
        The color as a tuple of RGB values.  Read only.
        """
        return self.red, self.green, self.blue

    @property
    def rgbw(self):
        """
        The color as a tuple of RGBW values.  Read only.
        """
        return self.red, self.green, self.blue, self.white

    @property
    def rgb_denormalized(self):
        """
        The color as a tuple of denormalized RGB values (between 0 and 255 for
        each component).  Read only.
        """
        return (
            self._denormalize(self.red),
            self._denormalize(self.green),
            self._denormalize(self.blue)
        )

    @property
    def rgbw_denormalized(self):
        """
        The color as a tuple of denormalized RGBW values (between 0 and 255 for
        each component).  Read only.
        """
        return (
            self._denormalize(self.red),
            self._denormalize(self.green),
            self._denormalize(self.blue),
            self._denormalize(self.white)
        )

    def _denormalize(self, val):
        if self.is_normalized:
            return int(val * 256)
        else:
            return val

