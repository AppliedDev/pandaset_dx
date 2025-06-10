from __future__ import annotations

import unittest

import data_sender
import mock_position_reader

from simian.public.proto.v2 import io_pb2

EXPECTED_NUM_MESSAGES = 120


class MockPositionReaderTest(unittest.TestCase):
    def test_position_reader(self) -> None:
        s = mock_position_reader.MockPositionReader({}, data_sender.FakeDataSender())
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
