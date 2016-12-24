#!/usr/bin/env python

from collections import deque

from neotiles import TileManager, PixelColor, Tile, TilePosition, TileSize
from netdumplings import DumplingEater


class Simplemovingaverage():
    # Taken from:
    # https://rosettacode.org/wiki/Averages/Simple_moving_average#Python
    def __init__(self, period):
        assert period == int(
            period) and period > 0, "Period must be an integer >0"
        self.period = period
        self.stream = deque()

    def __call__(self, n):
        stream = self.stream
        stream.append(n)  # appends on the right
        streamlength = len(stream)
        if streamlength > self.period:
            stream.popleft()
            streamlength -= 1
        if streamlength == 0:
            average = 0
        else:
            average = sum(stream) / streamlength

        return average


class PacketCountIntensityTile(Tile):
    def __init__(self, protocol='TCP', max_color=None, avg_intensity=0.5):
        """

        :param protocol:
        :param max_color:
        :param avg_intensity:
        """
        super().__init__(animate=False)

        self._protocol = protocol
        self._max_color = max_color
        self._avg_intensity = avg_intensity

        self._last_count = -1
        self._packet_history_far = Simplemovingaverage(period=60)
        self._packet_history_near = Simplemovingaverage(period=5)

    def draw(self):
        """

        :param in_data:
        :return:
        """
        if self.data is None:
            return

        packet_count = self.data['payload']['packet_counts'][self._protocol]

        if self._last_count > -1:
            packet_increment = packet_count - self._last_count
            avg_near = self._packet_history_near(packet_increment)
            avg_far = self._packet_history_far(packet_increment)
            self._last_count = packet_count
        else:
            self._last_count = packet_count
            return

        # TODO: This linear range is too restrictive.  Try log?
        try:
            display_intensity = (avg_near / avg_far) * self._avg_intensity
        except ZeroDivisionError:
            display_intensity = 0

        display_intensity = 1 if display_intensity > 1 else display_intensity

        for row in range(self.size[1]):
            for col in range(self.size[0]):
                display_color = tuple(
                    [int(val * display_intensity)
                     for val in self._max_color.components_denormalized]
                )
                self.set_pixel(
                    TilePosition(col, row), PixelColor(*display_color))


class Packtrix:
    def __init__(self):
        """

        """
        shifty_uri = "10.0.1.3:11348"
        self.dumpling_eater = DumplingEater(
            name='packtrix', shifty=shifty_uri, chefs=['PacketCountChef'],
            on_dumpling=self.on_dumpling
        )

        self.neotiles = TileManager(
            matrix_size=(8, 8), led_pin=18, draw_fps=None)
        print('Created: {}'.format(repr(self.neotiles)))

        tcp_intensity = PacketCountIntensityTile(
            protocol='TCP', max_color=PixelColor(1, 0, 0))
        udp_intensity = PacketCountIntensityTile(
            protocol='IPv6', max_color=PixelColor(0, 1, 0))
        ip6_intensity = PacketCountIntensityTile(
            protocol='IPv6', max_color=PixelColor(0, 0, 1))

        self.neotiles.register_tile(
            size=TileSize(8, 4), root=TilePosition(0, 0), tile=tcp_intensity)
        self.neotiles.register_tile(
            size=TileSize(8, 2), root=TilePosition(0, 4), tile=udp_intensity)
        self.neotiles.register_tile(
            size=TileSize(8, 2), root=TilePosition(0, 6), tile=ip6_intensity)

    async def on_dumpling(self, dumpling):
        """

        :param dumpling:
        :return:
        """
        for tile_object in self.neotiles.tiles:
            tile_object.data = dumpling
            tile_object.draw()

        self.neotiles.draw_hardware_matrix()

        print('{}\n'.format(self.neotiles))

    def run(self):
        """

        :return:
        """
        self.dumpling_eater.run()
        self.neotiles.draw_stop()

    def clear(self):
        self.neotiles.clear_hardware_matrix()


def main():
    packtrix = Packtrix()

    packtrix.run()
    packtrix.clear()


# =============================================================================

if __name__ == '__main__':
    main()



