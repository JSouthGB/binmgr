#!/usr/bin/env bash

set -euo pipefail

mkdir -p binmgr

echo "Building Docker image..."
docker build --no-cache -t binmgr . || {
    echo "Failed to build Docker image"
    exit 1
}

echo "Creating binary..."
docker run --rm --name container_builder \
    -v "$(pwd)/binmgr:/app/dist" \
    binmgr \
    /app/venv/bin/pyinstaller binmgr.spec

docker rmi binmgr

echo "Binary created successfully at: $(pwd)/binmgr"
