import enum
import numpy as np

class FeedMood(enum.Enum):
    main_data = 1
    select = 2
    zoom = 3

class ProgressType(enum.Enum):
    reader = 1
    parser = 2
    capsulator = 3
    visualizer = 4

class ShowPolicy(enum.Enum):
    scroll = 1
    non_scroll = 2

class PlotType(enum.Enum):
    stem = 1
    point = 2



class DataMode(enum.Enum):
    capsulated = 1
    normal = 2

ChannelUnit = {
    'TOA' : 'msec'
    ,'Omni' : 'dBm' 
    ,'DF' : 'dBm'
    ,'Freq' : 'Hz' 
    ,'PW' : 'usec' 
    ,'AOA' : 'deg' 
    ,'RRI' : 'usec' 
    ,'RRF' : 'MHz' 
    ,'CW' : 'None'
    ,'Freq_Validity' : 'None'
    ,'Amp': ' '
}

Channel_id_to_name = {}

TimeCoef = {
     'psec' : 10e-12
    ,'nsec' : 10e-9 
    ,'usec' : 10e-6
    ,'msec' : 10e-3 
    ,'sec' : 1 
}
 
class DataPacket:
    def __init__(self):
        self._id = None
        self._data = None
        self._key = None
        self._indexes = None

    def __repr__(self) -> str:
        return "DataPacket -> "+str(self._id) + " : " + str(len(self._key)) + ", " + str(len(self._data))

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

    @property
    def indexes(self):
        return self._indexes

    @indexes.setter
    def indexes(self, _indexes):
        self._indexes = _indexes




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

