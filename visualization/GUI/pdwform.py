import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from visualization.Channel.channel import Channel
from visualization.GUI.pdwinformationbox import PDWInformationBoxForm
from visualization.GUI.pdwtools import PDWToolsForm
from visualization.GUI.datainformationform import DataInformationForm
from visualization.visualizationparams import DataPacket
from matplotlib.figure import Figure
from visualization.GUI.subplotwidget import SubPlotWidget
import numpy as np

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdwui.ui'))[0]


def find_nearest_value_indx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


class PDWForm(QMainWindow, Form):
    filePathChanged = pyqtSignal(str)
    totalDataSizeChanged = pyqtSignal(int)
    dataRequested = pyqtSignal()

    def __init__(self):
        super(PDWForm, self).__init__()
        self.setupUi(self)

        # setup figure
        self.fig = Figure()

        # widgets
        self.infBoxWidget = PDWInformationBoxForm()
        self.toolsWidget = PDWToolsForm()
        self.dataInfoWidget = DataInformationForm()
        self.rightFrameLayout.addWidget(self.toolsWidget)
        self.rightFrameLayout.addWidget(self.infBoxWidget)
        self.dataInformationLayout.addWidget(self.dataInfoWidget)
        self.subPlotsWidget = SubPlotWidget(self.fig)
        self.leftVerticalLayout.addWidget(self.subPlotsWidget)

        self.navtool = self.subPlotsWidget.get_nav_tool()
        self.rightFrameLayout.addWidget(self.navtool)

        # variables
        self.canvas = self.subPlotsWidget.get_canvas()
        self.channels = []
        self.selection_area = (-1, -1)
        self.selection_area_updated = False
        self.selection_area_indx = (-1, -1)

        # initialization
        self.setup_connections()

    def setup_connections(self):
        self.toolsWidget.filePathChanged.connect(self.filePathChanged)
        self.toolsWidget.filePathChanged.connect(self.dataInfoWidget.set_file_name)
        self.toolsWidget.dataRequested.connect(self.dataRequested)
        self.totalDataSizeChanged.connect(self.dataInfoWidget.set_total_data_size)
        self.toolsWidget.selectBtnPressed.connect(self.subPlotsWidget.enable_select_action)
        self.subPlotsWidget.selectionRangeHasBeenSet.connect(self.set_selection_area)

    @pyqtSlot(dict)
    def setup_channels(self, header):
        axs = self.fig.subplots(len(header.items()), 1, sharex='all')
        ch_counter = 0
        for _id, _name in header.items():
            ch = Channel(_id, _name, axs[ch_counter], self.canvas)
            ch.setup_style()
            self.channels.append(ch)
            ch_counter += 1
        self.canvas.draw()

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        for channel in self.channels:
            if channel.id == data_packet.id:
                if self.selection_area[0] == -1 or self.selection_area[1] == -1:
                    channel.feed(data_packet.key, data_packet.data, "#ADD8E6")
                else:
                    if self.selection_area_updated:
                        first_index = find_nearest_value_indx(data_packet.key, self.selection_area[0])
                        last_index = find_nearest_value_indx(data_packet.key, self.selection_area[1])
                        self.selection_area_indx = (first_index, last_index)
                        self.selection_area_updated = False
                    channel.clear()
                    part_1_key = data_packet.key[:self.selection_area_indx[0]]
                    part_1_val = data_packet.data[:self.selection_area_indx[0]]
                    part_2_key = data_packet.key[self.selection_area_indx[0]:self.selection_area_indx[1]]
                    part_2_val = data_packet.data[self.selection_area_indx[0]:self.selection_area_indx[1]]
                    part_3_key = data_packet.key[self.selection_area_indx[1]:]
                    part_3_val = data_packet.data[self.selection_area_indx[1]:]
                    channel.feed(part_1_key, part_1_val, "#ADD8E6")
                    channel.feed(part_2_key, part_2_val, "#FF7F7F")
                    channel.feed(part_3_key, part_3_val, "#ADD8E6")

        self.canvas.draw()

    @pyqtSlot('double', 'double')
    def set_selection_area(self, xmin, xmax):
        self.selection_area = (xmin, xmax)
        self.selection_area_updated = True
        self.dataRequested.emit()
