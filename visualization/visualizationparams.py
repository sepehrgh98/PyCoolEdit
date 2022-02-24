import enum
from typing import NamedTuple
import numpy as np


class PlotInteraction(enum.Enum):
    Zoom = 1
    Drag = 2
    VerticalSelect = 3
    HorizontalSelect = 4


class DataPacket(NamedTuple):
    id: int
    data: np.ndarray
    key: np.ndarray
