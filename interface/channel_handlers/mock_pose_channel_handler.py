from __future__ import annotations

import math

import mailbox

from channel_handlers import channel_handler_base
import constants
import data_sender
import interface_errors

from simian.public.proto import spatial_pb2
from simian.public.proto.v2 import io_pb2
from simian.public.transforms import proto_util
from simian.public.transforms import spatial_py

def latlon_to_utm(lat, lon):
    # Constants
    a = 6378137.0  # WGS84 major axis
    f = 1 / 298.257223563  # WGS84 flattening
    k0 = 0.9996  # scale factor

    # Derived constants
    e = math.sqrt(f * (2 - f))  # eccentricity
    e_sq = e**2
    n = f / (2 - f)

    # Assume western hemisphere → lon is positive, so negate it to go west of Greenwich
    lon = -lon

    # UTM zone
    zone_number = int((lon + 180) / 6) + 1
    lon_origin = (zone_number - 1) * 6 - 180 + 3  # Longitude of the central meridian
    lon_origin_rad = math.radians(lon_origin)

    # Convert lat/lon to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Ellipsoid parameters
    N = a / math.sqrt(1 - e_sq * math.sin(lat_rad)**2)
    T = math.tan(lat_rad)**2
    C = e_sq / (1 - e_sq) * math.cos(lat_rad)**2
    A = math.cos(lat_rad) * (lon_rad - lon_origin_rad)

    # Meridian arc
    M = a * (
        (1 - e_sq / 4 - 3 * e_sq**2 / 64 - 5 * e_sq**3 / 256) * lat_rad
        - (3 * e_sq / 8 + 3 * e_sq**2 / 32 + 45 * e_sq**3 / 1024) * math.sin(2 * lat_rad)
        + (15 * e_sq**2 / 256 + 45 * e_sq**3 / 1024) * math.sin(4 * lat_rad)
        - (35 * e_sq**3 / 3072) * math.sin(6 * lat_rad)
    )

    # Easting
    x = k0 * N * (
        A + (1 - T + C) * A**3 / 6
        + (5 - 18 * T + T**2 + 72 * C - 58 * e_sq / (1 - e_sq)) * A**5 / 120
    ) + 500000.0

    # Northing
    y = k0 * (
        M + N * math.tan(lat_rad) * (
            A**2 / 2 + (5 - T + 9 * C + 4 * C**2) * A**4 / 24
            + (61 - 58 * T + T**2 + 600 * C - 330 * e_sq / (1 - e_sq)) * A**6 / 720
        )
    )

    return {
        "easting": x,
        "northing": y,
        "zone_number": zone_number,
        "hemisphere": "N"
    }

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
                f"Pose data not received from a log reader to the topic {constants.MOCK_POSE_TOPIC} but the `update` function on the channel handler was called."
            )
        del self._pose_proto.sections[:]
        section = self._pose_proto.sections.add()

        utm_point = latlon_to_utm(position.lat, position.long)

        x = utm_point['easting']
        y = utm_point['northing']
        x_vel = position.xvel
        y_vel = position.yvel

        # This needs to be swapped??
        yaw = math.atan2(x_vel, y_vel)

        pose3d = spatial_py.Pose3d.create_with_roll_pitch_yaw(x, y, 0, 0, 0, yaw)
        velocity3d = spatial_pb2.Screw()
        velocity3d.tx = position.xvel
        velocity3d.ty = position.yvel
        velocity3d.tz = 0
        velocity3d.rx = 0
        velocity3d.ry = 0
        velocity3d.rz = 0

        section.state.pose.CopyFrom(proto_util.pose3d_to_proto(pose3d))
        section.state.velocity.CopyFrom(velocity3d)

    def get(self) -> io_pb2.Pose:
        return self._pose_proto
