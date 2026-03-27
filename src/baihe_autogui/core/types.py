from pathlib import Path
from typing import List, Optional, Tuple, Union

PointInput = Tuple[int, int]
RegionInput = Tuple[int, int, int, int]
ImageInput = Union[str, Path, bytes]
SingleLocateInput = Union[PointInput, RegionInput, ImageInput]
LocateInputList = List[SingleLocateInput]
LocateInput = Union[SingleLocateInput, LocateInputList]
OptionalRegion = Optional[RegionInput]
