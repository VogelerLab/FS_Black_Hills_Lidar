#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Daniel Rode


"""Run list of grid metric jobs on HPC, in parallel."""


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Import libraries
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Import standard libraries
import os
import sys
import json
import logging
import hashlib
import datetime
import subprocess as sp
from pathlib import Path
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

MAX_WORKERS = int(os.environ['SLURM_NTASKS']) - 1

TILE_BUFFER = 40

SIF_PATH = Path("./bh_container.sif").resolve()
CTG_PATH = Path("./ctg.vpc").resolve()
DTM_PATH = Path("./dtm.vrt").resolve()


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def timestamp() -> str:
    """Return current date and time as string."""

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def init_logger(path=None, level=logging.INFO) -> logging.Logger:
    """Configure logging."""

    # Initialize logger, set format, and set verbosity level
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log = logging.getLogger()
    log.setLevel(level)

    # Set logger to output to stderr
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    log.addHandler(console)

    # Set logger to output to a file as well
    if path:
        file = logging.FileHandler(path, mode='a')
        file.setFormatter(fmt)
        log.addHandler(file)

    return log


def grid_metrics_chm_worker(poly_wkt: str) -> int:
    """Spawn a worker in new container to generate grid metrics for a tile."""

    # Setup job output directory and R script arguments
    poly_hash = hashlib.sha1(bytes(str(poly_wkt), 'utf8')).hexdigest()
    out_dir = Path("./export", poly_hash).resolve()
    out_dir.mkdir(exist_ok=True)

    # Setup command arguments
    cmd = (
        'srun',
        '--export=all',
        '--exclusive',
        '--nodes=1',
        '--ntasks=1',
        '--cpus-per-task=' + os.environ["SLURM_CPUS_PER_TASK"],
        '--cpu-bind=cores',
        'apptainer', 'exec',
        '--writable-tmpfs',
        str(SIF_PATH),
        '/bh/04-grid-metrics/gen-gridmet+chms.R',
        '--dtm-path', str(DTM_PATH),
        '--max-threads', os.environ["SLURM_CPUS_PER_TASK"],
        str(CTG_PATH),
        str(out_dir),
        poly_wkt,
        str(TILE_BUFFER),
    )

    # Log subprocess activity to file
    log_path = out_dir / "gen-gridmet+chms.log"
    with log_path.open('ab') as log_f:
        # Write log header
        log_header = (
            f"JOB: {poly_wkt}\n"
            f"STARTING: {timestamp()}\n\n"
        )
        log_f.write(bytes(log_header, 'utf8'))
        log_f.flush()

        if (out_dir / "DONE").exists():
            # Skip job if already done
            log_f.write("Found DONE file (job already complete)\n")
            rc = None
        else:
            # Run subprocess (job)
            p = sp.run(
                cmd,
                stdout=log_f,
                stderr=log_f,
            )
            rc = p.returncode

        # Write log footer
        log_footer = (
            f"\nFINISHED: {timestamp()}\n"
            f"EXIT CODE: {rc}\n"
        )
        log_f.write(bytes(log_footer, 'utf8'))

    return rc


def dispatch(jobs: iter, worker: Callable, max_workers=MAX_WORKERS):
    """Dispatch jobs.

    Dispatch a list of jobs with a given worker function, in parallel, and
    return the results in order of jobs list.
    """

    futures = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, j) for j in jobs]
        results = [f.result() for f in futures]

    return results


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

    # Calculate grid metrics and CHMs
    log.info("Calculating grid metrics and CHMs...")
    with open("./wkt.json") as f:
        wkt_list = json.load(f)
    dispatch(wkt_list, grid_metrics_chm_worker)

    # Print end time
    log.info("Finished")


if __name__ == "__main__":
    main()
