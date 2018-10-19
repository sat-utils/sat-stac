# STAC

This is a Python library for the creation and manipulation of Spatio-Temporal Asset Catalogs (STAC).

## Overview

sat-stac is a library for the programmatic creation of STAC catalogs.

- Open an existing catalog
- Create a new empty catalog
- Add or remove a STAC Collection from a catalog
- Add or remove STAC Items from a Collection


- Create static STAC files in hierarchy from unlinked STAC Items.

## Installation

sat-stac is pip installable, and has minimal dependencies (the Python requests library only)

```
$ pip install satstac
```


## Use

The main STAC classes: Catalog, Collection, and Item, can be be opened directly from JSON files or they can created from JSON-serializable dictionaries. Opening from a file has the advantage of automatically being able to link to other STAC files, such as a collection or a parent catalog.

Open a catalog and retrieve collections

```
import stac

cat = stac.Catalog('catalog.json')

print(cat.children)
```


### Creating a new STAC catalog from STAC Items





### Python Classes

The Python classes correspond to the different STAC constructs, with some additional classes due to implementation.

- **Thing**: A Thing is not a STAC object, it is a low-level parent class that is used by Catalog, Collection, and Item and includes the attributes they all have in common (read and save JSON, get links).
- **Catalog**: A catalog is the simplest STAC object, containing an id, a description, the STAC version, and a list of links.
- **Collection**: A Collection is a STAC catalog with some additional fields that describe a group of data, such as the provider, license, along with temporal and spatial extent.
- **Item**: The Item class implements the STAC Item, and has several convenience functions such as retrieving the collection, getting assets by common band name (if using the EO Extension)
- **Items**: The Items class does not correspond to a STAC object. It is a FeatureCollection of `Item`s, possibly from multiple collections. It is used to save and load sets of `Item`s as a FeatureCollection file, along with convenicen functions for extracting info across the set.




## About
[sat-stac](https://github.com/sat-utils/sat-stac) was created by [Development Seed](<http://developmentseed.org>) and is part of a collection of tools called [sat-utils](https://github.com/sat-utils).
