FROM python:3.9

# Install the Simian wheel
ARG SIMIAN_WHEEL=wheels/simian_py-0.0.1-cp39-cp39-linux_x86_64.whl
COPY ${SIMIAN_WHEEL} ${SIMIAN_WHEEL}
RUN /bin/bash -c "pip install -I ${SIMIAN_WHEEL}"

ARG STRADA_WHEEL=wheels/strada_py-0.0.1.tar.gz
COPY ${STRADA_WHEEL} ${STRADA_WHEEL}
RUN /bin/bash -c "pip install -I ${STRADA_WHEEL}"

# Install packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
  apt-get install -y --no-install-recommends \
  python3-distutils \
  python3-apt \
  ca-certificates \
  python3-rospy \
  python3-rosbag \
  ffmpeg \
  libsm6 \
  libxext6

# Install python packages
RUN pip install opencv-python utm more_itertools mypy coverage types-protobuf

# Copy python scripts
COPY interface/ /interface/
COPY scripts/ /scripts/
COPY setup.py /setup.py
COPY setup.cfg /setup.cfg
COPY pyproject.toml /pyproject.toml

# Set up interface folder as an editable package.
RUN pip install -e .