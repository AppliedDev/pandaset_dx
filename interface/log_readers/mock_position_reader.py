from __future__ import annotations

import datetime
import typing

import constants
import data_sender as data_sender_module

from simian.public.proto.v2 import io_pb2
from strada.public.log_readers import log_reader_base

MOCK_START_TIMESTAMP = datetime.datetime.fromtimestamp(1668741575, tz=datetime.timezone.utc)


class OffsetPosition(typing.NamedTuple):
    x: float
    y: float


class MockPositionReader(log_reader_base.LogReaderBase):
    """This log reader generates random gps data to convert and later send to ADP."""

    def __init__(
        self,
        _configuration: dict[typing.Any, typing.Any],
        data_sender: data_sender_module.DataSender,
    ) -> None:
        self._data_sender = data_sender

        self._counter = 0

    def open(
        self, _path: log_reader_base.LogPath, _log_open_options: io_pb2.LogOpenOptions
    ) -> io_pb2.LogOpenOutput:
        output = io_pb2.LogOpenOutput()
        output.start_timestamp.FromDatetime(MOCK_START_TIMESTAMP)
        return output

    def close(self, log_close_options: io_pb2.LogCloseOptions) -> None:
        pass

    def read_message(self) -> log_reader_base.LogReadType:
        if self._counter == 120:
            return None

        fake_epoch_time = MOCK_START_TIMESTAMP + datetime.timedelta(
            milliseconds=self._counter * 100
        )

        self._counter += 1
        return log_reader_base.LogReadType(
            constants.MOCK_POSE_TOPIC, OffsetPosition(self._counter, 0), fake_epoch_time
        )
