import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from visualization.visualizationparams import DataPacket
import numpy as np
import random
from visualization.visualizationparams import Channel_id_to_name

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'normalizewindowui.ui'))[0]


class NormalizeWindow(QWidget, Form):
    def __init__(self):
        super(NormalizeWindow, self).__init__()
        self.setupUi(self)

        # lines
        self.lines = []
        self.time = []

        # setup plot
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.main_plot = self.fig.subplots(1, 1)

        # style
        self.tick_size = 7
        self.title_size = 12
        self.font_name = "Times New Roman"
        self.font_weight = "bold"
        self.font_color = '#FFFCAD'
        self.plot_detail_color = 'w'
        self.axis_bg_color = '#222b2e'
        self.data_color = '#b0e0e6'
        self.fig_color = '#151a1e'


        # style fig
        self.fig.patch.set_color(self.fig_color)
        self.fig.subplots_adjust(left=0.061, bottom=0.06, right=0.9980, top=0.993, wspace=0.05, hspace=0.1)
        self.fig.tight_layout()

        self.plotLayout.addWidget(self.canvas)

        self.setup_main_plot()


    def setup_main_plot(self):
        self.main_plot.set_facecolor(self.axis_bg_color)
        self.main_plot.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.main_plot.spines['bottom'].set_color(self.plot_detail_color)
        self.main_plot.spines['top'].set_color(self.plot_detail_color)
        self.main_plot.spines['right'].set_color(self.plot_detail_color)
        self.main_plot.spines['left'].set_color(self.plot_detail_color)
        self.main_plot.grid(axis='both', ls='--', alpha=0.4)

    @pyqtSlot(DataPacket)
    def feed(self, data_packet):
        if not len(self.time):
            self.time = data_packet.key
        normalized_data = self.NormalizeData(data_packet.data)
        # line, = self.main_plot.plot(data_packet.key, normalized_data, 'o', markersize=0.5, color=color)
        self.lines.append((Channel_id_to_name[data_packet.id],normalized_data))
        # self.legend = self.main_plot.legend()


    def NormalizeData(self, data):
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    def plot_it(self):
        channels = []
        for line in self.lines:
            color = (["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])])[-1]
            self.main_plot.plot(self.time, line[1], 'o', markersize=0.5, color=color)
            channels.append(line[0])
        self.main_plot.legend(channels)

