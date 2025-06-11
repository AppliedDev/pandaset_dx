from __future__ import annotations

import datetime
import typing
import os

import constants
import cv2
import data_sender as data_sender_module
import numpy as np

from simian.public.proto.v2 import io_pb2
from strada.public.log_readers import log_reader_base

MOCK_START_TIMESTAMP = datetime.datetime.fromtimestamp(1668741575.5, tz=datetime.timezone.utc)

def get_number_from_counter(counter: int) -> str:
    return f"{counter:02d}"


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
        self._camera_images_path = None

        self._counter = 0

    def open(
        self, _path: log_reader_base.LogPath, log_open_options: io_pb2.LogOpenOptions
    ) -> io_pb2.LogOpenOutput:
        self._camera_images_path = os.path.join(log_open_options.path, "camera/front_camera")
        print(self._camera_images_path)
        output = io_pb2.LogOpenOutput()
        output.start_timestamp.FromDatetime(MOCK_START_TIMESTAMP)
        return output

    def close(self, log_close_options: io_pb2.LogCloseOptions) -> None:
        pass

    def read_message(self) -> log_reader_base.LogReadType:
        image_name = get_number_from_counter(self._counter) + ".jpg"
        image_path = os.path.join(self._camera_images_path, image_name)

        fake_epoch_time = MOCK_START_TIMESTAMP + datetime.timedelta(seconds=self._counter * constants.PERIOD_SECONDS)

        arr = cv2.imread(image_path)
        if arr is None:
            raise FileNotFoundError(f"Failed to read image at {image_path}")
        height, width = arr.shape[:2]

        self._counter += 1
        return log_reader_base.LogReadType(
            constants.MOCK_CAMERA_TOPIC,
            CameraData(image_arr=arr, height=height, width=width),
            fake_epoch_time,
        )
