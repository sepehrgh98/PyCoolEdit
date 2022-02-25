import enum


class PlotInteraction(enum.Enum):
    Zoom = 1
    Drag = 2
    VerticalSelect = 3
    HorizontalSelect = 4


class DataPacket:
    def __init__(self):
        self._id = None
        self._data = None
        self._key = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, _id):
        self._id = _id

    @property
    def key(self):
        return self._key
        # self._key = _key

    @key.setter
    def key(self, _key):
        self._key = _key

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, _data):
        self._data = _data
