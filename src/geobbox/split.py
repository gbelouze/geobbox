import math
from collections.abc import Iterator
from typing import TypeVar

import numpy as np

from geobbox.geobbox import GeoBoundingBox


def _floor_resolution_grid(z: float, grid: float) -> float:
    return grid * int(z // grid)


def _ceil_resolution_grid(z: float, grid: float) -> float:
    return grid * math.ceil(z / grid)


T = TypeVar("T")


def as_resolution_tuple(resolution: T | tuple[T, T]) -> tuple[T, T]:
    if isinstance(resolution, tuple):
        return resolution
    return (resolution, resolution)


def snap_to_grid(bbox: GeoBoundingBox, grid: int | tuple[int, int]) -> GeoBoundingBox:
    """'Snap' the bounding box so that its bounds aligns with a given grid.

    The returned bounding box is guaranteed to contain the original bounding box.

    Parameters
    ----------
    bbox : GeoBoundingBox
    grid : int | tuple[int, int]
        Defines x_grid, y_grid to snap the x- and y-coordinates of the bbox to.

    Returns
    -------
    GeoBoundingBox
        The bounding box inflated to snap to the grid.
    """
    xgrid, ygrid = as_resolution_tuple(grid)
    return bbox.with_(
        left=_floor_resolution_grid(bbox.left, xgrid),
        right=_ceil_resolution_grid(bbox.right, xgrid),
        bottom=_floor_resolution_grid(bbox.bottom, ygrid),
        top=_ceil_resolution_grid(bbox.top, ygrid),
    )


def approximate_split(
    bbox: GeoBoundingBox, minimal_size: float, resolution_grid: int | tuple[int, int] | None = None
) -> Iterator[GeoBoundingBox]:
    """Splits a bounding box into a grid of non-overlapping sub-bounding boxes of equal size.

    Parameters
    ----------
    bbox : GeoBoundingBox
        The bounding box to be split.
    minimal_size : float
        The minimum side length for each sub-bounding box, in box coordinates.
    resolution_grid : int | tuple[int, int] | None
        If provided, ensures that the sub-bounding box boundaries are aligned to the nearest
        multiple of this value.

    Yields
    ------
    GeoBoundingBox
        The generated sub-bounding boxes, adjusted based on `resolution_grid` if applicable.

    Notes
    -----
    if `resolution_grid` is provided, the resulting grid may be bigger than the original `bbox`.

    .. versionadded:: 0.1.1
    """
    resolution_grid = as_resolution_tuple(resolution_grid) if resolution_grid is not None else None

    if resolution_grid is not None:
        bbox = snap_to_grid(bbox, resolution_grid)
        nx_split = max(1, int((bbox.right - bbox.left) // minimal_size))
        ny_split = max(1, int((bbox.top - bbox.bottom) // minimal_size))
        stridex = _ceil_resolution_grid((bbox.right - bbox.left) / nx_split, resolution_grid[0])
        stridey = _ceil_resolution_grid((bbox.top - bbox.bottom) / ny_split, resolution_grid[0])
    else:
        nx_split = max(1, int((bbox.right - bbox.left) // minimal_size))
        ny_split = max(1, int((bbox.top - bbox.bottom) // minimal_size))
        stridex = (bbox.right - bbox.left) / nx_split
        stridey = (bbox.top - bbox.bottom) / ny_split

    for x in range(nx_split):
        for y in range(ny_split):
            yield GeoBoundingBox(
                left=bbox.left + x * stridex,
                right=bbox.left + (x + 1) * stridex,
                bottom=bbox.bottom + y * stridey,
                top=bbox.bottom + (y + 1) * stridey,
                crs=bbox.crs,
            )


def overlapping_split(
    bbox: GeoBoundingBox,
    size: float,
    fraction_overlap: float = 0,
    resolution_grid: int | tuple[int, int] | None = None,
) -> Iterator[GeoBoundingBox]:
    """Split a bounding box into equally sized possibly-overlapping
    sub-bounding boxes with side equal to `size`.

    Parameters
    ----------
    bbox : GeoBoundingBox
    size : float
        The size of the sub-bounding boxes in the unit of the `bbox`. If `resolution_grid`
        is provided, this is a lower bound on the actual size.
    fraction_overlap : float
        Float ≥ 0 and < 1 giving the approximate area overlap between two neighbouring sub-bounding
        boxes. This is always a lower bound on the actual overlap.
    resolution_grid : int | tuple[int, int] | None
        If provided, ensures that the sub-bounding box boundaries are aligned to the nearest
        multiple of this value.

    Yields
    ------
    GeoBoundingBox

    Notes
    -----
    if `resolution_grid` is provided, the resulting grid may be bigger than the original `bbox`.

    .. versionadded:: 0.1.1
    """
    resolution_grid = as_resolution_tuple(resolution_grid) if resolution_grid is not None else None
    size_eff = size * (1 - fraction_overlap)

    if resolution_grid is not None:
        bbox = snap_to_grid(bbox, resolution_grid)
        size_eff_x = max(resolution_grid[0], _floor_resolution_grid(size_eff, resolution_grid[0]))
        size_eff_y = max(resolution_grid[1], _floor_resolution_grid(size_eff, resolution_grid[1]))

        size = _ceil_resolution_grid(size, math.lcm(*resolution_grid))
        lefts = np.arange(bbox.left, bbox.right, size_eff_x)
        bottoms = np.arange(bbox.bottom, bbox.top, size_eff_y)

    else:
        Lx = bbox.right - bbox.left - size
        Ly = bbox.top - bbox.bottom - size
        if Lx < 0 or Ly < 0:
            raise ValueError(
                f"Cannot fit size {size} in bbox of shape"
                f"{(bbox.right - bbox.left, bbox.top - bbox.bottom)}."
            )
        nx_split = 1 + math.ceil(Lx / (size_eff))
        ny_split = 1 + math.ceil(Ly / (size_eff))

        lefts = np.linspace(bbox.left, bbox.right - size, nx_split)
        bottoms = np.linspace(bbox.bottom, bbox.top - size, ny_split)

    for left in lefts:
        for bottom in bottoms:
            yield GeoBoundingBox(
                left=left.item(),
                right=left.item() + size,
                bottom=bottom.item(),
                top=bottom.item() + size,
                crs=bbox.crs,
            )
