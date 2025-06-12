from __future__ import annotations

import json
import datetime
import typing
import os

import constants
import data_sender as data_sender_module

from simian.public.proto.v2 import io_pb2
from strada.public.log_readers import log_reader_base

MOCK_START_TIMESTAMP = datetime.datetime.fromtimestamp(1668741575, tz=datetime.timezone.utc)

class GPSPoseMessage(typing.NamedTuple):
    lat: float
    long: float
    next_lat: float
    next_long: float


class MockPositionReader(log_reader_base.LogReaderBase):
    """This log reader generates random gps data to convert and later send to ADP."""

    def __init__(
        self,
        _configuration: dict[typing.Any, typing.Any],
        data_sender: data_sender_module.DataSender,
    ) -> None:
        self._data_sender = data_sender
        self._gps_data = {}

        self._counter = 0

    def open(
        self, _path: log_reader_base.LogPath, log_open_options: io_pb2.LogOpenOptions
    ) -> io_pb2.LogOpenOutput:
        gps_path = os.path.join(log_open_options.path, "meta/gps.json")
        with open(gps_path) as f:
            self._gps_data = json.load(f)
        output = io_pb2.LogOpenOutput()
        output.start_timestamp.FromDatetime(MOCK_START_TIMESTAMP)
        return output

    def close(self, log_close_options: io_pb2.LogCloseOptions) -> None:
        pass

    def read_message(self) -> log_reader_base.LogReadType:
        gps_point = self._gps_data[self._counter]

        if self._counter < len(self._gps_data) - 1:
            next_gps_point = self._gps_data[self._counter + 1]
        else:
            next_gps_point = self._gps_data[self._counter]

        lat = gps_point['lat']
        long = gps_point['long']
        next_lat = next_gps_point['lat']
        next_long = next_gps_point['long']

        fake_epoch_time = MOCK_START_TIMESTAMP + datetime.timedelta(
            milliseconds=self._counter * 100
        )
        self._counter += 1
        print(f"fake_epoch_time pose: {fake_epoch_time}")
        return log_reader_base.LogReadType(constants.MOCK_POSE_TOPIC, GPSPoseMessage(lat, long, next_lat, next_long), fake_epoch_time)
