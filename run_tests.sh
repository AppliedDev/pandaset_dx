#!/bin/bash

set -eu

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/docker/variables.sh"

docker exec -it $CONTAINER_NAME coverage run -m unittest discover -p '*_test.py' -s /interface
docker exec -it $CONTAINER_NAME coverage report -i
