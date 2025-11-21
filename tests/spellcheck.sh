#!/usr/bin/env bash
# Author: Daniel Rode
# Dependencies:
#   codespell
#   hunspell
#   ripgrep


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Code and comment spellcheck
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Use codespell to find common typos
codespell --check-filenames \
    --ignore-words-list lasR,ans \
    ./ ../run.sh ../docker ../bin ../lib ../hpc ../tests \
;

# Use Hunspell for a more in-depth spellcheck
rg --invert-match --no-filename --only-matching --multiline \
    --multiline-dotall '\br\(""".+?"""\)' .. \
| rg --invert-match --only-matching --multiline --multiline-dotall \
    '\br\(".+?"\)' \
| rg --only-matching '((?-m)\s*#.*|(?m)""".+?""")' \
| rg --invert-match '^#SBATCH ' \
| rg --invert-match '#!' \
| hunspell -l | sort | uniq \
| rg --only-matching --invert-match --ignore-case \
    --file spelling-ignore.txt \
;
