import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from Channel.channel import Channel
from GUI.pdwinformationbox import PDWInformationBoxForm
from GUI.pdwtools import PDWToolsForm
from visualizationparams import DataPacket, PlotInteraction

Form = uic.loadUiType(os.path.join(os.getcwd(), 'GUI', 'pdwui.ui'))[0]


class PDWForm(QMainWindow, Form):
    filePathChanged = pyqtSignal(str)

    def __init__(self):
        super(PDWForm, self).__init__()
        self.setupUi(self)

        self.infBoxWidget = PDWInformationBoxForm()
        self.toolsWidget = PDWToolsForm()
        self.rightFrameLayout.addWidget(self.toolsWidget)
        self.rightFrameLayout.addWidget(self.infBoxWidget)

        self.setup_connections()
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

    def setup_connections(self):
        self.toolsWidget.filePathChanged.connect(self.filePathChanged)

    @pyqtSlot(dict)
    def setup_channels(self, header):
        print("header:", header)
        for _id, _name in header.items():
            ch = Channel(_id, _name)
            self.channels.append(ch)
            self.leftFrameLayout.addWidget(ch.plot)
            ch.plot.set_interaction(PlotInteraction.Zoom)
            ch.plot.set_interaction(PlotInteraction.Drag)

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        print(data_packet.id, len(data_packet.key), len(data_packet.data))
        for channel in self.channels:
            if channel.id == data_packet.id:
                channel.data.feed(data_packet.data)
                channel.plot.feed(data_packet.key, data_packet.data)
                break
