from __future__ import annotations

import mailbox
import numpy as np
import struct
import ctypes

from channel_handlers import channel_handler_base
import constants
import data_sender
import interface_errors

from simian.public.proto import sensor_model_pb2
from simian.public.transforms import proto_util
from simian.public.transforms import spatial_py


class MockLidarChannelHandler(channel_handler_base.ChannelHandlerBase):
    """
    This channel handler converts the raw lidar data from the log into the ADP format.
    """

    def __init__(self, data_sender: data_sender.DataSender, mailbox: mailbox.Mailbox) -> None:
        self._data_sender = data_sender
        self._mailbox = mailbox
        self._lidar_proto = sensor_model_pb2.SensorOutput.LidarCloud()

        # Initialize required fields
        self._lidar_proto.metadata.Clear()
        self._lidar_proto.id = 0  # Set an appropriate ID if needed
        self._lidar_proto.label_snapshot.Clear()

    def update(self) -> None:
        lidar_data = self._mailbox.latest_messages.get(constants.MOCK_LIDAR_TOPIC)

        if lidar_data is None:
            raise interface_errors.InterfaceImplementationError(
                f"Lidar data not received from a log reader to the topic {constants.MOCK_LIDAR_TOPIC} but the `update` function on the channel handler was called."
            )

        # Convert from standard right-handed Object Sim coordinate frame to
        # the left-handed coordinate frame that the lidar proto expects
        points = lidar_data.points.copy()

        # Create a new array with 7 columns (x,y,z,intensity,channel,instance_id,semantic_class)
        padded_points = np.zeros((points.shape[0], 7), dtype='<f')
        padded_points[:, :3] = points  # Copy the x,y,z coordinates
        # Other columns (intensity, channel, instance_id, semantic_class) remain 0

        # Convert from standard right-handed Object Sim coordinate frame to
        # the left-handed coordinate frame that the lidar proto expects
        padded_points[:,[0,1]] = -padded_points[:, [1,0]]

        # Create header bytes
        header_format = '<Q3I'  # 1x ULONG LONG, 3x ULONG
        header_size = struct.calcsize(header_format)
        header_bytes = ctypes.create_string_buffer(header_size)

        # Pack header with: timestamp(0), unused(0), unused(0), num_fields(7)
        struct.pack_into(header_format, header_bytes, 0, 0, 0, 0, 7)

        # Combine header and flattened points data
        raw_bytes = header_bytes.raw + padded_points.flatten().tobytes()
 
        # Set points data with header and converted points
        self._lidar_proto.Clear()
        self._lidar_proto.points = raw_bytes

        # Set lidar pose (example fixed pose, adjust as needed)
        lidar_pose = spatial_py.Pose3d.create_with_roll_pitch_yaw(0, 0, 0, 0, 0, 0)  # x,y,z, roll,pitch,yaw
        lidar_pose_proto = proto_util.pose3d_to_proto(lidar_pose)
        self._lidar_proto.pose.CopyFrom(lidar_pose_proto)

    def get(self) -> sensor_model_pb2.SensorOutput.LidarCloud:
        return self._lidar_proto