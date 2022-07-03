import os
from select import select
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from visualization.pdw.Channel.channel import Channel
from visualization.GUI.pdw.pdwinformationbox import PDWInformationBoxForm 
from visualization.Radar.radarcontroller import RadarController
from visualization.GUI.pdw.pdwtools import PDWToolsForm
from visualization.GUI.pdw.datainformationform import DataInformationForm
from visualization.visualizationparams import DataPacket, FeedMood
from matplotlib.figure import Figure
from visualization.GUI.pdw.subplotwidget import SubPlotWidget
from visualization.GUI.radar.radarform import RadarForm
import numpy as np

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'pdwui.ui'))[0]

class PDWForm(QMainWindow, Form):
    filePathChanged = pyqtSignal(str)
    # totalDataSizeChanged = pyqtSignal(int)
    # selectDataSizeChanged = pyqtSignal(int)
    dataRequested = pyqtSignal(tuple, tuple)  # time range & value range
    # selectedDataIsReady = pyqtSignal(DataPacket)
    channelsSettedUp = pyqtSignal()

    def __init__(self):
        super(PDWForm, self).__init__()
        self.setupUi(self)


        # widgets
        self.infBoxWidget = PDWInformationBoxForm()
        self.toolsWidget = PDWToolsForm()
        self.dataInfoWidget = DataInformationForm()
        self.rightFrameLayout.addWidget(self.toolsWidget)
        self.rightFrameLayout.addWidget(self.infBoxWidget)
        self.dataInformationLayout.addWidget(self.dataInfoWidget)
        self.subPlotsWidget = SubPlotWidget()
        self.plotLayout.addWidget(self.subPlotsWidget)
        # self.radar_form = RadarForm()
        self.radar_controller = RadarController()

        # self.navtool = self.subPlotsWidget.get_nav_tool()
        # self.rightFrameLayout.addWidget(self.navtool)

        # variables
        self.fig = self.subPlotsWidget.get_figure()
        self.canvas = self.fig.canvas
        self.hist_fig = self.subPlotsWidget.get_hist_figure()
        self.hist_canvas = self.hist_fig.canvas
        self.channels = []
        self.selection_area_x = (-1, -1)
        self.selection_area_y = (-1, -1)
        self.data_header = None
        self.radars = []
        self.feedMood = FeedMood.main_data

        # initialization
        self.setup_connections()

    def setup_connections(self):
        self.toolsWidget.filePathChanged.connect(self.filePathChanged)
        self.toolsWidget.filePathChanged.connect(self.dataInfoWidget.set_file_name)
        # self.toolsWidget.dataRequested.connect(self.dataRequested)
        self.toolsWidget.selectBtnPressed.connect(self.subPlotsWidget.enable_select_action)
        self.subPlotsWidget.selectionRangeHasBeenSet.connect(self.set_selection_area)
        self.subPlotsWidget.unselectRequested.connect(self.do_unselect)
        self.subPlotsWidget.unselectRequested.connect(self.radar_controller.reset)
        self.toolsWidget.radarRequested.connect(self.radar_controller.initialize_new_radar)
        # self.selectedDataIsReady.connect(self.radar_controller.feed)
        self.channelsSettedUp.connect(self.subPlotsWidget.setup_rect)

    @pyqtSlot(dict)
    def setup_channels(self, header):
        self.data_header = header
        self.radar_controller.setup_channel(header)
        axs = self.fig.subplots(len(header.items()), 1, sharex='all')
        hist_axs = self.hist_fig.subplots(len(header.items()), 1)
        ch_counter = 0
        for _id, _name in header.items():
            ch = Channel(_id, _name, axs[ch_counter], self.canvas, hist_axs[ch_counter])
            ch.setup_style()
            self.channels.append(ch)
            ch_counter += 1
        self.channelsSettedUp.emit()
        self.canvas.draw()

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        total_size=0
        select_size=0
        for channel in self.channels:
            if channel.id == data_packet.id:
                if self.feedMood == FeedMood.main_data:
                    channel.feed(data_packet.key, data_packet.data, "#ADD8E6", mood="initilize")
                    total_size += len(data_packet.key)
                elif self.feedMood == FeedMood.select:
                    self.radar_controller.feed(data_packet)
                    channel.feed(data_packet.key, data_packet.data, "red", mood="selection")
                    select_size += len(data_packet.key)
                    
        if self.feedMood == FeedMood.main_data:
            self.dataInfoWidget.set_total_data_size(total_size)
        else:
            self.dataInfoWidget.set_select_data_size(select_size)
                

        self.canvas.draw()
        self.canvas.flush_events()
        self.hist_canvas.draw()
        self.hist_canvas.flush_events()
        

    @pyqtSlot(tuple, tuple)
    def set_selection_area(self, x_range, y_range):
        self.feedMood = FeedMood.select
        self.selection_area_x = x_range
        self.selection_area_y = y_range
        self.dataRequested.emit(self.selection_area_x, self.selection_area_y)

    @pyqtSlot()
    def do_unselect(self):
        self.feedMood = FeedMood.main_data
        self.selection_area_x = (-1, -1)
        self.selection_area_y = (-1, -1)
        for channel in self.channels:
            channel.cancel_selection()
        



