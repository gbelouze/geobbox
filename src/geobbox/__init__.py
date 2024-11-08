"""
geobbox
========

A python library for georeferenced bounding boxes.
"""

__version__ = "0.0.2"

from .geobbox import GeoBoundingBox
from .utm import UTM

__all__ = ["GeoBoundingBox", "UTM"]
