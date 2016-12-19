import pytest

from neotiles import PixelColor


class TestPixelColor:
    def test_components(self):
        """
        Test the red, green, blue, and white components with both 0-1 and
        0-255 values.
        """
        col = PixelColor(0, 0.25, 0.5, 1.0)
        assert col.red == 0
        assert col.green == 0.25
        assert col.blue == 0.5
        assert col.white == 1.0

        col = PixelColor(0, 127, 255, 16)
        assert col.red == 0
        assert col.green == 127
        assert col.blue == 255
        assert col.white == 16

    def test_int(self):
        """
        Test the integer value of a color.  This requires bit shifting the
        various components and or'ing the result.
        """
        col = PixelColor(0, 127, 255, 16)
        assert col.int == (col.white << 24 | col.red << 16 | col.green << 8 |
                           col.blue)

        # And double-check against what this should be as a plan old number.
        assert col.int == 268468223

    def test_normalized(self):
        """
        Test the value of is_normalized for both 0-1 and 0-255 cases, as well
        as forced normalization values.
        """
        col = PixelColor(0, 0, 0, 0)
        assert col.is_normalized is True

        col = PixelColor(1, 1, 1, 1)
        assert col.is_normalized is True

        col = PixelColor(0, 2, 0, 0)
        assert col.is_normalized is False

        col = PixelColor(0.1, 0.05, 0.98, 0)
        assert col.is_normalized is True

        col = PixelColor(200, 255, 128, 16)
        assert col.is_normalized is False

        # Checked for forced normalization.
        col = PixelColor(200, 255, 128, 16, normalized=True)
        assert col.is_normalized is True

        col = PixelColor(200, 255, 128, 16, normalized=False)
        assert col.is_normalized is False

        col = PixelColor(0.1, 0.1, 0.1, 0.1, normalized=False)
        assert col.is_normalized is False

        col = PixelColor(0.1, 0.1, 0.1, 0.1, normalized=True)
        assert col.is_normalized is True

    def test_tuple_rgb(self):
        """
        Test the tuple returned by .rgb.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128)
        assert len(col.rgb) == 3
        assert col.rgb[0] == 200
        assert col.rgb[1] == 255
        assert col.rgb[2] == 128

        # Normalized.
        col = PixelColor(0.1, 0.5, 1.0)
        assert len(col.rgb) == 3
        assert col.rgb[0] == 0.1
        assert col.rgb[1] == 0.5
        assert col.rgb[2] == 1.0

    def test_tuple_rgbw(self):
        """
        Test the tuple returned by .rgbw.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128, 64)
        assert len(col.rgbw) == 4
        assert col.rgbw[0] == 200
        assert col.rgbw[1] == 255
        assert col.rgbw[2] == 128
        assert col.rgbw[3] == 64

        # Normalized.
        col = PixelColor(0.1, 0.5, 1.0, 0.25)
        assert len(col.rgbw) == 4
        assert col.rgbw[0] == 0.1
        assert col.rgbw[1] == 0.5
        assert col.rgbw[2] == 1.0
        assert col.rgbw[3] == 0.25

    def test_tuple_rgb_denormalized(self):
        """
        Test the tuple returned by .rgb_denormalized.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128)
        result = col.rgb_denormalized
        assert len(result) == 3
        assert result[0] == 200
        assert result[1] == 255
        assert result[2] == 128

        # Normalized.
        col = PixelColor(0.0, 0.5, 1.0)
        result = col.rgb_denormalized
        assert len(result) == 3
        assert result[0] == 0
        assert result[1] == 127
        assert result[2] == 255

    def test_tuple_rgbw_denormalized(self):
        """
        Test the tuple returned by .rgbw_denormalized.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128, 16)
        result = col.rgbw_denormalized
        assert len(result) == 4
        assert result[0] == 200
        assert result[1] == 255
        assert result[2] == 128
        assert result[3] == 16

        # Normalized.
        col = PixelColor(0.0, 0.5, 1.0, 0.25)
        result = col.rgbw_denormalized
        assert len(result) == 4
        assert result[0] == 0
        assert result[1] == 127
        assert result[2] == 255
        assert result[3] == 63

    def test_string(self):
        """
        Test the stringified color output.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128)
        assert str(col) == ('PixelColor(red=200, green=255, blue=128, white=0, '
                            'normalized=False)')

        col = PixelColor(200, 255, 128, 16)
        assert str(col) == ('PixelColor(red=200, green=255, blue=128, white=16, '
                            'normalized=False)')

        # Normalized.
        col = PixelColor(0.1, 0.2, 0.3)
        assert str(col) == ('PixelColor(red=0.1, green=0.2, blue=0.3, white=0, '
                            'normalized=True)')

        # Float output is limited to 5dp.
        col = PixelColor(0.1, 0.2, 0.333, 0.9121212121212)
        assert str(col) == ('PixelColor(red=0.1, green=0.2, blue=0.333, '
                            'white=0.91212, normalized=True)')

    def test_repr(self):
        """
        Test the repr color output.
        """
        col = PixelColor(200, 255, 128)
        assert repr(col) == ('PixelColor(red=200, green=255, blue=128, white=0, '
                             'normalized=False)')

        col = PixelColor(200, 255, 128, 16)
        assert repr(col) == ('PixelColor(red=200, green=255, blue=128, white=16, '
                             'normalized=False)')

        # Normalized.
        col = PixelColor(0.1, 0.2, 0.3)
        assert repr(col) == ('PixelColor(red=0.1, green=0.2, blue=0.3, white=0, '
                             'normalized=True)')

        col = PixelColor(0.1, 0.2, 0.333, 0.9121212)
        assert repr(col) == ('PixelColor(red=0.1, green=0.2, blue=0.333, '
                             'white=0.9121212, normalized=True)')

