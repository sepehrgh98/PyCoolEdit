import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from visualization.Channel.channelform import ChannelForm
from visualization.GUI.pdwinformationbox import PDWInformationBoxForm
from visualization.GUI.pdwtools import PDWToolsForm
from visualization.GUI.datainformationform import DataInformationForm
from visualization.visualizationparams import DataPacket, PlotInteraction, PlotMethods

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdwui.ui'))[0]


class PDWForm(QMainWindow, Form):
    filePathChanged = pyqtSignal(str)
    totalDataSizeChanged = pyqtSignal(int)

    def __init__(self):
        super(PDWForm, self).__init__()
        self.setupUi(self)

        self.infBoxWidget = PDWInformationBoxForm()
        self.toolsWidget = PDWToolsForm()
        self.dataInfoWidget = DataInformationForm()
        self.rightFrameLayout.addWidget(self.toolsWidget)
        self.rightFrameLayout.addWidget(self.infBoxWidget)
        self.dataInformationLayout.addWidget(self.dataInfoWidget)

        self.setup_connections()
        self.channels = []
        self.channels_time = None
        self.total_data_size = None
        self.total_data_range = ()

    def setup_connections(self):
        self.toolsWidget.filePathChanged.connect(self.filePathChanged)
        self.toolsWidget.filePathChanged.connect(self.dataInfoWidget.set_file_name)
        self.toolsWidget.plotDataRequested.connect(self.plot_data)
        self.totalDataSizeChanged.connect(self.dataInfoWidget.set_total_data_size)

    @pyqtSlot()
    def plot_data(self):
        for channel in self.channels:
            channel.plot.feed(self.channels_time, channel.data.get_data())

    @pyqtSlot(dict)
    def setup_channels(self, header):
        for _id, _name in header.items():
            ch = ChannelForm(_id, _name)
            self.channels.append(ch)
            self.plotLayout.addWidget(ch)
            # ch.plot.set_interaction(PlotInteraction.ZoomOnWheel)
            # ch.plot.set_interaction(PlotInteraction.Drag)
            # ch.plot.set_interaction(PlotInteraction.DoubleClick)
            # ch.plot.set_interaction(PlotInteraction.ZoomOnBox)
            ch.set_interaction(PlotInteraction.Select)
            ch.set_plot_method(PlotMethods.Scatter)

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        for channel in self.channels:
            if channel.id == data_packet.id:
                channel.feed(data_packet.key, data_packet.data)
                if self.channels_time is None:
                    self.channels_time = data_packet.key
                    self.total_data_size = len(data_packet.data)
                    self.total_data_range = (data_packet.key.min(), data_packet.key.max())
                    self.totalDataSizeChanged.emit(self.total_data_size)
