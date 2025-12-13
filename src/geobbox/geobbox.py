"""Utilities for working with different system of coordinates."""

import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import ee
import numpy as np
import rasterio as rio
import rasterio.warp as warp
import shapely
from typing_extensions import override

from .utm import _UTM_ZONE_LETTERS, UTM

log = logging.getLogger(__name__)

if (sys.version_info.major, sys.version_info.minor) <= (3, 10):
    from collections.abc import Iterator
    from typing import TypeAlias

    from typing_extensions import Self
else:
    from collections.abc import Iterator
    from typing import Self, TypeAlias

__all__ = ["WGS84", "GeoBoundingBox"]


Coordinate: TypeAlias = tuple[float, float]


_EPSILON = 1e-10

WGS84 = rio.CRS.from_epsg(4326)

# see https://stackoverflow.com/a/71699470/24033350
if TYPE_CHECKING:
    base = tuple[float, float, float, float]
else:
    base = object


@dataclass(frozen=True)
class GeoBoundingBox(base):
    """A georeferenced bounding box.

    This is a Coordinate Reference System (crs) and the bounding box's left, bottom, right and top
    borders, expressed in that CRS.

    Attributes
    ----------

    left, bottom, right, top : float
        The borders of the bounding box.

    crs : CRS
        The CRS of the GeoBoundingBox. Defaults to WGS84.

    """

    left: float
    bottom: float
    right: float
    top: float
    crs: rio.CRS = WGS84

    def __post_init__(self):
        if self.left > self.right:
            raise ValueError(f"GeoBoundingBox is initialized with {self.left=} > {self.right=}")
        if self.bottom > self.top:
            raise ValueError(f"GeoBoundingBox is initialized with {self.bottom=} > {self.top=}")

    @override
    def __contains__(self, point: Coordinate) -> bool:  # type: ignore # pyright: ignore[reportIncompatibleMethodOverride]
        """Whether a point is contained in the bounding box.

        Expects a point in northing/easting coordinate, in a CRS consistent with the bounding box.

        """
        northing, easting = point
        return (self.left <= easting <= self.right) and (self.bottom <= northing <= self.top)

    def __and__(self, other: Self) -> Self:
        """Intersection of bounding boxes. Emits a warning if the bboxes are not in the same CRS.

        Returns
        -------

        bbox : GeoBoundingBox
            The intersection of the bboxes expressed in the first one's CRS.

        """
        if other.crs != self.crs:
            log.warning("Intersection between bounding box in different CRS.")
            other = other.transform(self.crs)
        if (
            self.right < other.left
            or other.right < self.left
            or self.top < other.bottom
            or other.top < self.bottom
        ):
            return self.__class__(0, 0, 0, 0, self.crs)
        return self.__class__(
            left=max(self.left, other.left),
            right=min(self.right, other.right),
            top=min(self.top, other.top),
            bottom=max(self.bottom, other.bottom),
            crs=self.crs,
        )

    if not TYPE_CHECKING:

        def __iter__(self):
            """Iter over a GeoBoundingBox as if a (left, bottom, right, top) tuple

            Yields
            ------

            left : float
            bottom : float
            right : float
            top : float

            .. versionadded:: 0.0.2

            """
            yield self.left
            yield self.bottom
            yield self.right
            yield self.top

    @property
    def ul(self) -> Coordinate:
        """Upper-left corner of a bounding box, in northing/easting format."""
        return (self.top, self.left)

    @property
    def ur(self) -> Coordinate:
        """Upper-right corner of a bounding box, in northing/easting format."""
        return (self.top, self.right)

    @property
    def ll(self) -> Coordinate:
        """Lower-left corner of a bounding box, in northing/easting format."""
        return (self.bottom, self.left)

    @property
    def lr(self) -> Coordinate:
        """Lower-right corner of a bounding box, in northing/easting format."""
        return (self.bottom, self.right)

    @property
    def center(self) -> Coordinate:
        """Compute the center coordinate of a bounding box, in northing/easting format.

        Returns
        -------

        center: Coordinate
            The center of the bbox expressed in the same CRS.

        """
        return ((self.top + self.bottom) / 2, (self.left + self.right) / 2)

    @property
    def area(self) -> float:
        """Simple estimation of the area of the bounding box, expressed in the units of its CRS."""
        if self.is_empty:
            return 0
        return (self.top - self.bottom) * (self.right - self.left)

    @property
    def hypotenuse(self) -> float:
        """Length of the bounding box hypotenuse."""
        return math.sqrt((self.right - self.left) ** 2 + (self.top - self.bottom) ** 2)

    @property
    def is_empty(self) -> bool:
        """Check if a bounding box has an empty interior."""
        return bool((self.right - self.left) < _EPSILON or (self.top - self.bottom) < _EPSILON)

    @property
    def is_not_empty(self) -> bool:
        """Check if a bounding box has a non empty interior."""
        return not self.is_empty

    def with_(
        self,
        left: float | None = None,
        bottom: float | None = None,
        right: float | None = None,
        top: float | None = None,
    ) -> Self:
        """Returns a modification of the bounding box with specified changes."""
        return self.__class__(
            left=left if left is not None else self.left,
            bottom=bottom if bottom is not None else self.bottom,
            right=right if right is not None else self.right,
            top=top if top is not None else self.top,
            crs=self.crs,
        )

    def iou(self, other: Self) -> float:
        """Computes the IoU (Intersection over Union) of two bounding boxes.

        Parameters
        ----------

        other : GeoBoundingBox
            An other bounding box, in the same CRS.

        Returns
        -------

        float
            The IoU, a value between 0 and 1.

        """
        inter = self & other
        i = inter.area
        u = self.area + other.area - inter.area
        return i / u

    def intersects(self, other: Self) -> bool:
        """Check if a bounding box has non-empty intersection with another.

        Parameters
        ----------
        other : GeoBoundingBox
            An other bounding box, in the same CRS.

        Returns
        -------

        bool
            True if the two bounding boxes have non empty intersection.

        """
        if other.crs != self.crs:
            log.warning(
                f"Intersection between bounding box in different CRS ({self.crs=}, {other.crs=})."
            )
            other = other.transform(self.crs)
        if self.is_empty:
            return False
        return (
            self.right > other.left
            and other.right > self.left
            and self.top > other.bottom
            and other.top > self.bottom
        )

    def is_contained(self, other: Self) -> bool:
        """Check if a bounding box is fully contained in another.

        Parameters
        ----------

        other : GeoBoundingBox
            An other bounding box, in the same CRS.

        Returns
        -------

        bool
            True if the first bounding box is fully contained in the other.

        """
        if self.crs != other.crs:
            log.warning(
                "Containment test between bounding box in different CRS "
                f"({self.crs=}, {other.crs=})."
            )
            other = other.transform(self.crs)
        return (other.left <= self.left <= self.right <= other.right) and (
            other.bottom <= self.bottom <= self.top <= other.top
        )

    def buffer(self, buff: float) -> Self:
        """Returns a bounding box increased by a given buffer in all directions.

        Parameters
        ----------

        buff : float

        Returns
        -------

        GeoBoundingBox
            The buffered bounding box.

        """
        if buff < 0:
            raise ValueError(f"Invalid buffer value {buff}. Expected a positive value.")
        return self.with_(
            left=self.left - buff,
            right=self.right + buff,
            bottom=self.bottom - buff,
            top=self.top + buff,
        )

    def unbuffer(self, buff: float) -> Self:
        """Returns a bounding box decreased by a given buffer in all directions, that is,
        the same bounding box with its outer perimeter of given width removed.

        Parameters
        ----------

        buff : float

        Returns
        -------

        GeoBoundingBox
            The unbuffered bounding box.

        """
        if buff < 0:
            raise ValueError(f"Invalid buffer value {buff}. Expected a positive value.")
        if 2 * buff >= self.right - self.left:
            raise ValueError(
                f"Invalid buffer value {buff} is greater than the half-width of the bbox."
            )
        if 2 * buff >= self.top - self.bottom:
            raise ValueError(
                f"Invalid buffer value {buff} is greater than the half-height of the bbox."
            )
        return self.with_(
            left=self.left + buff,
            right=self.right - buff,
            bottom=self.bottom + buff,
            top=self.top - buff,
        )

    def to_ee_geometry(self) -> ee.Geometry:
        """Translate a bounding box as a ee.Geometry polygon.

        Returns
        -------

        ee.Geometry
            The polygon representing the bbox in Google Earth Engine, in the same CRS.

        """
        geom = ee.Geometry.Polygon(
            [
                [
                    [self.left, self.top],
                    [self.left, self.bottom],
                    [self.right, self.bottom],
                    [self.right, self.top],
                    [self.left, self.top],
                ]
            ],
            proj=f"EPSG:{self.crs.to_epsg()}",
            evenOdd=False,
        )
        return ee.Feature(geom, {}).geometry()  # type: ignore[no-any-return]

    def to_shapely_polygon(self, in_native_crs: bool = False) -> shapely.Polygon:
        """Translate a bounding box as a ee.Geometry polygon.

        Parameters
        ----------
        in_native_crs : bool
            Whether to use the bbox CRS (True) or WGS84 coordinates (False). Defaults to False.

        Returns
        -------

        shapely.Polygon
            The shapely polygon representing the bbox coordinates in its CRS or WGS84 (depending on
            `in_native_crs`).

        Warning
        -------

        Georeferencement information is lost. The shapely polygon is just a mathematical object.

        """
        bbox = self.transform(WGS84) if not in_native_crs else self
        return shapely.box(bbox.left, bbox.bottom, bbox.right, bbox.top)

    def to_latlon(self) -> tuple[Coordinate, Coordinate]:
        """Convert a bounding box to a tuple of the form (lat_min, lon_min), (lat_max, lon_max),
        as expected by folium.

        Returns
        -------
        (lat_min, lon_min), (lat_max, lon_max) : Coordinate, Coordinate
            Coordinates of the bottom left and top right box corners, in that order.

        """
        lon_min, lon_max = self.left, self.right
        lat_min, lat_max = self.bottom, self.top
        return ((lat_min, lon_min), (lat_max, lon_max))

    def transform(self, dst_crs: rio.CRS) -> Self:
        """Transform a bounding box to `dst_crs`.

        If mapping to the new CRS generates distortions, the smallest box encapsulating the corners
        of the distorted box is returned. This is in general the smallest encapsulating box of the
        distorted box.

        Parameters
        ----------
        dst : CRS
            Target CRS.

        Returns
        -------

        bbox: GeoBoundingBox
            Bounding box in `dst_crs`.

        """
        if not self.is_not_empty:
            log.warning("Transforming an empty GeoBoundingBox")
            return self.__class__(0, 0, 0, 0, dst_crs)
        left, bottom, right, top = warp.transform_bounds(
            self.crs, dst_crs, self.left, self.bottom, self.right, self.top
        )
        return self.__class__(left=left, bottom=bottom, right=right, top=top, crs=dst_crs)

    def shape(self, scale: int) -> tuple[int, int]:
        """Compute the shape that would have an image at resolution `scale` fitting the bbox.

        Parameters
        ----------
        scale : int
            A pixel side-length, in meter.

        Returns
        -------

        height, width: int

        """
        _, meter_factor = self.crs.linear_units_factor
        w = meter_factor * (self.right - self.left) // scale
        h = meter_factor * (self.top - self.bottom) // scale
        return (h, w)

    @classmethod
    def from_ee_geometry(cls, geometry: ee.Geometry) -> Self:
        coordinates = np.array(geometry.bounds().getInfo()["coordinates"][0])  # type: ignore[index]
        proj = geometry.projection().getInfo()["crs"]  # type: ignore[index]
        crs = rio.CRS.from_string(proj)
        return cls(
            left=coordinates[:, 0].min(),
            right=coordinates[:, 0].max(),
            bottom=coordinates[:, 1].min(),
            top=coordinates[:, 1].max(),
            crs=crs,
        )

    @classmethod
    def from_latlon(cls, cmin: Coordinate, cmax: Coordinate, crs: rio.CRS = WGS84) -> Self:
        """Convert a bounding box of the form (lat_min, lon_min), (lat_max, lon_max),
        as expected by folium, to a GeoBoundingBox.

        Parameters
        ----------
        cmin : Coordinate
            Bottom left corner coordinates.
        cmax : Coordinate
            Top right corner coordinates.
        crs : CRS (optional)
            The CRS in which the coordinates are expressed. Default is WGS84.

        Returns
        -------
        GeoBoundingBox
        """
        return cls(left=cmin[1], right=cmax[1], bottom=cmin[0], top=cmax[0], crs=crs)

    @classmethod
    def ee_image_bbox(cls, image: ee.Image) -> Self:
        """Compute the bounding box of a GEE image in WGS84 CRS.

        Parameters
        ----------
        image : ee.Image
            A GEE image.

        Returns
        -------
        GeoBoundingBox
        """
        coordinates = np.array(image.geometry().bounds().coordinates().getInfo())
        return cls(
            left=coordinates[:, :, 0].min(),
            right=coordinates[:, :, 0].max(),
            top=coordinates[:, :, 1].max(),
            bottom=coordinates[:, :, 1].min(),
        )

    @classmethod
    def from_rio(cls, bbox: rio.coords.BoundingBox, crs: rio.CRS = WGS84) -> Self:
        """Get a bounding box from a `rasterio` bounding box.

        Parameters
        ----------

        bbox : GeoBoundingBox
            A rasterio bounding box object.

        crs : CRS
            The CRS in which the bbox is expressed. Default is WGS84.

        Returns
        -------

        GeoBoundingBox

        """
        return cls(left=bbox.left, bottom=bbox.bottom, right=bbox.right, top=bbox.top, crs=crs)

    @classmethod
    def from_geofile(cls, path: Path) -> Self:
        """Get a bounding box from a `rasterio`-compatible Geo file.

        Parameters
        ----------
        path : Path
            A path to a Geo file.

        Returns
        -------

        GeoBoundingBox
            The bounding box of the geodata contained in the file.

        """
        with rio.open(path) as data:
            return cls.from_rio(data.bounds, data.crs)

    @classmethod
    def from_utm(cls, utm: UTM) -> Self:
        """Get the bounding box of a UTM zone in WGS84.

        Parameters
        ----------
        utm : UTM
            The UTM zone.

        Returns
        -------

        GeoBoundingBox
            The bounding box expressed in WGS84.

        """
        left = (utm.zone - 31) * 6
        right = left + 6
        bottom = -80 + 8 * _UTM_ZONE_LETTERS.index(utm.letter)
        top = bottom + 8 if utm.letter != "X" else 84
        return cls(left=left, bottom=bottom, right=right, top=top)

    def to_utms(self) -> Iterator[UTM]:
        """Computes the UTM zones that the bounding box intersects.

        Yields
        ------

        UTM

        """
        bbox = self.transform(WGS84)
        zone_left = int(bbox.left // 6) + 31
        zone_right = int(bbox.right // 6) + 31
        letter_index_bottom = int((bbox.bottom + 80) // 8)
        letter_index_top = int((bbox.top + 80) // 8)
        for zone in range(zone_left, zone_right + 1):
            for letter_index in range(letter_index_bottom, letter_index_top + 1):
                yield UTM(zone, _UTM_ZONE_LETTERS[letter_index])
