from pathlib import Path
from typing import List

from .element import Element
from .target import ImageTarget, PointTarget, RegionTarget, Target
from .types import LocateInput, OptionalRegion


class Auto:
    def __init__(self):
        self._pause = 0.1
        self._failsafe = True

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
        t = self._create_target(target, region, confidence, timeout, retry)
        return Element(t, self)

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
        from .target import ImageTarget

        t = self._create_target(target, region, confidence, timeout, retry)

        if isinstance(t, ImageTarget):
            points = t._locate_all_with_retry()
            elements = []
            for point in points:
                new_target = ImageTarget(
                    image=t.image,
                    search_region=t.search_region,
                    confidence=t.confidence,
                    timeout=t.timeout,
                    retry=t.retry,
                )
                elements.append(Element(new_target, self, cached_point=point))
            return elements

        # PointTarget 和 RegionTarget 只有 1 个
        return [Element(t, self)]

    def _create_target(
        self,
        target: LocateInput,
        region: OptionalRegion,
        confidence: float,
        timeout: float,
        retry: int,
    ) -> Target:
        if isinstance(target, tuple) and len(target) == 2:
            return PointTarget(target[0], target[1], search_region=region)
        if isinstance(target, tuple) and len(target) == 4:
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
        raise ValueError(f"Unsupported target type: {type(target)}")
