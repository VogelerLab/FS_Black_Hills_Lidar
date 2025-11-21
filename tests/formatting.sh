#!/usr/bin/env bash
# Author: Daniel Rode
# Dependencies:
#   ripgrep


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Formatting/documentation tests
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Test codebase for improperly formatted Python function docstrings
rg --multiline '"""\n(\t| +)\S' ..
