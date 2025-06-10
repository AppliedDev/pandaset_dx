#!/bin/bash

set -eu

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/variables.sh"

LOGS_MOUNT_STR=""
if [[ ${1-} == "--logs" ]]; then
  LOGS_MOUNT_STR="--mount type=bind,source=$2,target=/logs/"
fi

IMAGE="$CONTAINER_NAME:latest"

# TODO: Mount credentials to access raw logs if necessary
# Ex: --mount type=bind,source="$(realpath ~)"/.aws,target=/root/.aws/ \
docker run -id --rm --network host --name "$CONTAINER_NAME" \
  "$LOGS_MOUNT_STR" \
  --mount type=bind,source="$(realpath .)"/interface,target=/interface/ \
  --mount type=bind,source="$(realpath .)"/scripts,target=/scripts/ \
  -w /interface \
  "$IMAGE"
