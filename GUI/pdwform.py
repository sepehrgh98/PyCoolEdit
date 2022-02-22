from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from GUI.pdwinformationbox import PDWInformationBoxForm
from GUI.pdwtools import PDWToolsForm
from PyQt5.QtCore import pyqtSlot
from Channel.channel import Channel
from visualizationparams import DataPacket
import os

Form = uic.loadUiType(os.path.join(os.getcwd(), 'GUI', 'pdwui.ui'))[0]


class PDWForm(QMainWindow, Form):
    def __init__(self):
        super(PDWForm, self).__init__()
        self.setupUi(self)

        self.infBoxWidget = PDWInformationBoxForm()
        self.toolsWidget = PDWToolsForm()
        self.rightFrameLayout.addWidget(self.toolsWidget)
        self.rightFrameLayout.addWidget(self.infBoxWidget)

        self.channels = []

        # self.plot1 = ChannelForm()
        # self.leftFrameLayout.addWidget(self.plot1)
        # self.plot1.set_interaction(PlotInteraction.Zoom)
        # self.plot1.set_interaction(PlotInteraction.Drag)
        #
        # self.plot2 = ChannelForm()
        # self.leftFrameLayout.addWidget(self.plot2)
        #
        # x = np.linspace(0, 2 * np.pi, 2000)
        # self.plot1.feed(x, np.sin(x))
        # self.plot2.feed(x, np.cos(x))

    @pyqtSlot(dict)
    def setup_channels(self, header):
        for _id, _name in header.items():
            self.channels.append(Channel(_id, _name))

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        for channel in self.channels:
            if channel.id == data_packet.id:
                channel.data.feed(data_packet.data)
                channel.plot.feed(data_packet.key, data_packet.data)
                break
