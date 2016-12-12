class TileColor:
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
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    @property
    def white(self):
        return self._white

    @property
    def is_normalized(self):
        return self._normalized

    @property
    def int(self):
        return (
            self._denormalize(self._white) << 24 |
            self._denormalize(self._red) << 16 |
            self._denormalize(self._green) << 8 |
            self._denormalize(self._blue)
        )

    @property
    def rgb(self):
        return self.red, self.green, self.blue

    @property
    def rgbw(self):
        return self.red, self.green, self.blue, self.white

    @property
    def rgb_denormalized(self):
        return (
            self._denormalize(self.red),
            self._denormalize(self.green),
            self._denormalize(self.blue)
        )

    @property
    def rgbw_denormalized(self):
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

