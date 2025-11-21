#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Daniel Rode


"""Constants used throughout BH workflows.

See `find-2od-constants` for how constant values were determined.
"""


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Individual tree detection and crown segmentation tile buffer
TAO_PLOT_BUFF = 17.5  # meters

# Height to DBH threshold for Forest Service BH field plots
BIG_TREE_DBH_Z_METERS = 7.816541541647245  # meters

# DBH to height threshold for experimental forest half-acre plot data
EFOREST_BIG_TREE_DBH_Z_METERS = 4.8535857283086195  # meters

# Experimental Forest data half-acre plot radius
EFOREST_PLOT_RADIUS = 25.37867615948758

# Min window diameter for ITD LMF (based on minimum crown diameter found in
# FVS outputs from BH FS field data where tree heights were measured)
Y_FLOOR = 2.26538933944702  # meters
