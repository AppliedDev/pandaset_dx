from __future__ import annotations

import mailbox

from channel_handlers import channel_handler_base
import constants
import cv2
import data_sender
import interface_errors

from simian.public.proto import sensor_model_pb2
from simian.public.transforms import proto_util
from simian.public.transforms import spatial_py


class MockCameraChannelHandler(channel_handler_base.ChannelHandlerBase):
    """
    This channel handler converts the raw data from the log into the ADP format.
    """

    def __init__(self, data_sender: data_sender.DataSender, mailbox: mailbox.Mailbox) -> None:
        self._data_sender = data_sender
        self._mailbox = mailbox

        self._camera_proto = sensor_model_pb2.SensorOutput.CameraImage()

    def update(self) -> None:
        camera_data = self._mailbox.latest_messages.get(constants.MOCK_CAMERA_TOPIC)

        if camera_data is None:
            raise interface_errors.InterfaceImplementationError(
                f"Camera data not received from a log reader to the topic {constants.MOCK_CAMERA_TOPIC} but the `update` function on the channel handler was called."
            )
        img_bytes = cv2.imencode(".jpg", camera_data.image_arr)[1].tobytes()
        self._camera_proto.image.image_bytes = img_bytes
        self._camera_proto.image_shape.height = camera_data.height
        self._camera_proto.image_shape.width = camera_data.width
        camera_pose = spatial_py.Pose3d.create_with_roll_pitch_yaw(0, -10, 2, 0, -0.05, 1)
        camera_pose_proto = proto_util.pose3d_to_proto(camera_pose)
        self._camera_proto.pose.CopyFrom(camera_pose_proto)

    def get(self) -> sensor_model_pb2.SensorOutput.CameraImage:
        return self._camera_proto
