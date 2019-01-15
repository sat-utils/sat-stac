# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.1.1] - 2019-01-15

### Added

- When adding items to a catalog the parent catalog of the item is now cached. This can greatly improve ingest speed when ingesting multiple items under the same parent, especially if the catalog is a remote catalog (i.e., updating catalog on an s3 bucket).

### Changed

- More lenient version requirements for `requests` (now <=2.19.1). Otherwise can cause dependency incompatibility problems in some cases.
- Behavior of `path` and `filename` keyword arguments to Collection.add_item() has changed slightly. The components of `path` are now exclusively used to generate sub-catalogs, while `filename` is the relative filename (which could include a further subdirectory) from the last sub-catalog (it's parent). Before, it was assumed that Item files were always in a single subdirectory under it's parent catalog.
- Tutorials updated

## [v0.1.0] - 2019-01-13

Initial Release

[Unreleased]: https://github.com/sat-utils/sat-stac/compare/master...develop
[v0.1.1]: https://github.com/sat-utils/sat-api/compare/0.1.0...v0.1.1
[v0.1.0]: https://github.com/sat-utils/sat-stac/tree/0.1.0