import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'radar', 'radarchannelui.ui'))[0]


class RadarChannelForm(QWidget, Form):
    def __init__(self, _id, _name):
        super(RadarChannelForm, self).__init__()
        self.setupUi(self)

        # initialize
        self._id = _id
        self._name = _name

        # variables
        self.bin = None
        self.range = ()

        # ui initialize
        self.channelLabel.setText(self._name + " :")
        self.tableWidget.setColumnCount(6)
        table_header = ["#", self._name, "Count", "Accuracy", "Min", "Max"]
        self.tableWidget.setHorizontalHeaderLabels(table_header)
        self.tableWidget.verticalHeader().setVisible(False)

        # setup figure
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        axs = self.fig.subplots(2, 1)
        self.main_plot = axs[0]
        self.hist_plot = axs[1]

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

        # setup fig
        self.fig.patch.set_color('#151a1e')
        self.fig.subplots_adjust(left=0.061, bottom=0.007, right=0.9980, top=0.993, wspace=0, hspace=0.2)
        self.fig.tight_layout()
        self.fig.suptitle(self._name, fontsize=self.title_size
                          , fontname=self.font_name
                          , fontweight=self.font_weight
                          , color=self.font_color)

        self.setup_main_plot()
        self.setup_hist_plot()
        self.plotLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.setup_connections()
        self.initialize()

    def setup_connections(self):
        self.binSpinBox.valueChanged.connect(self.set_bin)

    def setup_main_plot(self):
        self.main_plot.set_facecolor(self.axis_bg_color)
        self.main_plot.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.main_plot.spines['bottom'].set_color(self.plot_detail_color)
        self.main_plot.spines['top'].set_color(self.plot_detail_color)
        self.main_plot.spines['right'].set_color(self.plot_detail_color)
        self.main_plot.spines['left'].set_color(self.plot_detail_color)
        self.main_plot.grid(axis='both', ls='--', alpha=0.4)

    def setup_hist_plot(self):
        self.hist_plot.set_facecolor(self.axis_bg_color)
        self.hist_plot.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.hist_plot.spines['bottom'].set_color(self.plot_detail_color)
        self.hist_plot.spines['top'].set_color(self.plot_detail_color)
        self.hist_plot.spines['right'].set_color(self.plot_detail_color)
        self.hist_plot.spines['left'].set_color(self.plot_detail_color)
        self.hist_plot.grid(axis='both', ls='--', alpha=0.4)

    def feed(self, time, val):
        self.main_plot.scatter(time, val, linewidths=1.5)
        self.hist_plot.hist(val, bins=self.bin)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, _id):
        self._id = _id

    @pyqtSlot(int)
    def set_bin(self, value):
        if self.bin != value:
            self.bin = value

    def initialize(self):
        self.set_bin(40)
