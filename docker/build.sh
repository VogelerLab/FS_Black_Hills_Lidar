#!/usr/bin/env bash
# Author: Daniel Rode
# Dependencies:
#   podman 5.6.2
#   git


# Package up the workflow in this repository into a container.


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

WORKFLOW_VERSION=v80


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Use Podman instead of Docker
function docker {
    podman "$@"
}


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Configure Bash
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Exit on error
set -e


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Change directory to where this script is
cd "$(dirname "$0")"

# Clone BH workflow code
echo "Getting BH code..."
current_commit="$(git rev-parse HEAD)"
git clone "file://$PWD/.." ./tmp-repo-clone.git
git -C ./tmp-repo-clone.git checkout "$current_commit"
rm -fr ./tmp-repo-clone.git/.git
function cleanup {
    rm -fr ./tmp-repo-clone.git
}
trap cleanup EXIT

# Build container
echo "Building BH container..."
docker build \
    --label "bh_workflow_git_commit=$current_commit" \
    --tag "vogeler-lab/bh-lidar-workflow:latest" \
    --tag "vogeler-lab/bh-lidar-workflow:$WORKFLOW_VERSION" \
    --target bh . \
;
