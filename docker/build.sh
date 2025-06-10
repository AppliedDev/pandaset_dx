#!/bin/bash

set -eu

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/variables.sh"

IMAGE=$CONTAINER_NAME
TAG="$(date +'%m-%d-%y')-$(git describe --always 2> /dev/null || echo 'none')"
docker build -f "$DIR/Dockerfile" -t "$IMAGE:$TAG" "$DIR"/..
docker tag "$IMAGE:$TAG" "$IMAGE:latest"

# TODO: implement a --upload flag to upload image to cloud repo for cloud conversions.
