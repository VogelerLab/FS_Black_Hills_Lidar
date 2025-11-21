#!/usr/bin/env bash
# Dependencies:
#   bash 4+


# Example script that shows the general way to setup the workflow container
# and run the workflow script inside of it using Podman.

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Shell settings
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

set -e  # Exit on error
set -x  # Echo script lines as they are executed


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# VENDOR_DIR defines path to where vendor source data reside.
# It is the folder that contains these folders:
#   USGS_SD_BlackHills_Preliminary_Delivery_Block1_09272023
#   USGS_SD_BlackHills_Preliminary_Delivery_Block2
VENDOR_DIR=PATH/TO/VENDOR/DATA

# RSTOR_BH_DIR defines path to Vogeler Labs in-house assets used in processing
RSTOR_BH_DIR=/mnt/n/RStor/jvogeler/Lab/projects/BH

# DST defines path to where products and intermediate files should be stored
DST_1OD=./export_1od
DST_2OD=./export_2od

# Configure container
CON_IMG=ghcr.io/vogelerlab/fs_black_hills_lidar:latest
CON_SETTINGS=(
    --rm
    --interactive --tty
    --volume "$VENDOR_DIR:/import/vendor:ro"
    --volume "$RSTOR_BH_DIR:/import/rstor:ro"
    --volume "$(pwd):$(pwd)"
    --workdir "$(pwd)"
    "$CON_IMG"
)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

function main {
    # Run first order derivatives workflow
    nice --adjustment 15 podman run "${CON_SETTINGS[@]}" workflow1 "$DST_1OD"

    # Run second order derivatives workflow
    nice --adjustment 15 podman run "${CON_SETTINGS[@]}" workflow2 "$DST_2OD"
}
main |& tee -a ./run.log
