from pathlib import Path
from typing import List

from .element import Element
from .exceptions import ValidationError
from .target import ImageTarget, PointTarget, RegionTarget, Target
from .types import LocateInput, OptionalRegion


def _is_coordinate(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_region(region: OptionalRegion, *, name: str) -> None:
    if region is None:
        return
    if len(region) != 4 or not all(_is_coordinate(value) for value in region):
        raise ValidationError(f"{name} must be a tuple of 4 integers")
    if region[2] <= 0 or region[3] <= 0:
        raise ValidationError(f"{name} width and height must be greater than 0")


class Auto:
    def locate(
        self,
        target: LocateInput,
        *,
        region: OptionalRegion = None,
        confidence: float = 0.8,
        timeout: float = 0,
        retry: int = 0,
    ) -> Element:
        """定位目标，返回第一个匹配的 Element"""
        return Element(self._create_target(target, region, confidence, timeout, retry))

    def locate_all(
        self,
        target: LocateInput,
        *,
        region: OptionalRegion = None,
        confidence: float = 0.8,
        timeout: float = 0,
        retry: int = 0,
    ) -> List[Element]:
        """定位目标，返回所有匹配的 Element 列表"""
        t = self._create_target(target, region, confidence, timeout, retry)

        if isinstance(t, ImageTarget):
            return [Element(t, cached_point=point) for point in t._locate_all_with_retry()]

        # PointTarget and RegionTarget only produce one result.
        return [Element(t)]

    def _create_target(
        self,
        target: LocateInput,
        region: OptionalRegion,
        confidence: float,
        timeout: float,
        retry: int,
    ) -> Target:
        _validate_region(region, name="region")

        if not 0 <= confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        if timeout < 0:
            raise ValidationError("timeout must be greater than or equal to 0")
        if retry < 0:
            raise ValidationError("retry must be greater than or equal to 0")

        if isinstance(target, tuple) and len(target) == 2:
            if not all(_is_coordinate(value) for value in target):
                raise ValidationError("point target must be a tuple of 2 integers")
            return PointTarget(target[0], target[1], search_region=region)
        if isinstance(target, tuple) and len(target) == 4:
            if not all(_is_coordinate(value) for value in target):
                raise ValidationError("region target must be a tuple of 4 integers")
            if target[2] <= 0 or target[3] <= 0:
                raise ValidationError("region target width and height must be greater than 0")
            return RegionTarget(
                target[0], target[1], target[2], target[3], search_region=region
            )
        if isinstance(target, (str, Path, bytes)):
            return ImageTarget(
                target,
                search_region=region,
                confidence=confidence,
                timeout=timeout,
                retry=retry,
            )
        raise ValidationError(f"Unsupported target type: {type(target)}")
