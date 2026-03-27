from baihe_autogui.core.types import (
    ImageInput,
    OptionalRegion,
    PointInput,
    RegionInput,
)


def test_types_point_input():
    """PointInput is a tuple of 2 integers"""
    point: PointInput = (100, 200)
    assert len(point) == 2
    assert isinstance(point[0], int)
    assert isinstance(point[1], int)


def test_types_region_input():
    """RegionInput is a tuple of 4 integers"""
    region: RegionInput = (100, 200, 300, 400)
    assert len(region) == 4
    assert all(isinstance(x, int) for x in region)


def test_types_image_input_str():
    """ImageInput accepts string path"""
    image: ImageInput = "path/to/image.png"
    assert isinstance(image, str)


def test_types_optional_region():
    """OptionalRegion can be None or RegionInput"""
    region: OptionalRegion = (0, 0, 800, 600)
    none_region: OptionalRegion = None
    assert region is not None
    assert none_region is None
