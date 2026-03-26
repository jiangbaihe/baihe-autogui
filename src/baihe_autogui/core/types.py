from pathlib import Path
from typing import Optional, Tuple, Union

PointInput = Tuple[int, int]
RegionInput = Tuple[int, int, int, int]
ImageInput = Union[str, Path, bytes]
LocateInput = Union[PointInput, RegionInput, ImageInput]
OptionalRegion = Optional[RegionInput]
