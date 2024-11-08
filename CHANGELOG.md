# Changelog

All notable changes to this project will be documented in this file.

This changelog should be updated with every pull request with some information about what has been changed. These changes can be added under a temporary title 'pre-release'.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Each release can have sections: "Added", "Changed", "Deprecated", "Removed", "Fixed" and "Security".

## pre-release

### Added

- Added `mypy` pre-commit hooks [ffa9ec6](https://github.com/gbelouze/geobbox/commit/ffa9ec6d15f1eddc28861cca12db9ce1d1788322)

### Fixed

- Added `py.typed` to declare the package typed [c7988b5](https://github.com/gbelouze/geobbox/commit/c7988b532f495a09df8054e2849c576864d56eb3)

## [0.0.2] - 2024-11-04

### Added

- Added `GeoBoundingBox.__iter__` [97fda87](https://github.com/gbelouze/geobbox/commit/97fda87da1390e75a27b04a341235a627b9a8b1d)

### Fixed

- `rio.coords.GeoBoundingBox` should be `rio.coords.BoundingBox` [552e0e9](https://github.com/gbelouze/geobbox/commit/552e0e9200f9546c5f2e1e2edb1414108fcf65d2)
