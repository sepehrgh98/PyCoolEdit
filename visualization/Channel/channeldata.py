import numpy as np
from PyQt5.QtCore import pyqtSlot


class ChannelData:
    def __init__(self, _id, _name):
        self._id = _id
        self._name = _name
        self._data = None
        self.range = ()

    @pyqtSlot(np.ndarray)
    def feed(self, data):
        self._data = data
        self.set_range(data.min(), data.max())

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, a):
        if not isinstance(a, int):
            raise ValueError("id must be integer!")
        self._id = a

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, a):
        if not isinstance(a, str):
            raise ValueError("name must be integer!")
        self._name = a

    def get_data(self):
        return self._data

    def set_range(self, dmin, dmax):
        self.range = (dmin, dmax)
