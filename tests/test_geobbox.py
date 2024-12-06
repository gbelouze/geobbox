"""Utilities for working with different system of coordinates."""

import pytest
from rasterio import CRS

from geobbox import UTM, GeoBoundingBox

WGS84 = CRS.from_epsg(4326)
UTM36 = UTM(36, "M").crs

geobbox_examples = (
    (0, 0, 1, 1, WGS84),
    (-1, -2, 1, 2, WGS84),
    (170, -70, 180, 0, WGS84),
    (100_000, 6_000_000, 500_000, 7_000_000, UTM36),
)


@pytest.fixture(params=geobbox_examples)
def geobbox(request):
    left, bottom, right, top, crs = request.param
    return GeoBoundingBox(left, bottom, right, top, crs)


def test_invalid_bbox_creation():
    with pytest.raises(
        ValueError,
        match="GeoBoundingBox is initialized with self.left=0 > self.right=-1",
    ):
        GeoBoundingBox(0, 0, -1, 1)
    with pytest.raises(
        ValueError,
        match="GeoBoundingBox is initialized with self.bottom=0 > self.top=-1",
    ):
        GeoBoundingBox(0, 0, 1, -1)


def test_geobbox_contains_center(geobbox):
    assert geobbox.center in geobbox


def test_geobbox_contains_corners(geobbox):
    assert geobbox.ul in geobbox
    assert geobbox.ur in geobbox
    assert geobbox.ll in geobbox
    assert geobbox.lr in geobbox


def test_geobbox_does_not_contained_buffer_corners(geobbox):
    geobbox_buffered = geobbox.buffer(1)
    assert geobbox_buffered.ul not in geobbox
    assert geobbox_buffered.ur not in geobbox
    assert geobbox_buffered.ll not in geobbox
    assert geobbox_buffered.lr not in geobbox


def test_geobbox_intersection(geobbox):
    geobbox_buffered = geobbox.buffer(1)
    assert geobbox & geobbox_buffered == geobbox


def test_geobbox_intersects(geobbox):
    ul_northing, ul_easting = geobbox.ul
    geobbox_other = geobbox.buffer(1).with_(
        left=ul_easting - 0.1, bottom=ul_northing - 0.1
    )
    assert geobbox.intersects(geobbox_other)


def test_is_contained(geobbox):
    assert geobbox.is_contained(geobbox.buffer(1))
    assert geobbox.unbuffer(0.1).is_contained(geobbox)


def test_transform_in_own_crs(geobbox):
    assert geobbox.transform(geobbox.crs) == geobbox
