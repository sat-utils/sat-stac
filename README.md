# sat-stac

[![CircleCI](https://circleci.com/gh/sat-utils/sat-stac.svg?style=svg&circle-token=ef97f3eea6cf901646fc2951e5a941686456b0da)](https://circleci.com/gh/sat-utils/sat-stac) [![PyPI version](https://badge.fury.io/py/sat-stac.svg)](https://badge.fury.io/py/sat-stac) [![codecov](https://codecov.io/gh/sat-utils/sat-stac/branch/master/graph/badge.svg)](https://codecov.io/gh/sat-utils/sat-stac)

This is a Python 3 library for working with [Spatio-Temporal Asset Catalogs (STAC)](https://github.com/radiantearth/stac-spec). It can be used to

- Open and update existing catalogs
- Traverse through catalogs
- Create a new catalogs
- Add or remove a STAC Collection from a catalog
- Add or remove STAC Items from a catalog
- Create a hierarchical STAC catalog from STAC Items.

## Installation

sat-stac has minimal dependencies (`requests` and `python-dateutil`). To install sat-stac from PyPi:
sat-stac can be installed from pip or the source repository. 

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
To install a specific versions of sat-stac, install the matching version of sat-stac. 

```bash
pip install sat-stac==0.1.0
```

The table below shows the corresponding versions between sat-stac and STAC:

| sat-stac | STAC  |
| -------- | ----  |
| 0.1.x    | 0.6.x - 0.7.x |
| 0.2.x    | 0.6.x - 0.7.x |
| 0.3.x    | 0.6.x - 0.8.x |

## Tutorials

There are two tutorials. [Tutorial-1](tutorial-1.ipynb) includes an overview of how to create and manipulate STAC static catalogs. [Tutorial-2](tutorial-2.ipynb) is on the Python classes that reflect STAC entities: Catalogs, Collections, and Items.

## About
[sat-stac](https://github.com/sat-utils/sat-stac) is part of a collection of tools called [sat-utils](https://github.com/sat-utils).
