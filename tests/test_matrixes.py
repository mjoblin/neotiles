import pytest

from neotiles import PixelColor
from neotiles.exceptions import NeoTilesError
from neotiles.matrixes import NTMatrix, NTNeoPixelMatrix, NTRGBMatrix


class TestMatrixes:
    def test_base_class(self):
        """
        Test the base class.
        """
        base = NTMatrix()

        with pytest.raises(NotImplementedError):
            base.setPixelColor(1, 1, PixelColor(1, 1, 1))

        with pytest.raises(NotImplementedError):
            base.show()

        assert base.brightness is None
        assert base.size is None

        base.brightness = 10
        assert base.brightness == 10

    def test_neopixel_instantiation(self):
        """
        Test neopixel matrix instantiation.
        """
        with pytest.raises(NeoTilesError) as e:
            NTNeoPixelMatrix()
        assert 'size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            NTNeoPixelMatrix(led_pin=18)
        assert 'size and led_pin must be specified' in str(e)

        with pytest.raises(NeoTilesError) as e:
            NTNeoPixelMatrix(size=(8, 8))
        assert 'size and led_pin must be specified' in str(e)

    def test_neopixel_repr(self):
        """
        Test the neopixel matrix default representation.
        """
        matrix = NTNeoPixelMatrix(size=(8, 8), led_pin=18)
        assert repr(matrix) == (
            'NTNeoPixelMatrix(size=MatrixSize(cols=8, rows=8), led_pin=18, '
            'led_freq_hz=800000, led_dma=5, led_brightness=64, '
            'led_invert=False, strip_type=ws.WS2811_STRIP_GRB)'
        )

    def test_rgb_repr(self):
        """
        Test the RGB matrix default representation.
        """
        matrix = NTRGBMatrix()
        assert repr(matrix) == (
            'NTRGBMatrix(brightness=100, chain_length=1, daemon=0, '
            'disable_hardware_pulsing=False, drop_privileges=1, '
            'gpio_slowdown=1, hardware_mapping=b\'adafruit-hat-pwm\', '
            'inverse_colors=False, parallel=1, pwm_bits=11, '
            'pwm_lsb_nanoseconds=130, rows=32, scan_mode=0, '
            'show_refresh_rate=False, swap_green_blue=False)'
        )
