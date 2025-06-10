#!/bin/bash

set -eu

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/variables.sh"

docker stop "$CONTAINER_NAME"
