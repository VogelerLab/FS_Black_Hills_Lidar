# Author: Daniel Rode
# Dependencies:
#   podman 5.6.2


# Container definition for this repository's workflow.


# https://docs.docker.com/reference/dockerfile/


FROM ghcr.io/vogelerlab/fs_black_hills_lidar:v62 as bh

# Install further dependencies
RUN python3 -m pip install openpyxl

# Install BH scripts
COPY tmp-repo-clone.git /vogeler/
