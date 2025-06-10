from __future__ import annotations

import unittest

import data_sender
import mock_camera_reader

from simian.public.proto.v2 import io_pb2

EXPECTED_NUM_MESSAGES = 10


class MockCameraReaderTest(unittest.TestCase):
    def test_camera_reader(self) -> None:
        s = mock_camera_reader.MockCameraReader({}, data_sender.FakeDataSender())
        s.open("", io_pb2.LogOpenOptions())
        num_messages = 0
        try:
            while True:
                next(s)
                num_messages += 1
        except StopIteration:
            pass

        self.assertEqual(num_messages, EXPECTED_NUM_MESSAGES)


if __name__ == "__main__":
    unittest.main()
