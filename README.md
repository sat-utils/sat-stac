# STAC

This is a Python library for working with [Spatio-Temporal Asset Catalogs (STAC)](https://github.com/radiantearth/stac-spec). It can be used to

- Open and update existing catalogs
- Traverse through catalogs
- Create a new catalogs
- Add or remove a STAC Collection from a catalog
- Add or remove STAC Items from a catalog
- Create a hierarchical STAC catalog from STAC Items.

## Installation

sat-stac cam be installed from this repository, or from PyPi using pip. It has minimal dependencies (the Python requests library only)

```bash
$ git clone https://github.com/sat-utils/sat-stac.git
$ cd sat-stac
$ pip install .
```

From pip
```bash
$ pip install satstac
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
