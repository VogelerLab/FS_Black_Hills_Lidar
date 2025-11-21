#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Daniel Rode
# Dependencies:
#   git
#   gdalbuildvrt
#   gdaladdo
#   gdalwarp
#   pdal
#   pdal_wrench
#   fd
#   (GNU) parallel


"""Functions that depend on third-party system binaries."""


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Import libraries
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Import standard libraries
import os
import subprocess as sp
from pathlib import Path
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory

# Import external libraries
import rasterio as rio
from geopandas import GeoDataFrame


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def gdaladdo(src_tif: Path) -> None:
    """Generate pyramids for the given raster."""

    sp.run(['gdaladdo', str(src_tif)], check=True)


def gdalbuildvrt(
    src_tif_list: list[Path],
    dst_tif: Path,
    pyramids=False,
) -> None:
    """Create virtual mosaic from a list of rasters using GDAL."""

    with NamedTemporaryFile(suffix='.txt', buffering=0) as f:
        # Write list of source rasters to file
        for p in src_tif_list:
            f.write(bytes(p))
            f.write(b'\n')

        # Run GDAL to build virtual raster from source rasters
        cmd = ['gdalbuildvrt', '-input_file_list', f.name, dst_tif]
        sp.run(cmd, check=True)

    # If requested, generate pyramids for mosaic
    if pyramids:
        gdaladdo(dst_tif)


def gdal_build_vrt(*args, **kwargs):
    gdalbuildvrt(*args, **kwargs)


def build_vpc(src_las_list: list[Path], dst_vpc: Path) -> None:
    """Create virtual mosaic from a list of point cloud files.

    Uses PDAL Wrench.
    """

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Save list of file paths to temp file to pass to PDAL Wrench
        assets_list_txt = tmpdir / "assets.txt"
        with assets_list_txt.open('w') as f:
            for i in src_las_list:
                f.write(str(i))
                f.write("\n")

        # Run PDAL Wrench to build VPC
        cmd = (
            'pdal_wrench', 'build_vpc',
            '--input-file-list', assets_list_txt,
            '--output', dst_vpc,
        )
        sp.run(cmd, check=True)


def find(
    query: str,
    dir_list: list[Path],
    ignore_case=False,
    result_type=None | list[str],
    fixed_strs=False,
) -> list[Path]:
    """List files matching the given query in the given directories."""

    cmd = ['fd']
    if ignore_case:
        cmd += ['--ignore-case']
    if result_type:
        cmd += ['--type', *result_type]
    if fixed_strs:
        cmd += ['--fixed-strings']
    cmd += [str(query), *[str(d) for d in dir_list]]

    proc = sp.run(cmd, check=True, text=True, capture_output=True)

    return [Path(p) for p in proc.stdout.strip().splitlines()]


def clip_rast(
    src_tif: Path,
    dst_tif: Path,
    bounds: GeoDataFrame,
    dstnodata='nan',
) -> None:
    """Clip a given raster to a given polygon."""

    # Get raster CRS
    with rio.open(src_tif, 'r') as f:
        rast_crs = f.crs

    with TemporaryDirectory() as tmpdir:
        # Save bounds polygon to file so GDAL utility can read it
        bounds_path = Path(tmpdir, "bounds.fgb")
        bounds.to_crs(rast_crs).to_file(bounds_path)

        # Run GDAL to do clipping
        cmd = (
            'gdalwarp',
            '-cutline',
            bounds_path,
            '-crop_to_cutline',
            # '-srcnodata', 'nan',  # Doesn't need set if source defines NoData
            '-dstnodata', dstnodata,
            '-co', 'BIGTIFF=YES',
            '-co', 'COMPRESS=LZW',
            '-co', 'TILED=YES',
            str(src_tif),
            str(dst_tif),
        )
        sp.run(cmd, check=True)


def parallel(
    jobs_: list[list[str]],
    cmd_: str,
    delimiter_=';/⦿/;',
    max_workers_=os.cpu_count(),
    **kwargs,
) -> None:
    """Run a set of jobs concurrently using GNU Parallel."""

    jobs = list(jobs_)
    cmd = str(cmd_)

    if len(jobs) == 0:
        return

    jobs_str = '\0'.join(delimiter_.join(j) for j in jobs)

    parallel_cmd = [
        'parallel',
        f'--max-procs={max_workers_}',
        '--group',
        '--null',
        f'--colsep={delimiter_}',
        '--tagstring={#}',  # Uses job sequence number as tag string
        # Include other flags passed as keyword arguments by uesr
        *[
            # Flags set to `True` will simply be the flag name without any
            # value attached (so `flag=True` will become '--flag', and
            # `another_flag=something` will become '--another-flag=something')
            f'--{k.replace("_", "-")}' if kwargs[k] is True
            else f'--{k.replace("_", "-")}={kwargs[k]}'
            for k in kwargs
        ],
        # Include main executable Parallel will be calling
        cmd,
    ]
    sp.run(parallel_cmd, check=True, text=True, input=jobs_str)
