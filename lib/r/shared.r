#!/usr/bin/env Rscript
# Author: Daniel Rode


# Constants and shared R functions used throughout BH workflows.


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Point cloud initial loading filters
LIDAR_POINT_FILTER = paste(
    # LAS 1.4 classes:
    #     0: Never classified
    #     1: Unassigned
    #     2: Ground
    #     3: Low Vegetation
    #     4: Medium Vegetation
    #     5: High Vegetation
    #     6: Building
    #     7: Low Point
    #     8: Reserved
    #     9: Water
    #     10: Rail
    #     11: Road Surface
    #     12: Reserved
    #     13: Wire - Guard (Shield)
    #     14: Wire - Conductor (Phase)
    #     15: Transmission Tower
    #     16: Wire-Structure Connector (Insulator)
    #     17: Bridge Deck
    #     18: High Noise
    #     19-63: Reserved
    #     64-255: User Definable
    # (Graham, 2012)
    "-keep_extended_class 0 1 3 4 5",
    "-drop_withheld"
)
LIDAR_ATTR_FILTER = "xyzirnc"  # See https://rdrr.io/cran/lidR/man/readLAS.html

# Default Dalponte parameters
DAL_TH_SEED = 0.45
DAL_TH_CR   = 0.55

# Max crown diameter in pixels
DAL_MAX_CR = 13

# Whether tree crown outlines should have dents
CROWN_GEOM = "concave"
# CROWN_GEOM = "convex"

# How 'denty' to make the crown outlines
# "1 returns the convex hulls, 0 maximally concave hulls"
# https://r-spatial.github.io/sf/reference/geos_unary.html
CONCAVE_HULL_RATIO = 0.3

# Max window diameter for ITD LMF
Y_CAP = 15.24  # 50 feet

# Min window diameter for ITD LMF
Y_FLOOR = 2.26538933944702  # meters

# Lidar vegetation height delimiter (cut-off), in the point cloud's CRS units,
# (which is meters for the Black Hills collection). 1.37 meters is
# equivalent to 4.5 feet (breast height).
HIGHPASS_DELIM = 1.3716  # meters

# Tallest tree in Black Hills has recorded height of 160 feet (48.8 meters)
# (Woster, 2013), thus, all points higher than than can be considered noise
LOWPASS_DELIM = 50  # High noise delimiter (cut-off) for Black Hills area

# Tree minimum height (threshold below which a pixel or a point cannot be a
# local maxima)
TREE_HMIN = 2


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

window_func = function(x) {
    # Set window size smaller for lower points and larger for higher points (so
    # that tall trees have a larger window than short trees)

    # This equation's coefficients were fitted to the 1st percentile
    # (quantile 0.01) of BH tree height field data and FVS tree crown width
    # data derived from BH field data. A linear model was chosen since the
    # coefficient for the x^2 term of quadratic fits were insignificant.
    y = (0.08899321922889102 * x) + 1.52873159848727

    # Set max window diameter to 50 feet
    y[y > Y_CAP] = Y_CAP

    # Set minimum window diameter
    y[y < Y_FLOOR] = Y_FLOOR

    return(y)
}

get_smooth_chm = function(chm) {
    kernel = matrix(1, 3, 3)
    smooth_chm = terra::focal(
        chm,
        w = kernel,
        fun = median,
        na.rm = TRUE
    )
    return(smooth_chm)
}



# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# REFERENCES (APA)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#
# Graham, L. (2012). The LAS 1.4 Specification (Version 1.4) [Specification].
# ASPRS.
# https://www.asprs.org/wp-content/uploads/2010/12/LAS_Specification.pdf
#
# Woster, K. (2013, August 7). Alive or dead? tallest known Black Hills pine
# focus of questions, controversy. Rapid City Journal.
# https://rapidcityjournal.com/news/alive-or-dead-tallest-known-black-hills-
#     pine-focus-of-questions-controversy/article_9955d0fb-af61-5293-92e2-
#     103f968ad441.html
