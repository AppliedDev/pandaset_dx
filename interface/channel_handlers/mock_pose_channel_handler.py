from __future__ import annotations

import mailbox

from channel_handlers import channel_handler_base
import constants
import data_sender
import interface_errors

from simian.public.proto import common_pb2
from simian.public.proto.v2 import io_pb2
from simian.public.transforms import proto_util
from simian.public.transforms import spatial_py

ORIGIN = {"x": 587502.2016647939, "y": 4140476.18819831}


class MockPoseChannelHandler(channel_handler_base.ChannelHandlerBase):
    """
    This channel handler converts the raw data from the log into the ADP format.
    """

    def __init__(self, data_sender: data_sender.DataSender, mailbox: mailbox.Mailbox) -> None:
        self._data_sender = data_sender
        self._mailbox = mailbox

        self._pose_proto = io_pb2.Pose()

    def update(self) -> None:
        position = self._mailbox.latest_messages.get(constants.MOCK_POSE_TOPIC)
        if position is None:
            raise interface_errors.InterfaceImplementationError(
                f"Camera data not received from a log reader to the topic {constants.MOCK_CAMERA_TOPIC} but the `update` function on the channel handler was called."
            )

        del self._pose_proto.sections[:]
        section = self._pose_proto.sections.add()
        pose3d = spatial_py.Pose3d.create_with_roll_pitch_yaw(
            position.x + ORIGIN["x"], position.y + ORIGIN["y"], 0, 0, 0, 0
        )
        section.state.pose.CopyFrom(proto_util.pose3d_to_proto(pose3d))

        self._data_sender.send_data_point(common_pb2.DataPoint(name="x offset", value=position.x))
        self._data_sender.send_data_point(common_pb2.DataPoint(name="y offset", value=position.y))

    def get(self) -> io_pb2.Pose:
        return self._pose_proto
