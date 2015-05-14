#!/bin/bash
set -o errexit
set -p nounset

# Configuration

: ${APP_PORT:="80"} # Default to listening on port 80


# Constants

CONTAINER_PORT=8000
CONTAINER_IMAGE="krallin/webhooks-training-app"


# Library function

command_exists() {
  command -v "$@" > /dev/null 2>&1
}


# Ensure we have curl

if command_exists apt-get; then
  apt-get update
  apt-get install -y curl
elif command_exists yum; then
  yum install -y curl
fi


# Install Docker

curl -sSL https://get.docker.com/ | sh

# Run the app

docker run -d -p "${APP_PORT}:${CONTAINER_PORT}" "${CONTAINER_IMAGE}"

