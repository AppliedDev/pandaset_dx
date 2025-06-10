#!/bin/bash

set -eu

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/docker/variables.sh"

docker exec -it $CONTAINER_NAME mypy . --explicit-package-bases
