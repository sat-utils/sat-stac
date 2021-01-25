# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.4.1] - 2021-01-24

### Changed
- Allow reading in of ItemCollections without collections

## [v0.4.0] - 2020-06-11

### Added
- README directs users who want to do large scale creation or updating of catalogs to the [PySTAC](https://github.com/azavea/pystac) library instead
- ItemCollections.asset_defnition function for printing info on assets

### Changed
- Default STAC_VERSION changed to 1.0.0-beta.1
- Item.get_filename replaced with Item.get_path which takes in single template string rather than separate `path` and `filename` arguments
- Collection.add_item() function input keywords changed `filename_template`

### Fixed
- Substitution of templates on Windows: [issue](https://github.com/sat-utils/sat-stac/issues/51)

### Removed
- Item.get_filename removed in favor of Item.get_path
- Storing search information in an ItemCollections file (and associated functions)

## [v0.3.3] - 2020-01-23

### Fixed
- Spelling of requester pays (was requestor)

## [v0.3.2] - 2020-01-22

### Changed
- sat-stac now compatible with Python3 versions < 3.6 ()
- Updated README to indicate compatability with STAC 0.9

### Removed
- Removed lone f-string to allow compatability with Python3 < 3.6

## [v0.3.1] - 2019-12-06

### Fixed
- Item constructor now properly accepts passing in the collection
- Item.substitute and item.get_filename now properly accept ${collection} as a template parameter

### Deprecated
- ItemCollection.load() is now ItemCollection.open() and behaves like Item.open() (able to read remote files)

## [v0.3.0] - 2019-09-19

### Fixed
- Loading Items now properly looks for collection at Item root level rather than in properties (STAC 0.6.0).

### Changed
- Format of saved search results now follows new [Single File STAC extension](https://github.com/radiantearth/stac-spec/tree/v0.8.0-rc1/extensions/single-file-stac).

## [v0.2.0] - 2019-07-16

### Changed
- Thing.publish() removed. Self links are not used at all (and not recommended for static catalogs)
- Thing.root() returns Thing if no root (rather than an empty list). If more than one root an error will now be thrown.
- Thing.parent() functions now return `None` if no parent (rather than an empty list). If more than one parent then an error will now be thrown.
- Internal JSON data now stored in variable called `_data` rather than `data`

## [v0.1.3] - 2019-05-04

### Added
- Items.search_geometry() function added to return search geometry
- Extension of `Item` files can now be specified in `Item.get_filename()`. Defaults to `item.json`.
- Specify STAC version by setting SATUTILS_STAC_VERSION environment variable. Currently defaults to '0.6.2'.

### Changed
- Items objects no longer require a Collection for every Item

## [v0.1.2] - 2019-02-14

### Added
- Item.download_assets() and Items.download_assets() works as download() except accepts a list of keys rather than a single key. Passing in `None` for keys will download all assets.
- requestor_pays keyword option added to Item.download() (and Items.download()). Defaults to False. Use it to acknowledge paying egress costs when downloading data from a Reqeuestor Pays bucket (e.g., Sentinel-2). If the bucket is requestor pays and this is not set to True an AccessDenied error message will occur.

## [v0.1.1] - 2019-01-15

### Added

- When adding items to a catalog the parent catalog of the item is now cached. This can greatly improve ingest speed when ingesting multiple items under the same parent, especially if the catalog is a remote catalog (i.e., updating catalog on an s3 bucket).

### Changed

- Python 3 only. With Python 2.7 going unsupported in 2020 the time has come to stop supporting 2.7. There are too many additions in Python3 that continue to make backward compatability with Python 2.7 more difficult. In the case of this release the addition of caching using `functools` made sat-stac incompatible with Python 2.7.
- More lenient version requirements for `requests` (now >=2.19.1). Otherwise can cause dependency incompatibility problems in some cases.
- Behavior of `path` and `filename` keyword arguments to Collection.add_item() has changed slightly. The components of `path` are now exclusively used to generate sub-catalogs, while `filename` is the relative filename (which could include a further subdirectory) from the last sub-catalog (it's parent). Before, it was assumed that Item files were always in a single subdirectory under it's parent catalog.
- Tutorials updated

## [v0.1.0] - 2019-01-13

Initial Release

[Unreleased]: https://github.com/sat-utils/sat-stac/compare/master...develop
[v0.4.0-rc1]: https://github.com/sat-utils/sat-stac/compare/0.3.3...v0.4.0-rc1
[v0.3.3]: https://github.com/sat-utils/sat-stac/compare/0.3.2...v0.3.3
[v0.3.2]: https://github.com/sat-utils/sat-stac/compare/0.3.1...v0.3.2
[v0.3.1]: https://github.com/sat-utils/sat-stac/compare/0.3.0...v0.3.1
[v0.3.0]: https://github.com/sat-utils/sat-stac/compare/0.2.0...v0.3.0
[v0.2.0]: https://github.com/sat-utils/sat-stac/compare/0.1.3...v0.2.0
[v0.1.3]: https://github.com/sat-utils/sat-stac/compare/0.1.2...v0.1.3
[v0.1.2]: https://github.com/sat-utils/sat-stac/compare/0.1.1...v0.1.2
[v0.1.1]: https://github.com/sat-utils/sat-stac/compare/0.1.0...v0.1.1
[v0.1.0]: https://github.com/sat-utils/sat-stac/tree/0.1.0
