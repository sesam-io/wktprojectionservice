#!/usr/bin/env bash
set -e

TAG=${TAG-latest}
DOCKER_BUILD=${DOCKER_BUILD-1}
DOCKER_BUILD_PUSH=${DOCKER_BUILD_PUSH-0}

if [ $DOCKER_BUILD -eq 1 ]; then
  docker build $DOCKER_BUILD_OPTIONS -t sesambuild/wktprojectionservice:$TAG .
fi
if [ $DOCKER_BUILD_PUSH -eq 1 ]; then
  docker push sesambuild/wktprojectionservice:$TAG
fi
