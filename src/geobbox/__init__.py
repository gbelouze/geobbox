"""geobbox
=======

A python library for georeferenced bounding boxes.

"""

__version__ = "0.1.1"

from .geobbox import GeoBoundingBox
from .split import approximate_split, overlapping_split
from .utm import UTM

__all__ = ["GeoBoundingBox", "UTM", "approximate_split", "overlapping_split"]
