import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QTableWidget

from visualization.GUI.pdw.datainformationform import DataInformationForm
from visualization.GUI.radar.radarchannel import RadarChannelForm
from visualization.visualizationparams import DataPacket

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'radar', 'radarformui.ui'))[0]


class RadarForm(QMainWindow, Form):
    def __init__(self):
        super(RadarForm, self).__init__()
        self.setupUi(self)

        self.tabWidget = QTabWidget()
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Triangular)
        self.channels = []

    @pyqtSlot(dict)
    def setup_channel(self, header):
        for _id, _info in header.items():
            radar_ch_form = RadarChannelForm(_id, _info[0])
            # if _info[0] == "Omni" or _info[0] == "DF":
            radar_ch_form.setup_TimePeriod_SCR()
            self.tabWidget.addTab(radar_ch_form, _info[0])
            self.channels.append(radar_ch_form)
        self.tabBarLayout.addWidget(self.tabWidget)

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        for channel in self.channels:
            if channel.id == data_packet.id:
                channel.feed(data_packet.key, data_packet.data)
                break
        


            
