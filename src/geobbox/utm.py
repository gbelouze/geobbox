"""Base class to work with UTM zones."""

import logging
import string
import sys
from dataclasses import dataclass

import rasterio as rio
import utm

if (sys.version_info.major, sys.version_info.minor) <= (3, 10):
    from typing_extensions import Self
else:
    from typing import Self

log = logging.getLogger(__name__)

__all__ = ["UTM"]

_UTM_ZONE_LETTERS = tuple(
    char for char in string.ascii_uppercase if char not in ["A", "B", "I", "O", "Y", "Z"]
)


@dataclass(frozen=True, eq=True)
class UTM:
    """Class to represent a UTM zone.

    Attributes
    ----------

    zone : int
        The zone number, between 1 and 60.

    letter : str
        The zone letter.

    See also
    --------

    `Universal Transverse Mercator
    <https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system>`_

    """

    zone: int
    letter: str

    def __post_init__(self):
        if self.letter not in _UTM_ZONE_LETTERS:
            raise ValueError(f"Invalid UTM zone letter {self.letter}.")
        if not (1 <= self.zone <= 60):
            raise ValueError(
                f"Invalid UTM zone number {self.zone}. Expected a value in the range [1, 60]."
            )
        # Frozen dataclass hack
        # :see_also: https://stackoverflow.com/questions/53756788/
        #   how-to-set-the-value-of-dataclass-field-in-post-init-when-frozen-true
        object.__setattr__(self, "_crs", None)

    def __str__(self) -> str:
        return str(self.zone) + self.letter

    @property
    def crs(self) -> rio.CRS:
        """The CRS associated to the UTM zone."""
        if self._crs is not None:  # type: ignore
            return self._crs  # type: ignore
        crs = rio.CRS.from_epsg((32600 if self.hemisphere == "N" else 32700) + self.zone)
        object.__setattr__(self, "_crs", crs)
        return self._crs  # type: ignore

    @property
    def hemisphere(self) -> str:
        """The hemisphere of the UTM region.

        Returns
        -------

        str
            "N" for northern hemisphere and "S" for southern.

        """
        return "N" if self.letter >= "N" else "S"

    def left(self) -> Self:
        """Computes the UTM region left of the current region."""
        return self.__class__((self.zone - 2) % 60 + 1, self.letter)

    def right(self) -> Self:
        """Computes the UTM region right of the current region."""
        return self.__class__(self.zone % 60 + 1, self.letter)

    @classmethod
    def from_latlon(cls, lat: float, lon: float) -> Self:
        """Computes the UTM zone encapsulating the point at the given coordinate.

        Parameters
        ----------

        lat : float
            Point latitude, between 80°S and 84°N (i.e. -80 <= lat <= 84).

        lon : float
            Point longitude, between 180°W and 180°E (i.e. -180 <= lon <= 180).

        Returns
        -------

        Self

        """
        _, _, zone, letter = utm.from_latlon(lat, lon)
        return cls(zone, letter)

    @classmethod
    def utm_hemisphere_from_crs(cls, crs: rio.CRS) -> str:
        """Computes the UTM hemisphere defined by the given `crs`.

        Parameters
        ----------

        crs : CRS
            The Coordinate Reference System, expected to be EPSG:326** or EPSG:327**.

        Returns
        -------

        str
            The hemisphere of the given UTM CRS.

        """
        epsg = crs.to_epsg()
        if 32600 < epsg <= 32660:
            return "N"
        if 32700 < epsg <= 32760:
            return "S"
        raise ValueError(f"{crs} is not a UTM local CRS.")

    @classmethod
    def utm_zone_from_crs(cls, crs: rio.CRS) -> int:
        """Computes the UTM zone defined by the given `crs`.

        Parameters
        ----------

        crs : CRS
            The Coordinate Reference System, expected to be EPSG:326** or EPSG:327**.

        Returns
        -------

        int
            The zone number of the given CRS.

        """
        epsg: int = crs.to_epsg()
        if not (32600 < epsg <= 32660 or 32700 < epsg <= 32760):
            raise ValueError(f"{crs} is not a UTM local CRS.")
        return epsg % 100

    @classmethod
    def is_utm_crs(cls, crs: rio.CRS) -> bool:
        """Whether the given `crs` is a UTM local CRS."""
        epsg: int = crs.to_epsg()
        return 32600 < epsg <= 32660 or 32700 < epsg <= 32760

    @classmethod
    def utm_strip_name_from_crs(cls, crs: rio.CRS) -> str:
        return f"UTM{cls.utm_zone_from_crs(crs)}{cls.utm_hemisphere_from_crs(crs)}"
