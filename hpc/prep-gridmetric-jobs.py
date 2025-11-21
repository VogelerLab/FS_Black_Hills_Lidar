#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Daniel Rode


"""Generate list of grid metric tile jobs to run on HPC."""


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Import libraries
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Import standard libraries
import sys
import json
from pathlib import Path

# Import in-house libraries
from vogeler.stlib import init_logger
from vogeler.sp import build_vpc
from vogeler.sp import gdal_build_vrt

# Import external libraries
import pyogrio


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

LAS_DIR = Path("PATH_TO_DIR_WITH_CLEANED_NORMALIZED_POINT_CLOUDS_HERE")
DTM_DIR = Path("PATH_TO_DIR_WITH_CLEANED_DTM_RASTERS_HERE")
TILE_GEOMS_PATH = Path("PATH_TO_TILE_BOUNDARIES_SHAPEFILE_HERE")

CTG_PATH = Path("./ctg.vpc").resolve()
DTM_PATH = Path("./dtm.vrt").resolve()


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def main() -> None:
    # Setup logging
    global log
    log = init_logger()
    # Setup logging: Capture unhandled exceptions
    sys.excepthook = lambda e_type, e_val, e_traceback: log.critical(
        "Program terminating:", exc_info=(e_type, e_val, e_traceback)
    )

    # Print start time
    log.info("Starting...")

    # Catalog LiDAR tiles
    if not CTG_PATH.exists():
        log.info("Creating LiDAR catalog...")
        lidar_src_paths = [*LAS_DIR.glob("*.laz")]
        build_vpc(lidar_src_paths, CTG_PATH)

        # Make sure VPC catalog has the same number of paths as source
        # point cloud directory (this check will help detect partially
        # generated, and thus malformed, VPCs)
        vpc_feat_count = len(json.loads(CTG_PATH.read_text())['features'])
        assert len(lidar_src_paths) == vpc_feat_count

    # Create virtual mosaic of DTM where patched tiles replace vendor versions
    if not DTM_PATH.exists():
        log.info("Creating virtual DTM mosaic...")
        dtm_src_paths = [*DTM_DIR.glob("*.tif")]
        gdal_build_vrt(dtm_src_paths, DTM_PATH)

    # Extract polygons as WKT from tile FGB (since HPC does not have pyogrio
    # library, but it does have Python json library)
    wkt_path = Path("wkt.json")
    if not wkt_path.exists():
        log.info("Extracting WKT...")
        tiles = pyogrio.read_dataframe(TILE_GEOMS_PATH)
        with open(wkt_path, 'w') as f:
            json.dump(list(tiles.geometry.to_wkt()), f)

    # Print end time
    log.info("DONE")


if __name__ == "__main__":
    main()
