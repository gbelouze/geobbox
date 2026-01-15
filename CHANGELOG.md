# Changelog

All notable changes to this project will be documented in this file.

This changelog should be updated with every pull request with some information about what has been changed. These changes can be added under a temporary title 'pre-release'.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Each release can have sections: "Added", "Changed", "Deprecated", "Removed", "Fixed" and "Security".

## pre-release

### Fixed

- `overlapping_split` was sometimes not overlapping [a692b73](https://github.com/gbelouze/geobbox/commit/a692b73264dc1f3ee00ceaa765353fccd491ddc9)

## [0.1.1] - 2026-01-15

### Added

- `approximate_split` and `overlapping_split` utilities [5db2e0e](https://github.com/gbelouze/geobbox/commit/5db2e0e5767efa1f7124936e7d4578b57cac87d3)

### Changed

- Typecheck `GeoBoundingBox` as a tuple of 4 float [7f8482e](https://github.com/gbelouze/geobbox/commit/7f8482eec14e4b11d46b2d4f3dfa89ca46bbd4f2)

### Fixed

- Fixed `GeoBoundingBox.is_contained` [971cddd](https://github.com/gbelouze/geobbox/commit/971cddd5e3b9b5c7db8d6e699dbbf8370b040504)
- Make `pyright` happy [e6daea6](https://github.com/gbelouze/geobbox/commit/e6daea6eb7b466876897b495ed712edab1044ded)

## [0.1.0] - 2024-12-09

### Changed

- Add compatibility down to Python 3.10 [3fb6783](https://github.com/gbelouze/geobbox/commit/3fb67837fef2b3b46c573ffca20bfb6c4ab056e5)

## [0.0.4] - 2024-12-06

### Added

- Added `ruff` and `pydoclint` pre-commit hooks [f20c27d](https://github.com/gbelouze/geobbox/commit/f20c27ddb2a9292fb3a41e57c851b25310f8fa5c)
- Added tests using `pytest` [4dc7248](https://github.com/gbelouze/geobbox/commit/4dc724874180cc33cf5a456a3a864ec84dc79d9f)

### Fixed

- Fixed `GeoBoundingBox.__contains__` [4dc7248](https://github.com/gbelouze/geobbox/commit/4dc724874180cc33cf5a456a3a864ec84dc79d9f)

## [0.0.3] - 2024-11-12

### Added

- Added `mypy` pre-commit hooks [ffa9ec6](https://github.com/gbelouze/geobbox/commit/ffa9ec6d15f1eddc28861cca12db9ce1d1788322)

### Fixed

- Added `py.typed` to declare the package typed [c7988b5](https://github.com/gbelouze/geobbox/commit/c7988b532f495a09df8054e2849c576864d56eb3)
- Relaxed `conda` dependencies [308d812](https://github.com/gbelouze/geobbox/commit/308d8128206f0a68ebaeb6be9d788b2284d62c2f)

## [0.0.2] - 2024-11-04

### Added

- Added `GeoBoundingBox.__iter__` [97fda87](https://github.com/gbelouze/geobbox/commit/97fda87da1390e75a27b04a341235a627b9a8b1d)

### Fixed

- `rio.coords.GeoBoundingBox` should be `rio.coords.BoundingBox` [552e0e9](https://github.com/gbelouze/geobbox/commit/552e0e9200f9546c5f2e1e2edb1414108fcf65d2)
