# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
[v0.1.2]: https://github.com/sat-utils/sat-stac/compare/0.1.1...v0.1.2
[v0.1.1]: https://github.com/sat-utils/sat-stac/compare/0.1.0...v0.1.1
[v0.1.0]: https://github.com/sat-utils/sat-stac/tree/0.1.0
