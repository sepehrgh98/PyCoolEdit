from PyQt5.QtCore import pyqtSlot, QObject

from visualization.visualizationparams import DataPacket


class RadarController(QObject):
    def __init__(self):
        super(RadarController, self).__init__()

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        print(data_packet)
