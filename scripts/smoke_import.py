from importlib.metadata import version

from baihe_autogui import (
    Auto,
    Element,
    ImageTarget,
    PointTarget,
    RegionTarget,
    __version__,
)


def main() -> None:
    assert Auto is not None
    assert Element is not None
    assert PointTarget is not None
    assert RegionTarget is not None
    assert ImageTarget is not None
    assert __version__ == version("baihe-autogui")


if __name__ == "__main__":
    main()
