"""geobbox
=======

A python library for georeferenced bounding boxes.

"""

__version__ = "0.1.0"

from .geobbox import GeoBoundingBox
from .utm import UTM

__all__ = ["GeoBoundingBox", "UTM"]
