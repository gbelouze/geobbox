import pytest
from rasterio.crs import CRS

from geobbox import GeoBoundingBox, approximate_split, overlapping_split


@pytest.fixture
def integer_bbox():
    """Returns a standard 10x10 bounding box."""
    return GeoBoundingBox(left=0, right=10, bottom=0, top=10, crs=CRS.from_string("EPSG:4326"))


@pytest.fixture
def non_integer_bbox():
    """Returns a bounding box with non-integer coordinates."""
    return GeoBoundingBox(
        left=0.3, right=9.7, bottom=1.2, top=10.8, crs=CRS.from_string("EPSG:4326")
    )


@pytest.fixture
def wide_bbox():
    """Returns a highly skewed bounding box (wide but short)."""
    return GeoBoundingBox(left=0, right=20, bottom=0, top=2, crs=CRS.from_string("EPSG:4326"))


@pytest.fixture
def tall_bbox():
    """Returns a highly skewed bounding box (tall but narrow)."""
    return GeoBoundingBox(left=0, right=2, bottom=0, top=20, crs=CRS.from_string("EPSG:4326"))


@pytest.mark.parametrize(
    "bbox_fixture", ["integer_bbox", "non_integer_bbox", "wide_bbox", "tall_bbox"]
)
@pytest.mark.parametrize("minimal_size", [2, 2.5])
@pytest.mark.parametrize("resolution_grid", [None, 3, (1, 2)])
def test_approximate_split(request, bbox_fixture, minimal_size, resolution_grid):
    """Test approximate_split on different bounding boxes with various settings."""
    bbox: GeoBoundingBox = request.getfixturevalue(bbox_fixture)
    subboxes = list(approximate_split(bbox, minimal_size, resolution_grid))

    # Check that all splits have the same area
    areas = [split_bbox.area for split_bbox in subboxes]
    assert all(pytest.approx(area, rel=1e-6) == areas[0] for area in areas)

    # Check that splits are non overlapping
    for i, b1 in enumerate(subboxes[:-1]):
        for b2 in subboxes[i + 1 :]:
            assert (b1 & b2).is_empty, f"Bounding boxes {b1} and {b2} should not overlap"

    for subbox in subboxes:
        assert (
            2 * minimal_size
            > subbox.right - subbox.left
            >= min(minimal_size, bbox.right - bbox.left)
        )
        assert (
            2 * minimal_size
            > subbox.top - subbox.bottom
            >= min(minimal_size, bbox.top - bbox.bottom)
        )

        # If resolution_grid is set, check alignment
        if resolution_grid is not None:
            xres, yres = (
                resolution_grid
                if isinstance(resolution_grid, tuple)
                else (resolution_grid, resolution_grid)
            )
            assert subbox.left % xres == 0
            assert subbox.right % xres == 0
            assert subbox.bottom % yres == 0
            assert subbox.top % yres == 0


@pytest.mark.parametrize(
    "bbox_fixture", ["integer_bbox", "non_integer_bbox", "wide_bbox", "tall_bbox"]
)
@pytest.mark.parametrize("size", [2, 2.5])
@pytest.mark.parametrize("fraction_overlap", [0, 0.2, 0.5])
@pytest.mark.parametrize("resolution_grid", [None, 3, (1, 2)])
def test_overlapping_split(request, bbox_fixture, size, fraction_overlap, resolution_grid):
    """Test overlapping_split on different bounding boxes with various settings."""
    bbox: GeoBoundingBox = request.getfixturevalue(bbox_fixture)
    if resolution_grid is None and (
        (bbox.top - bbox.bottom < size) or (bbox.right - bbox.left < size)
    ):
        with pytest.raises(ValueError, match=r"Cannot fit .*"):
            subboxes = list(overlapping_split(bbox, size, fraction_overlap, resolution_grid))
        return
    subboxes = list(overlapping_split(bbox, size, fraction_overlap, resolution_grid))

    # Check that all sub-bounding boxes have the correct size
    for subbox in subboxes:
        if resolution_grid is None:
            assert pytest.approx(subbox.right - subbox.left, rel=1e-6) == size
            assert pytest.approx(subbox.top - subbox.bottom, rel=1e-6) == size
            assert (bbox & subbox).area == subbox.area

        # If resolution_grid is set, check alignment
        if resolution_grid is not None:
            assert subbox.right - subbox.left >= size
            assert subbox.top - subbox.bottom >= size

            xres, yres = (
                resolution_grid
                if isinstance(resolution_grid, tuple)
                else (resolution_grid, resolution_grid)
            )
            assert subbox.left % xres == 0
            assert subbox.right % xres == 0
            assert subbox.bottom % yres == 0
            assert subbox.top % yres == 0

    # Check that all bounding boxes remain within or cover the original bbox
    total_bbox = GeoBoundingBox(
        left=min(b.left for b in subboxes),
        right=max(b.right for b in subboxes),
        bottom=min(b.bottom for b in subboxes),
        top=max(b.top for b in subboxes),
        crs=bbox.crs,
    )
    assert bbox.is_contained(total_bbox)
