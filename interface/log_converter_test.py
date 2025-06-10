from __future__ import annotations

import collections
import typing
import unittest

import log_converter

from simian.public.proto import sensor_model_pb2
from simian.public.proto.v2 import io_pb2

EXPECTED_MESSAGE_FREQUENCY = {
    io_pb2.Pose: 120,
    sensor_model_pb2.SensorOutput.CameraImage: 10,
}


class LogConverterTest(unittest.TestCase):
    def test_interface(self) -> None:
        interface = log_converter.DataExplorerInterface(None)
        interface.log_open_v2_2(io_pb2.LogOpenOptions(path=""))
        t = 0
        num_messages = 0

        frequencies: dict[typing.Any, int] = collections.defaultdict(int)
        while True:
            read_options = io_pb2.LogReadOptions()
            read_options.offset.FromMilliseconds(t)
            read_output = interface.log_read_v2_1(read_options)
            offset_reached = read_output.offset_reached

            # for each channel, run convert
            for channel in read_output.seen_channel_names:
                data = interface.convert_to_simian(io_pb2.Channel(name=channel))
                frequencies[type(data)] += 1
                num_messages += 1
            if offset_reached.ToMilliseconds() >= t:
                t += 100

            if not read_output.data_remaining:
                break
        for channel_type in EXPECTED_MESSAGE_FREQUENCY:
            self.assertEqual(frequencies[channel_type], EXPECTED_MESSAGE_FREQUENCY[channel_type])


if __name__ == "__main__":
    unittest.main()
