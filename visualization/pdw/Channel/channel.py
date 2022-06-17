from PyQt5 import uic
from matplotlib.axes._axes import Axes
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import os
import matplotlib
import numpy as np

matplotlib.use("Qt5Agg")
Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'channelui.ui'))[0]


class Channel:
    dataRequested = pyqtSignal(int, tuple, tuple)  # channel_id , x_range , y_range

    def __init__(self, _id, _name, axis, _canvas):

        # initialize
        self._id = _id
        self._name = _name
        self._axis = axis
        self.canvas = _canvas

        # variables
        self.properties = dict()
        self.plot_method = None
        self.time = []
        self._max = None
        self._min = None
        self.time_range = ()
        self.selected_area = None

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

    @pyqtSlot(np.ndarray, list)
    def feed(self, x, data_list, color, mood="initilize"):
        if self.selected_area:
            self.selected_area.set_data([], [])
        self._max = max(data_list)
        self._min = min(data_list)
        self.feed_time(x)
        line, = self._axis.plot(x, data_list, 'o', markersize=0.5, color=color)
        if mood == "selection":
            self.selected_area = line

    def feed_time(self, x):
        self.time = x
        self.set_time_range((min(x), max(x)))

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, a):
        if not isinstance(a, int):
            raise ValueError("id must be integer!")
        self._id = a

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, a):
        if not isinstance(a, str):
            raise ValueError("name must be integer!")
        self._name = a

    def setup_style(self):
        self._axis.set_facecolor(self.axis_bg_color)
        self._axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self._axis.spines['bottom'].set_color(self.plot_detail_color)
        self._axis.spines['top'].set_color(self.plot_detail_color)
        self._axis.spines['right'].set_color(self.plot_detail_color)
        self._axis.spines['left'].set_color(self.plot_detail_color)
        self._axis.grid(axis='both', ls='--', alpha=0.4)
        # self._axis.xaxis.set_visible(False)
        self._axis.set_ylabel(self._name, fontsize=self.title_size, fontname=self.font_name,
                              fontweight=self.font_weight,
                              color=self.font_color)

    @pyqtSlot(Axes)
    def add_axis(self, ax):
        self._axis = ax

    @property
    def axis(self):
        return self._axis

    @pyqtSlot(tuple)
    def set_time_range(self, freq_range):
        self.time_range = freq_range

    def rescale(self):
        self.axis.set_xlim(list(self.time_range))
        if self._min == self._max:
            self.axis.set_ylim(self._min - 1, self._max + 1)
        else:
            self.axis.set_ylim(self._min, self._max)

        self.canvas.draw()

    def clear(self):
        self.axis.cla()
