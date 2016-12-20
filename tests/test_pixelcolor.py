import pytest

from neotiles import PixelColor


class TestPixelColor:
    def test_individual_components(self):
        """
        Test the red, green, blue, and white components with both 0-1 and
        0-255 values.
        """
        col = PixelColor(0, 0.25, 0.5, 1.0)
        assert col.red == 0
        assert col.green == 0.25
        assert col.blue == 0.5
        assert col.white == 1.0

        col = PixelColor(0, 0.25, 0.5)
        assert col.red == 0
        assert col.green == 0.25
        assert col.blue == 0.5
        assert col.white is None

        col = PixelColor(0, 127, 255, 16)
        assert col.red == 0
        assert col.green == 127
        assert col.blue == 255
        assert col.white == 16

        col = PixelColor(0, 127, 255)
        assert col.red == 0
        assert col.green == 127
        assert col.blue == 255
        assert col.white is None

        # Test some float and out-of-bounds denormalized values.
        col = PixelColor(-1, 96.764, 128.123, 995.4)
        assert col.red == 0
        assert col.green == 96
        assert col.blue == 128
        assert col.white == 255

        # Check out-of-bounds normalized floats.
        col = PixelColor(5.1, 0.1, 0.2, -99, normalized=True)
        assert col.is_normalized is True
        assert col.red == 1.0
        assert col.green == 0.1
        assert col.blue == 0.2
        assert col.white == 0.0

    def test_hardware_components(self):
        """
        Test the tuple returned by .hardware_components.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128)
        result = col.hardware_components
        assert len(result) == 3
        assert result[0] == 200
        assert result[1] == 255
        assert result[2] == 128

        col = PixelColor(200, 255, 128, 16)
        result = col.hardware_components
        assert len(result) == 4
        assert result[0] == 200
        assert result[1] == 255
        assert result[2] == 128
        assert result[3] == 16

        # Normalized.
        col = PixelColor(0.0, 0.5, 1.0)
        result = col.hardware_components
        assert len(result) == 3
        assert result[0] == 0
        assert result[1] == 127
        assert result[2] == 255

        col = PixelColor(0.0, 0.5, 1.0, 0.25)
        result = col.hardware_components
        assert len(result) == 4
        assert result[0] == 0
        assert result[1] == 127
        assert result[2] == 255
        assert result[3] == 63

    def test_hardware_int(self):
        """
        Test the integer value of a color.  This requires bit shifting the
        various components and or'ing the result.
        """
        col = PixelColor(0, 127, 255, 16)
        assert col.hardware_int == (
            col.white << 24 | col.red << 16 | col.green << 8 | col.blue)

        # And double-check against what this should be as a plain old number.
        assert col.hardware_int == 268468223

        # Do the same for an RGB color.
        col = PixelColor(0, 127, 255)
        assert col.hardware_int == col.red << 16 | col.green << 8 | col.blue
        assert col.hardware_int == 32767

    def test_is_normalized(self):
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

    def test_components(self):
        """
        Test tuple-based component retrieval.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128)
        assert len(col.components) == 3
        assert col.components[0] == 200
        assert col.components[1] == 255
        assert col.components[2] == 128

        col = PixelColor(200, 255, 128, 16)
        assert len(col.components) == 4
        assert col.components[0] == 200
        assert col.components[1] == 255
        assert col.components[2] == 128
        assert col.components[3] == 16

        # Normalized.
        col = PixelColor(0.1, 0.2, 0.3)
        assert len(col.components) == 3
        assert col.components[0] == 0.1
        assert col.components[1] == 0.2
        assert col.components[2] == 0.3

        col = PixelColor(0.1, 0.2, 0.3, 0.4)
        assert len(col.components) == 4
        assert col.components[0] == 0.1
        assert col.components[1] == 0.2
        assert col.components[2] == 0.3
        assert col.components[3] == 0.4

    def test_components_normalized(self):
        """
        Test normalized tuple-based component retrieval.
        """
        # Inputs not normalized.
        col = PixelColor(0, 127, 255, 64)
        result = col.components_normalized
        assert len(result) == 4
        assert result[0] == 0.0
        assert abs(result[1] - 0.5) < 0.01
        assert result[2] == 1.0
        assert abs(result[3] - 0.25) < 0.01

        # Inputs normalized.
        col = PixelColor(0.0, 0.5, 1.0)
        result = col.components_normalized
        assert len(result) == 3
        assert result[0] == 0.0
        assert result[1] == 0.5
        assert result[2] == 1.0

    def test_components_denormalized(self):
        """
        Test denormalized tuple-based component retrieval.
        """
        # Inputs not normalized.
        col = PixelColor(200, 255, 128)
        result = col.components_denormalized
        assert len(result) == 3
        assert result[0] == 200
        assert result[1] == 255
        assert result[2] == 128

        # Inputs normalized.
        col = PixelColor(0.0, 0.5, 1.0)
        result = col.components_denormalized
        assert len(result) == 3
        assert result[0] == 0
        assert result[1] == 127
        assert result[2] == 255

    def test_string(self):
        """
        Test the stringified color output.
        """
        # Not normalized.
        col = PixelColor(200, 255, 128)
        assert str(col) == (
            'PixelColor(red=200, green=255, blue=128, normalized=False)')

        col = PixelColor(200, 255, 128, 16)
        assert str(col) == (
            'PixelColor(red=200, green=255, blue=128, white=16, '
            'normalized=False)')

        # Normalized.
        col = PixelColor(0.1, 0.2, 0.3)
        assert str(col) == (
            'PixelColor(red=0.1, green=0.2, blue=0.3, normalized=True)')

        # Float output is limited to 5dp.
        col = PixelColor(0.1, 0.2, 0.333, 0.9121212121212)
        assert str(col) == ('PixelColor(red=0.1, green=0.2, blue=0.333, '
                            'white=0.91212, normalized=True)')

    def test_repr(self):
        """
        Test the repr color output.
        """
        col = PixelColor(200, 255, 128)
        assert repr(col) == (
            'PixelColor(red=200, green=255, blue=128, normalized=False)')

        col = PixelColor(200, 255, 128, 16)
        assert repr(col) == (
            'PixelColor(red=200, green=255, blue=128, white=16, '
            'normalized=False)')

        # Normalized.
        col = PixelColor(0.1, 0.2, 0.3)
        assert repr(col) == (
            'PixelColor(red=0.1, green=0.2, blue=0.3, normalized=True)')

        col = PixelColor(0.1, 0.2, 0.333, 0.9121212)
        assert repr(col) == (
            'PixelColor(red=0.1, green=0.2, blue=0.333, white=0.9121212, '
            'normalized=True)')

