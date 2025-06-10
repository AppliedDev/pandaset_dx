from __future__ import annotations

import datetime
import typing

import constants
import cv2
import data_sender as data_sender_module
import numpy as np

from simian.public.proto.v2 import io_pb2
from strada.public.log_readers import log_reader_base

MOCK_START_TIMESTAMP = datetime.datetime.fromtimestamp(1668741575.5, tz=datetime.timezone.utc)
MOCK_CAMERA_WIDTH = 600
MOCK_CAMERA_HEIGHT = 400


class CameraData(typing.NamedTuple):
    image_arr: typing.Any
    height: int
    width: int


class MockCameraReader(log_reader_base.LogReaderBase):
    """This log reader generates random camera data to convert and later send to ADP."""

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
        if self._counter == 10:
            return None

        fake_epoch_time = MOCK_START_TIMESTAMP + datetime.timedelta(seconds=self._counter)

        arr = np.zeros((MOCK_CAMERA_HEIGHT, MOCK_CAMERA_WIDTH, 3), dtype=np.uint8)
        arr[:, :, self._counter % 3] = 255
        arr = cv2.putText(arr, str(self._counter), (75, 175), 0, 1, (0, 0, 0), thickness=2).astype(
            np.uint8
        )

        self._counter += 1
        return log_reader_base.LogReadType(
            constants.MOCK_CAMERA_TOPIC,
            CameraData(image_arr=arr, height=MOCK_CAMERA_HEIGHT, width=MOCK_CAMERA_WIDTH),
            fake_epoch_time,
        )
