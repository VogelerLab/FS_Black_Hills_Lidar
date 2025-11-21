#!/usr/bin/env bash
# Author: Daniel Rode


# This script is a template for kicking off production of grid metrics and
# CHMS on an HPC. A container cannot spawn jobs on an HPC (not without some
# hacks), so it is best to first create a list of jobs and then spawn those
# jobs natively on the HPC, each running in their own individual container.


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# References to HPC documentation
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Submit this script as a HPC job with `sbatch`.
# HPC resources guide:
# - https://curc.readthedocs.io/en/latest/clusters/alpine/alpine-hardware.html
# SLURM documentation:
# - https://slurm.schedmd.com/sbatch.html
# - https://slurm.schedmd.com/srun.html


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# HPC SBATCH Settings/Variables
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# "sbatch will stop processing further #SBATCH directives once the first
# non-comment non-whitespace line has been reached in the script"

#SBATCH --ntasks=256
#SBATCH --cpus-per-task=2
#SBATCH --time=23:55:00


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

CONTAINER_SIF_PATH=./bh_container.sif  # Must be generated (see ./docker dir)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Prepare HPC environment
echo "Slurm Job ID: $SLURM_JOB_ID"
module purge
module load singularity

# Change directory to this one
cd "$(dirname "$0")"

# Prep jobs
args=(
    # "The --writable-tmpfs size is controlled by sessiondir max size in 
    # apptainer.conf." Default is 64 MiB.
    --writable-tmpfs
    "$CONTAINER_SIF_PATH"
    ./prep-gridmetric-jobs.py
)
apptainer exec "${args[@]}"

# Dispatch jobs
./dispatch-gridmetric-jobs.py
