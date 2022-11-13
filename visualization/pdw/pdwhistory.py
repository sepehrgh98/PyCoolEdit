from visualization.visualizationparams import DataPacket
from visualization.helper_functions import find_nearest_value_indx
import numpy as np

class PDWHistory:
    def __init__(self, is_capsulated = False):
        self._data = None
        self._time_range = None
        self._val_range = None
        self.is_capsulated = is_capsulated


    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, _data):
        self._data = _data

    @property
    def time_range(self):
        return self._time_range

    @time_range.setter
    def time_range(self, _time_range):
        self._time_range = _time_range

    @property
    def val_range(self):
        return self._val_range

    @val_range.setter
    def val_range(self, _val_range):
        self._val_range = _val_range

