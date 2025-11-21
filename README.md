
# Description

This code documents the workflow used for processing lidar data from Black
Hills National Forest as part of a contract between Vogeler Lab and The
U.S. Forest Service.

## Directory Structure

- `run.sh`: Example bootstrap script
- `bin/`: Workflow executable scripts/utilities
- `docker/`: Code and schematics for compiling this repository into a container
- `hpc/`: Extra code and tweaks needed to get this workflow running on an HPC
- `lib/`: In-house libraries developed for this workflow (called by scripts
					under `bin/`)
- `tests/`: Some test scripts used to validate proper code style and integrity

# Getting Started

See `run.sh` for an example of how to get the workflow running.

# References

```bib
# Fekety, P. A., Falkowski, M. J., Hudak, A. T., Jain, T. B., & Evans, J. S.
# (2018). Transferability of Lidar-derived Basal Area and Stem Density Models
# within a Northern Idaho Ecoregion. Canadian Journal of Remote Sensing, 44(2),
# 131–143.
# https://doi.org/10.1080/07038992.2018.1461557
@article{fekety2018transferability,
	title = {Transferability of lidar-derived basal area and stem density models
	         within a northern Idaho ecoregion},
	author = {Fekety, Patrick A and Falkowski, Michael J and Hudak, Andrew T and
	          Jain, Theresa B and Evans, Jeffrey S},
	journal = {Canadian Journal of Remote Sensing},
	volume = {44},
	number = {2},
	pages = {131--143},
	year = {2018},
	publisher = {Taylor \& Francis},
}

# Graham, L. (2012). The LAS 1.4 Specification (Version 1.4) [Specification].
# ASPRS.
# https://www.asprs.org/wp-content/uploads/2010/12/LAS_Specification.pdf
@misc{graham_14_2012,
	type = {{LAS}},
	title = {{LAS} 1.4 {Specification}},
	url = {https://www.asprs.org/wp-content/uploads/2010/12/LAS_Specification.pdf},
	urldate = {2025-05-08},
	publisher = {ASPRS},
	author = {Graham, Lewis},
	month = feb,
	year = {2012},
}

# Khosravipour, A., Skidmore, A. K., Isenburg, M., Wang, T., & Hussin, Y. A.
# (2014). Generating pit-free canopy height models from airborne lidar.
# Photogrammetric Engineering & Remote Sensing, 80(9), 863-872.
# https://www.ingentaconnect.com/content/asprs/pers/2014/00000080/00000009/
#     art00003?crawler=true
@article{khosravipour2014generating,
	title = {Generating pit-free canopy height models from airborne lidar},
	author = {Khosravipour, Anahita and Skidmore, Andrew K and Isenburg, Martin
	          and Wang, Tiejun and Hussin, Yousif A},
	journal = {Photogrammetric Engineering \& Remote Sensing},
	volume = {80},
	number = {9},
	pages = {863--872},
	year = {2014},
	publisher = {American Society for Photogrammetry and Remote Sensing},
}

# The lidR package. (n.d.). Retrieved January 8, 2025, from
# https://r-lidar.github.io/lidRbook/
@misc{noauthor_lidr_nodate,
	title = {The {lidR} package},
	url = {https://r-lidar.github.io/lidRbook/},
	abstract = {A guide to the lidR package},
	urldate = {2025-01-08},
}

Tange, O. (2024, November 22). GNU Parallel 20241122 ('Ahoo Daryaei'). Zenodo.
https://doi.org/10.5281/zenodo.14207479
@software{tange_2024_14207479,
	author = {Tange, Ole},
	title = {GNU Parallel 20241122 ('Ahoo Daryaei')},
	month = Nov,
	year = 2024,
	note = {{GNU Parallel is a general parallelizer to run multiple serial
	        command line programs in parallel without changing them.}},
	publisher = {Zenodo},
	doi = {10.5281/zenodo.14207479},
	url = {https://doi.org/10.5281/zenodo.14207479},
}

# Woster, K. (2013, August 7). Alive or dead? tallest known Black Hills pine
# focus of questions, controversy. Rapid City Journal.
# https://rapidcityjournal.com/news/alive-or-dead-tallest-known-black-hills-
#     pine-focus-of-questions-controversy/article_9955d0fb-af61-5293-92e2-
#     103f968ad441.html
@misc{woster_alive_2013,
	title = {Alive or dead? {Tallest} known {Black} {Hills} pine focus of
	         questions, controversy},
	shorttitle = {Alive or dead?},
	url = {
	       https://rapidcityjournal.com/news/alive-or-dead-tallest-known-black-hills-pine-focus-of-questions-controversy/article_9955d0fb-af61-5293-92e2-103f968ad441.html
	       },
	abstract = {In a peaceful valley in southwest Custer State Park, the tallest
	            known Ponderosa pine tree in the Black Hills towers above the
	            landscape.},
	language = {en},
	urldate = {2024-06-11},
	journal = {Rapid City Journal},
	author = {Woster, Kevin},
	month = aug,
	year = {2013},
}
```
