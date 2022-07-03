import os
from tkinter import N
import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from visualization.GUI.cursorline import CursorLine

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'radar', 'radarchannelui.ui'))[0]


class RadarChannelForm(QWidget, Form):
    def __init__(self, _id, _name):
        super(RadarChannelForm, self).__init__()
        self.setupUi(self)

        # initialize
        self._id = _id
        self._name = _name

        # variables
        # self.time = np.array([])
        # self.channel_val =  np.array([])
        self.bin = None
        self.time_range = [-1,-1]
        self.val_range = [-1,-1]
        self.main_layer = None
        # self.hist_layer = None
        self.hist_n = None
        self.his_X = None
        self.hist_V = None
        self.row_counter = 0

        # ui initialize
        self.channelLabel.setText(self._name + " :")
            # local table
        self.tableWidget.setColumnCount(4)
        table_header = [self._name, "Count", "Min", "Max"]
        self.tableWidget.setHorizontalHeaderLabels(table_header)
        # self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            #shared table
        

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

        # style fig
        self.fig.patch.set_color('#151a1e')
        self.fig.subplots_adjust(left=0.061, bottom=0.007, right=0.9980, top=0.993, wspace=0, hspace=0.2)
        self.fig.tight_layout()
        self.fig.suptitle(self._name, fontsize=self.title_size
                          , fontname=self.font_name
                          , fontweight=self.font_weight
                          , color=self.font_color)

        # show line
        self.hist_line_cursor = CursorLine(self.hist_plot, "h")


        # plot control
        self.navbar = NavigationToolbar(self.canvas, self.plotWidget)
        self.plotControlLayout.addWidget(self.navbar)

        self.setup_main_plot()
        self.setup_hist_plot()
        self.plotLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.canvas.flush_events()
        self.setup_connections()
        self.initialize()

    def setup_connections(self):
        self.binSpinBox.valueChanged.connect(self.set_bin)
        self.hist_plot.figure.canvas.mpl_connect('button_press_event', self.hist_line_cursor.on_mouse_pressed)
        self.hist_plot.figure.canvas.mpl_connect('button_release_event', self.hist_line_cursor.on_mouse_released)
        self.hist_line_cursor.data_selected.connect(self.set_thd)
        self.add_tb_btn.clicked.connect(self.feed_local_table)

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
        # set range
        self.time_range[0] = min(time)
        self.time_range[1] = max(time)
        self.val_range[0] = min(val)
        self.val_range[1] = max(val)
        self.channelDoubleSpinBox.setRange(self.val_range[0], self.val_range[1])
        self.channelDoubleSpinBox.setValue(self.val_range[0])

        # set line cursor
        self.hist_line_cursor.set_pos(self.val_range[0])

        # plot
        self.main_layer, = self.main_plot.plot(time, val, 'o', markersize=0.8, color=self.data_color)
        [self.hist_n,self.his_X, self.hist_V] = self.hist_plot.hist(val, bins=self.bin, color=self.data_color)

        # rescale
        self.main_plot.set_xlim(self.time_range[0], self.time_range[1])

        # update plot
        self.canvas.draw()
        self.canvas.flush_events()

    def feed_local_table(self):
        thd = self.hist_line_cursor.get_last_data()
        # self.thdLineEdit.setText(str(thd))
        if(thd):
            channel_val = self.channelDoubleSpinBox.value()
            self.tableWidget.setRowCount(self.row_counter+1)
            self.tableWidget.setItem(self.row_counter, 0, QTableWidgetItem(str(thd)))
            self.tableWidget.setItem(self.row_counter, 1, QTableWidgetItem(str(channel_val)))
            self.tableWidget.setItem(self.row_counter, 2, QTableWidgetItem(str(self.val_range[0])))
            self.tableWidget.setItem(self.row_counter, 3, QTableWidgetItem(str(self.val_range[1])))
            self.row_counter += 1
        

    def set_thd(self, val):
        self.thdLineEdit.setText(str(val))





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
