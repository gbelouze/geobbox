<!-- Do not remove the surrounding blank lines. See https://stackoverflow.com/questions/70292850/centre-align-shield-io-in-github-readme-file -->
<div align="center">

  <a href="https://github.com/psf/black">![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)</a>
  <a href="https://geobbox.readthedocs.io/en/latest/?badge=latest">![Documentation Status](https://readthedocs.org/projects/geobbox/badge/?version=latest)</a>

</div>

# Geobbox

A simple Python library to manipulate georeferenced bounding boxes.

```python
from geobbox import GeoBoundingBox
from rasterio import CRS

bbox = GeoBoundingBox(
    left = 0,
    right = 1,
    bottom = 0,
    right = 1,
    crs = CRS.from_epsg(4326)
)
```

Read the [docs](https://geobbox.readthedocs.io/en/latest/) for more details.
