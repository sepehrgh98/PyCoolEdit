from PyQt5.QtCore import pyqtSlot, QObject
from visualization.GUI.radar.radarchannel import RadarChannelForm
from visualization.GUI.radar.radarform import RadarForm
import numpy as np
from visualization.visualizationparams import DataPacket


class RadarController(QObject):
    def __init__(self, parent):
        super(RadarController, self).__init__()
        self.channels_header = None
        self.radars = []
        self.temp_data = {}
        self.temp_data_is_empty = True
        self.channels_status = False
        self.parent = parent

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        for id in self.temp_data.keys():
            if id == data_packet.id:
                (self.temp_data[id])[0] = np.concatenate([(self.temp_data[id])[0], data_packet.key], axis=0)
                (self.temp_data[id])[1] = np.concatenate([(self.temp_data[id])[1], data_packet.data], axis=0)
                break
        self.temp_data_is_empty = False
        
    def initialize_new_radar(self):
        if self.channels_header:
            radar = RadarForm(self.parent)
            radar.setup_channel(self.channels_header)
            self.radars.append(radar)
            if not self.temp_data_is_empty :
                for key, val in self.temp_data.items():
                    packet = DataPacket()
                    packet.id = key
                    packet.key = val[0]
                    packet.data = val[1]
                    radar.feed(packet)
                radar.show()

    @pyqtSlot(dict)
    def setup_channel(self, header):
        self.channels_header = header
        for _id, _info in header.items():
            self.temp_data[_id] = [np.array([]), np.array([])] # time & val
        self.channels_status = True

    @pyqtSlot()
    def reset(self):
        for _id, _name in self.temp_data.items():
            self.temp_data[_id] = [np.array([]), np.array([])] # time & val
        self.temp_data_is_empty = True

    def channels_defined(self):
        return self.channels_status

    def clear(self):
        self.channels_header = None
        self.radars = []
        self.temp_data = {}
        self.temp_data_is_empty = True
        self.channels_status = False

