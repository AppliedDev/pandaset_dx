from __future__ import annotations

import datetime
import typing
import os
import pickle
import gzip
import numpy as np
import pandas as pd
import boto3
import io

import constants
import cv2
import data_sender as data_sender_module

from simian.public.proto.v2 import io_pb2
from simian.public.proto import sensor_model_pb2
from strada.public.log_readers import log_reader_base

MOCK_START_TIMESTAMP = datetime.datetime.fromtimestamp(1668741575.5, tz=datetime.timezone.utc)

def get_number_from_counter(counter: int) -> str:
    return f"{counter:02d}"

class LidarData(typing.NamedTuple):
    points: np.ndarray  # Nx4 array of (x,y,z,i) points

class MockLidarReader(log_reader_base.LogReaderBase):

    def __init__(
        self,
        _configuration: dict[typing.Any, typing.Any],
        data_sender: data_sender_module.DataSender,
    ) -> None:
        self._data_sender = data_sender
        self._lidar_clouds_path = None
        self._s3_client = boto3.client("s3")
        self._counter = 0

    def open(
        self, _path: log_reader_base.LogPath, log_open_options: io_pb2.LogOpenOptions
    ) -> io_pb2.LogOpenOutput:
        self._lidar_clouds_path = os.path.join(log_open_options.path, "lidar")
        print(self._lidar_clouds_path) # Pandaset/<id>/lidar
        output = io_pb2.LogOpenOutput()
        output.start_timestamp.FromDatetime(MOCK_START_TIMESTAMP)
        return output

    def close(self, log_close_options: io_pb2.LogCloseOptions) -> None:
        pass

    def read_message(self) -> log_reader_base.LogReadType:
        cloud_name = get_number_from_counter(self._counter) + ".pkl.gz"
        s3_key = os.path.join(self._lidar_clouds_path, cloud_name)
        print(f"S3 key: {s3_key}") # Pandaset/<id>/lidar/<counter>.pkl.gz

        fake_epoch_time = MOCK_START_TIMESTAMP + datetime.timedelta(seconds=self._counter * constants.PERIOD_SECONDS + 0.066)

        # Download and decompress the pickle file from S3
        compressed_buffer = io.BytesIO()
        try:
            self._s3_client.download_fileobj(
                Bucket=constants.BUCKET_NAME,
                Key=s3_key,
                Fileobj=compressed_buffer
            )
            compressed_buffer.seek(0)

            with gzip.GzipFile(fileobj=compressed_buffer, mode='rb') as gz:
                data = pickle.load(gz)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load LIDAR data from S3 key {s3_key}: {str(e)}")

        # Data is a pandas DataFrame with columns x, y, z, i (intensity)
        # Convert to numpy arrays in the required format
        points = data[['x', 'y', 'z', 'i']].to_numpy()  # Nx4 array of points

        # Create LidarData object
        lidar_data = LidarData(
            points=points,
        )

        print(f"length of lidar data: {len(lidar_data.points)}")

        self._counter += 1
        return log_reader_base.LogReadType(
            constants.MOCK_LIDAR_TOPIC,
            lidar_data,
            fake_epoch_time,
        )
