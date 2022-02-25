import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from visualization.Channel.channel import Channel
# from visualization.Channel.channel import Channel
from visualization.GUI.pdwinformationbox import PDWInformationBoxForm
from visualization.GUI.pdwtools import PDWToolsForm
from visualization.visualizationparams import DataPacket, PlotInteraction

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdwui.ui'))[0]


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

        # self.ch1 = Channel(1, "a")
        # self.leftFrameLayout.addWidget(self.ch1.plot)
        # self.ch1.plot.set_interaction(PlotInteraction.Zoom)
        # self.ch1.plot.set_interaction(PlotInteraction.Drag)
        #
        # self.ch2 = Channel(2 , "b")
        # self.leftFrameLayout.addWidget(self.ch2.plot)
        #
        # x = np.linspace(0, 2 * np.pi, 2000)
        # self.ch1.plot.feed(x, np.sin(x))
        # self.ch1.data.feed(np.sin(x))
        # self.ch2.plot.feed(x, np.cos(x))

    def setup_connections(self):
        self.toolsWidget.filePathChanged.connect(self.filePathChanged)

    @pyqtSlot(dict)
    def setup_channels(self, header):
        for _id, _name in header.items():
            ch = Channel(_id, _name)
            self.channels.append(ch)
            self.leftFrameLayout.addWidget(ch.plot)
            ch.plot.set_interaction(PlotInteraction.Zoom)
            ch.plot.set_interaction(PlotInteraction.Drag)

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        for channel in self.channels:
            if channel.id == data_packet.id:
                channel.data.feed(data_packet.data)
                channel.plot.feed(data_packet.key, data_packet.data)
                break
