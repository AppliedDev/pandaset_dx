from __future__ import annotations

import typing

from simian.public.proto import common_pb2
from simian.public.proto import drawing_pb2

if typing.TYPE_CHECKING:
    from log_converter import DataExplorerInterface


class DataSender:
    def __init__(self, log_converter: DataExplorerInterface):
        self._log_converter = log_converter

    def send_data_point(self, datapoint: common_pb2.DataPoint) -> None:
        """send custom data points as common_pb2.DataPoint to ADP"""
        self._log_converter.send_data_point(datapoint)

    def send_drawing(self, drawing: drawing_pb2.Drawing) -> None:
        """send a drawing proto as drawing_pb2.Drawing to ADP"""
        self._log_converter.send_drawing(drawing)

    def send_timestamped_struct(self, timestamped_struct: common_pb2.TimestampedStruct) -> None:
        """send a timestamped struct proto as common_pb2.TimestampedStruct to ADP"""
        self._log_converter.send_timestamped_struct(timestamped_struct)

    def send_log_custom_field(self, datapoint: common_pb2.CustomField) -> None:
        """send custom log custom points to ADP"""
        self._log_converter.send_log_custom_field(datapoint)


class FakeDataSender(DataSender):
    """
    For use in testing.
    """

    def __init__(self) -> None:
        pass

    def send_data_point(self, datapoint: common_pb2.DataPoint) -> None:
        """send custom data points as common_pb2.DataPoint to ADP"""
        print("Sending data point", datapoint)

    def send_drawing(self, drawing: drawing_pb2.Drawing) -> None:
        """send a drawing proto as drawing_pb2.Drawing to ADP"""
        print("Sending drawing", drawing)

    def send_timestamped_struct(self, timestamped_struct: common_pb2.TimestampedStruct) -> None:
        """send a timestamped struct proto as common_pb2.TimestampedStruct to ADP"""
        print("Sending timestamped struct", timestamped_struct)

    def send_log_custom_field(self, datapoint: common_pb2.CustomField) -> None:
        """send custom log custom points to ADP"""
        print("Sending log custom points", datapoint)
