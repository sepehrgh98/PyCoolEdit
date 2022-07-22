import enum
import numpy as np



class FeedMood(enum.Enum):
    main_data = 1
    select = 2

class ProgressType(enum.Enum):
    reader = 1
    parser = 2
    visualizer = 3


ChannelUnit = {
    'TOA' : 'sec'
    ,'Omni' : 'dBm' 
    ,'DF' : 'dBm'
    ,'Freq' : 'Hz' 
    ,'PW' : 'usec' 
    ,'AOA' : 'deg' 
    ,'RRI' : 'usec' 
    ,'RRF' : 'MHz' 
}
 
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

    @key.setter
    def key(self, _key):
        self._key = _key

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, _data):
        self._data = _data


class SignalDataPacket:
    def __init__(self):
        self._id = None
        self._key = None
        self._data = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, _id):
        self._id = _id

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, _key):
        self._key = _key

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, _data):
        self._data = _data

