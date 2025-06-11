# Copyright (C) 2021 Applied Intuition, Inc. All rights reserved.
# This source code file is distributed under and subject to the LICENSE in license.txt
from __future__ import annotations

import datetime
import heapq
import logging
import mailbox
import typing

from channel_handlers import mock_camera_channel_handler
from channel_handlers import mock_pose_channel_handler
import constants
import data_sender
from google.protobuf import json_format
from log_readers import mock_camera_reader
from log_readers import mock_position_reader

from simian.public import customer_stack_server
from simian.public import stack_interface_v2
from simian.public.proto import common_pb2
from simian.public.proto.v2 import io_pb2
from strada.public.log_readers import log_reader_base

DEFAULT_RATE = 10


class DataExplorerInterface(stack_interface_v2.StackInterfaceV2):
    """Implements the interface class
    The necessary methods are:
        * get_default_rate
        * convert_to_simian
        * convert_to_simian_free
        * log_open_v2_2
        * log_read_v2_1
        * log_close
    """

    def __init__(self, proc_handler: typing.Any) -> None:
        super().__init__(proc_handler)

        # This will be populated with the channel names
        # that are requested by ADP as part of the log conversion
        # AFTER set_startup_options_v2_1 is called.
        self._channel_names: list[str] = []

        self._data_sender = data_sender.DataSender(self)
        self._unprocessed_message = None

        # Store earliest log startime seen.
        self._earliest_log_dt = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)

        self._mailbox = mailbox.Mailbox()

    def get_default_rate(self, _channel: str) -> int:
        """Returns the default channel rate (in this case 10Hz)"""
        return DEFAULT_RATE

    def convert_to_simian(self, channel: io_pb2.Channel) -> typing.Any:
        """Returns data for the specified channel at this time in ADP format"""
        return self._mailbox.latest_outputs.get(channel.name)

    def convert_to_simian_free(self, channel: str) -> None:
        """Optionally frees any data returned by convert_to_simian"""
        pass

    def set_startup_options_v2_1(self, startup_options: io_pb2.InterfaceStartupOptions) -> None:
        channels = startup_options.channel_setup.all_channels
        self._channel_names = [channel.name for channel in channels]

        options = json_format.MessageToDict(startup_options)
        logging.warning(f"In set startup {options}")  # noqa: G004
        self._extra_data = options.get("scenarioExtraData", {})

    def log_open_v2_2(self, log_open_options: io_pb2.LogOpenOptions) -> io_pb2.LogOpenOutput:
        """Called once at the start of the conversion. Does all the work necessary to prepare
        for the conversion, including opening files, querying the DBs, and downloading data.
        The drive start time is returned in the output.
        """

        # Add any additional information here to initialize the
        # log readers with the right configuration based on the drive configuration
        # parameters or the scenario extra data.
        reader_configuration = {"channel_names": self._channel_names}

        # Initialize the log readers.
        self._log_readers: list[log_reader_base.LogReaderBase] = [
            mock_camera_reader.MockCameraReader(reader_configuration, self._data_sender),
            mock_position_reader.MockPositionReader(reader_configuration, self._data_sender),
        ]

        self._pose_handler = mock_pose_channel_handler.MockPoseChannelHandler(
            self._data_sender, self._mailbox
        )
        self._camera_handler = mock_camera_channel_handler.MockCameraChannelHandler(
            self._data_sender, self._mailbox
        )

        # Create a multi log reader which will combine messages
        # from all the log readers, organized by earliest timestamp.

        # NOTE: A heapq can be slow. If you only have one log reader, you
        # can remove this. If conversion performance is slow, consider
        # using alternative methods to decide which messages to send back to
        # ADP first.
        self._multi_log_reader = heapq.merge(
            *self._log_readers, key=lambda log_read_type: log_read_type.epoch_timestamp
        )

        output = io_pb2.LogOpenOutput()
        for log_reader in self._log_readers:
            log_open_response = log_reader.open("", log_open_options)

            # Check if this log start time is the earliest we've seen
            log_start_datetime = log_open_response.start_timestamp.ToDatetime(
                tzinfo=datetime.timezone.utc
            )
            if log_start_datetime < self._earliest_log_dt:
                self._earliest_log_dt = log_start_datetime

        output.start_timestamp.FromDatetime(self._earliest_log_dt)
        return output

    def log_read_v2_1(self, log_read_options: io_pb2.LogReadOptions) -> io_pb2.LogReadOutput:
        """Called repeatedly until all of the data has been read (or we have reached the
        max duration specified in the Drive Conversion modal).
        """
        target_offset = log_read_options.offset.ToTimedelta()

        # This variable will have a valid LogReadOutput when the log has a message ready to ingest.
        output = None
        if self._unprocessed_message is not None:
            if self._message_too_far(target_offset, self._unprocessed_message.epoch_timestamp):
                return self._create_output(offset=target_offset)
            output = self._process_message(self._unprocessed_message)
            self._unprocessed_message = None

        while output is None:
            try:
                read_message = next(iter(self._multi_log_reader))
            except StopIteration:
                return self._create_output(data_remaining=False)

            # Special case where the simulator is NOT ready to receive messages past a certain timestamp.
            # Save this message for processing later.
            if self._message_too_far(target_offset, read_message.epoch_timestamp):
                self._unprocessed_message = read_message
                return self._create_output(offset=target_offset)

            output = self._process_message(read_message)
        return output

    def _message_too_far(
        self, target_offset: datetime.timedelta, message_epoch: datetime.datetime
    ) -> bool:
        """Special case where the simulator is NOT ready to receive messages past a certain timestamp.
        Save this message for processing later.
        """
        message_offset = message_epoch - self._earliest_log_dt
        return message_offset > target_offset

    def _process_message(self, read_message: log_reader_base.LogReadType) -> io_pb2.LogReadOutput:
        """
        Process a single message.
        Return NONE if no output is ready (ie, no message required to convert to Applied visualization protos is seen).
        Datapoints & drawings can still be created during this function call, but should still return None if no channel is seen.
        """
        topic, message, epoch_timestamp = (
            read_message.topic,
            read_message.message,
            read_message.epoch_timestamp,
        )

        self._mailbox.latest_messages[read_message.topic] = message

        offset = epoch_timestamp - self._earliest_log_dt
        seen_channels = []

        if topic == constants.MOCK_POSE_TOPIC:
            self._populate_pose()
            seen_channels.extend([constants.POSE_CHANNEL])
        elif topic == constants.MOCK_CAMERA_TOPIC:
            self._populate_cameras()
            seen_channels.append(constants.CAMERA_CHANNEL)

        return self._create_output(offset=offset, seen_channels=seen_channels)

    def log_close(self, _log_close_options: io_pb2.LogCloseOptions) -> None:
        """Called once at the end of the drive conversion."""
        for log_reader in self._log_readers:
            log_reader.close(_log_close_options)
        logging.info("Drive conversion complete")

    @staticmethod
    def _create_output(
        offset: datetime.timedelta = datetime.timedelta(),
        data_remaining: bool = True,
        seen_channels: list[str] = [],
    ) -> io_pb2.LogReadOutput:
        """Creates the output returned by each call to log_read_v2_1"""
        output = io_pb2.LogReadOutput()
        output.data_remaining = data_remaining
        output.offset_reached.FromTimedelta(offset)

        if seen_channels:
            output.seen_channel_names.extend(seen_channels)
        return output

    def _populate_cameras(self) -> None:
        self._camera_handler.update()
        self._mailbox.latest_outputs[constants.CAMERA_CHANNEL] = self._camera_handler.get()

    def _populate_pose(self) -> None:
        self._pose_handler.update()
        self._mailbox.latest_outputs[constants.POSE_CHANNEL] = self._pose_handler.get()

    def _send_data_point(self, name: str, value: float) -> None:
        self.send_data_point(common_pb2.DataPoint(name=name, value=value))

    def _send_observer_event(self, name: str, passed: bool = False) -> None:
        self.send_observer_event(common_pb2.ObserverEvent(name=name, passed=passed))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting log converter")
    customer_stack_server.start_server(DataExplorerInterface)
