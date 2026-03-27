from pathlib import Path
from typing import List, Tuple

from .element import Element
from .exceptions import ValidationError
from .overlay import overlay
from .target import (
    ImageTarget,
    MultiTarget,
    PointTarget,
    RegionTarget,
    Target,
    dedupe_match_regions,
    point_from_region,
)
from .types import LocateInput, OptionalRegion, SingleLocateInput


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
    def clear_highlights(self) -> None:
        overlay.clear()

    def locate(
        self,
        target: LocateInput,
        *,
        region: OptionalRegion = None,
        confidence: float = 0.9,
        timeout: float = 0,
        retry: int = 0,
    ) -> Element:
        targets = self._create_targets(target, region, confidence, timeout, retry)
        resolved_target = targets[0] if len(targets) == 1 else MultiTarget(targets)
        return Element(
            resolved_target,
            auto=self,
        )

    def locate_all(
        self,
        target: LocateInput,
        *,
        region: OptionalRegion = None,
        confidence: float = 0.9,
        timeout: float = 0,
        retry: int = 0,
    ) -> List[Element]:
        elements: List[Element] = []
        matched_regions: List[Tuple[int, int, int, int]] = []
        for t in self._create_targets(target, region, confidence, timeout, retry):
            if isinstance(t, ImageTarget):
                for match_region in t._locate_all_regions_with_retry():
                    deduped = dedupe_match_regions(matched_regions + [match_region])
                    if len(deduped) == len(matched_regions):
                        continue
                    matched_regions.append(match_region)
                    elements.append(
                        Element(
                            t,
                            auto=self,
                            cached_point=point_from_region(match_region),
                            cached_region=match_region,
                        )
                    )
            else:
                elements.append(Element(t, auto=self))

        return elements

    def _create_targets(
        self,
        target: LocateInput,
        region: OptionalRegion,
        confidence: float,
        timeout: float,
        retry: int,
    ) -> List[Target]:
        _validate_region(region, name="region")

        if not 0 <= confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        if timeout < 0:
            raise ValidationError("timeout must be greater than or equal to 0")
        if retry < 0:
            raise ValidationError("retry must be greater than or equal to 0")

        if isinstance(target, list):
            if not target:
                raise ValidationError("target list must contain at least one locator")
            return [
                self._create_single_target(candidate, region, confidence, timeout, retry)
                for candidate in target
            ]

        return [self._create_single_target(target, region, confidence, timeout, retry)]

    def _create_single_target(
        self,
        target: SingleLocateInput,
        region: OptionalRegion,
        confidence: float,
        timeout: float,
        retry: int,
    ) -> Target:
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
