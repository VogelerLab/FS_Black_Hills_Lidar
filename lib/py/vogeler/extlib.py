#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Daniel Rode


"""Functions that depend on third-party Python libraries."""


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Import libraries
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Import standard libraries
import os
import json
import functools
from pathlib import Path
from logging import ERROR
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed

from typing import Any
from collections.abc import Callable
from collections.abc import Iterator

# Import external libraries
import dill
import pyogrio
import numpy as np
import pandas as pd
import rasterio as rio
from rasterio.fill import fillnodata
from geopandas import GeoDataFrame
from shapely import force_2d
from shapely.geometry import shape

# Import R libraries
from rpy2.robjects.packages import importr
from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
rbase = importr("base")
rmethods = importr("methods")
rpy2_logger.setLevel(ERROR)  # Suppress R warning messages


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

MAX_WORKERS = os.cpu_count()


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def run_dill(fn: Callable, *args, **kwargs) -> Any:
    """Helper function to use dill instead of pickle.

    This allows multiprocessing to accept lambda functions.
    """

    return dill.loads(fn)(*args, **kwargs)


def dispatch(
    jobs: iter, worker: Callable, max_workers=MAX_WORKERS,
) -> Iterator[(Any, Any)]:
    """Run jobs in parallel.

    Parallel apply dispatching function: Run a list of jobs with a given
    worker function, in parallel, and yield worker results in order they
    finish.
    """

    worker = functools.partial(run_dill, dill.dumps(worker))  # Allow lambdas
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures_jobs = {executor.submit(worker, j): j for j in jobs}
        for f in as_completed(futures_jobs):
            log.info("Worker finished: %s", futures_jobs[f])
            yield (futures_jobs[f], f.result())


def catgdf(gdf_list: list[GeoDataFrame]) -> GeoDataFrame:
    """Vertically concatenate list of GeoDataFrames into one GeoDataFrame."""

    # Drop empty dataframes
    gdf_list = [
        gdf for gdf in gdf_list if len(gdf) != 0
    ]

    # Handle if gdf_list is empty
    if not gdf_list:
        return GeoDataFrame()

    # Verify all CRSs match
    assert len({g.crs for g in gdf_list}) == 1

    # Concatenate GeoDataFrames
    gdf = GeoDataFrame(
        pd.concat(gdf_list, axis=0, ignore_index=True),
        crs=gdf_list[0].crs,
    )

    return gdf


def catshp(src_shp_list: list[Path], dst_shp: Path) -> None:
    """Vertically concatenate list of shapefiles; save as single shapefile."""

    # Load shapefiles
    gdf_list = [
        pyogrio.read_dataframe(shp) for shp in src_shp_list
    ]

    # Drop empty dataframes
    gdf_list = [
        gdf for gdf in gdf_list if len(gdf) != 0
    ]

    # Concatenate shapefiles and save to new file
    gdf = catgdf(gdf_list)
    gdf.to_file(dst_shp)


def fill_grid_na(
    arr: np.ndarray, neighborhood=128, fill_all=True,
) -> np.ndarray:
    """Fill-in raster NA values using nearest neighbor.

    Interpolate the nan values of a 2D or 3D Numpy array using nearest
    neighbor values. If "fill_all" is false, this function will only fill
    values within the "neighborhood" distance away from the nearest non-nan
    value; if "fill_all" is true, filling is done iteratively until all indexes
    have a non-nan value.
    """

    arr = np.copy(arr)
    while np.isnan(arr).sum() != 0:
        arr = fillnodata(
            arr, ~np.isnan(arr), max_search_distance=neighborhood,
        )
        if not fill_all:
            return arr
    return arr


def tif_m2ft(src_tif: Path, dst_tif: Path) -> None:
    """Convert rasters meters to feet.

    Convert the pixel values of a given raster from meters to feet and save
    as new raster.

    1 ft = 12 in
    100 cm = 1 m
    1 in = 2.54 cm
    1 in * 12 = 2.54 cm * 12
    12 in = 2.54 cm * 12
    1 ft = 2.54 cm * 12
    1 ft = 30.48 cm
    1 ft / 30.48 = 30.48 cm / 30.48
    1 ft / 30.48 = 1 cm
    1 ft / 30.48 * 100 = 1 cm * 100
    1 ft / 30.48 * 100 = 100 cm
    1 ft / 30.48 * 100 = 1 m
    100 ft / 30.48 = 1 m
    1 m = (100 / 30.48) ft
    """

    # Import source raster (the one with pixel values in meters)
    with rio.open(src_tif) as f:
        # Read the metadata
        profile = f.profile.copy()
        pixels = f.read()

    # Convert pixel values from meters to feet
    pixels_ft = pixels * (100 / 30.48)

    # Verify pixels' data type remained the same after value conversion
    assert pixels_ft.dtype == profile['dtype']

    # Write new raster to file
    with rio.open(dst_tif, 'w', **profile) as f:
        f.write(pixels_ft)


def update_crs_metadata(tif: Path, epsg: int) -> None:
    """Update a given raster's CRS metadata."""

    with rio.open(tif, 'r+') as f:
        f.crs = rio.crs.CRS.from_epsg(epsg).wkt


def vpc2df(src_vpc: Path) -> pd.DataFrame:
    """Convert a VPC to a DataFrame."""

    with open(src_vpc, 'r') as f:
        stac = json.load(f)

    df = []
    for asset in stac['features']:
        crs = asset['properties']['proj:wkt2']
        geom = force_2d(shape(asset['properties']['proj:geometry']))

        df += [{'crs': crs, 'geometry': geom}]

    return pd.DataFrame(df)


def get_field_and_fvs_data_from_src(
    fvs_path: Path,
) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """Import FS field data and FVS data and pre-process + join them."""

    # Import FVS tree data
    # NOTE: Column meanings:
    # https://www.fs.usda.gov/sites/default/files/essential-fvs.pdf
    fvs_trees = pd.read_excel(
        fvs_path,
        sheet_name='FVS_TreeList',
    )

    # Discard projections (assumed future) entries
    fvs_trees = fvs_trees.query('Year != 2033')

    # Import Forest Service field data
    field_data = pd.read_excel(
        './import/field_data/fseprd1221357.xlsx',
        sheet_name=None,  # Get all sheets
    )
    field_data_trees = field_data["Tree"]
    field_data_plots = field_data["Plot"]

    # Discard partial plots
    plot_coverage_map = {
        plot_id: prop
        for plot_id, prop in zip(
            field_data_plots['Plot'], field_data_plots["Proportion"]
        )
    }
    field_data_trees['Proportion'] = field_data_trees['Plot'].apply(
        lambda plot_id: plot_coverage_map[plot_id]
    )
    field_data_trees = field_data_trees.query("Proportion == 1.0")

    # Join FVS data onto field data
    fvs_trees['tree_uid'] = (
        fvs_trees['StandID'].astype(str)
        + "-" +
        fvs_trees['TreeId'].astype(str)
    )
    field_data_trees['tree_uid'] = (
        field_data_trees['Plot'].astype(str)
        + "-" +
        field_data_trees['Tree'].astype(str)
    )
    joined_data = field_data_trees.merge(fvs_trees, how='left', on='tree_uid')

    # Convert feet to meters
    joined_data['Ht_m'] = joined_data['Ht'] * 0.3048
    joined_data['Height_m'] = joined_data['Height'] * 0.3048
    joined_data['CrWidth_m'] = joined_data['CrWidth'] * 0.3048

    return fvs_trees, field_data_trees, joined_data


def order_df_cols_by_mean(df: pd.DataFrame) -> pd.DataFrame:
    """Order df columns by their mean value."""

    return df.reindex(df.mean().sort_values().index, axis=1)
