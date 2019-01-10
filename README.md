# sat-stac

[![CircleCI](https://circleci.com/gh/sat-utils/sat-stac.svg?style=svg&circle-token=ef97f3eea6cf901646fc2951e5a941686456b0da)](https://circleci.com/gh/sat-utils/sat-stac) [![PyPI version](https://badge.fury.io/py/sat-stac.svg)](https://badge.fury.io/py/sat-stac) [![codecov](https://codecov.io/gh/sat-utils/sat-stac/branch/master/graph/badge.svg)](https://codecov.io/gh/sat-utils/sat-stac)

This is a Python library for working with [Spatio-Temporal Asset Catalogs (STAC)](https://github.com/radiantearth/stac-spec). It can be used to

- Open and update existing catalogs
- Traverse through catalogs
- Create a new catalogs
- Add or remove a STAC Collection from a catalog
- Add or remove STAC Items from a catalog
- Create a hierarchical STAC catalog from STAC Items.

## Installation

sat-stac has minimal dependencies (`requests` and `python-dateutil`). To install sat-stac from PyPi:
sat-stac cam be installed from this repository, or . 

```bash
$ pip install sat-stac
```

From source repository:

```bash
$ git clone https://github.com/sat-utils/sat-stac.git
$ cd sat-stac
$ pip install .
```


#### Versions
The initial sat-stac version is 0.1.0, which uses the STAC spec v0.6.0. To install other versions of sat-stac, install the matching version of sat-stac. 

```bash
pip install satstac==0.1.0
```

The table below shows the corresponding versions between sat-stac and STAC:

| sat-stac | STAC  |
| -------- | ----  |
| 0.1.0    | 0.6.0 |

## Tutorials

See the [Jupyter notebook tutorial](tutorial-1.ipynb) for detailed examples on how to use sat-stac to open and update existing catalogs, and create new ones.

## About
[sat-stac](https://github.com/sat-utils/sat-stac) was created by [Development Seed](<http://developmentseed.org>) and is part of a collection of tools called [sat-utils](https://github.com/sat-utils).
