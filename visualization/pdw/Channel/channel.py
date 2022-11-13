from pkgutil import iter_importers
from PyQt5 import uic
from matplotlib.axes._axes import Axes
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QElapsedTimer
import os
import matplotlib
import numpy as np
from visualization.visualizationparams import ChannelUnit, FeedMood
import matplotlib.pyplot as plt
import time

class Channel:
    dataRequested = pyqtSignal(int, tuple, tuple)  # channel_id , x_range , y_range

    def __init__(self, _id, _name, _unit, axis, _canvas, _hist_axis):
        # initialize
        self._id = _id
        self._name = _name
        self._axis = axis
        self._canvas = _canvas
        self._hist_axis = _hist_axis
        self.unit = _unit

 
        # variables
        self.properties = dict()
        self.time = []
        self.val = []
        self._max = None
        self._min = None
        self.time_range = ()
        self.whole_area = None
        self.selected_area = {}   # arange : line obj
        self.initial_plot = True
        self.time_show_range = ()
        self.color = None
        self.counts = None
        self.bins = None
        self.bars = None

        # style
        self.tick_size = 10
        self.title_size = 10
        self.font_name = "Times New Roman"
        self.font_weight = "bold"
        self.font_color = '#FFFCAD'
        self.plot_detail_color = 'w'
        self.axis_bg_color = '#222b2e'
        self.data_color = '#b0e0e6'
        self.fig_color = '#151a1e'


    def __repr__(self) -> str:
        return str(self.id)

    @pyqtSlot(np.ndarray, list, FeedMood)
    # def feed(self, x, data_list, color, mood="initilize"):
    def feed(self, x, data_list, color, mood=FeedMood.main_data):
        if len(x)<2:
            return
        if mood == FeedMood.main_data or mood == FeedMood.zoom:
            timer = QElapsedTimer()
            if len(data_list):
                self._max = np.amax(data_list)
                self._min = np.amin(data_list)
            self.val = data_list
            self.feed_time(x)
            if self.whole_area:
                self.whole_area.set_data([], [])

            if self.bars:
                _ = [b.remove() for b in self.bars]
            self.cancel_selection_all()
            self.color = color
            area, = self._axis.plot(x, data_list, 'o', markersize=1.6, color=color)
            timer.start()
            self.counts, self.bins, self.bars = self._hist_axis.hist(data_list, bins=50, orientation='horizontal', color=color)
            # print(timer.elapsed())
            self.whole_area = area
            self.rescale()
        elif mood == FeedMood.select:
            line, = self._axis.plot(x, data_list, 'o', markersize=1.6, color=color)
            self.selected_area[x[0], x[-1]] = line

       

    def feed_time(self, x):
        if len(x):
            self.time = x
            self.set_time_range((np.amin(x), np.amax(x)))


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
        self.title = a

    @property
    def canvas(self):
        return self._canvas

    @canvas.setter
    def canvas(self, a):
        self._canvas = a

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, a):
        self._axis = a


    @property
    def hist_axis(self):
        return self._hist_axis

    @hist_axis.setter
    def hist_axis(self, a):
        self._hist_axis = a

    def setup_style(self):
        self._axis.set_facecolor(self.axis_bg_color)
        self._axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self._axis.spines['bottom'].set_color(self.plot_detail_color)
        self._axis.spines['top'].set_color(self.plot_detail_color)
        self._axis.spines['right'].set_color(self.plot_detail_color)
        self._axis.spines['left'].set_color(self.plot_detail_color)
        self._axis.grid(axis='both', ls='--', alpha=0.4)
        self._axis.set_ylabel(self.name +'('+ self.unit + ')', fontsize=self.title_size, fontname=self.font_name,
                              fontweight=self.font_weight,
                              color=self.font_color)
        self._hist_axis.set_facecolor(self.axis_bg_color)
        # self._hist_axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self._hist_axis.tick_params(left = False, labelleft = False , labelbottom = False, bottom = False)
        self._hist_axis.spines['bottom'].set_color(self.plot_detail_color)
        self._hist_axis.spines['top'].set_color(self.plot_detail_color)
        self._hist_axis.spines['right'].set_color(self.plot_detail_color)
        self._hist_axis.spines['left'].set_color(self.plot_detail_color)
        # self._hist_axis.set_xticks([])

    @pyqtSlot(Axes)
    def add_axis(self, ax):
        self._axis = ax

    @pyqtSlot(tuple)
    def set_time_range(self, freq_range):
        self.time_range = freq_range

    def rescale(self):
        self._axis.set_xlim(list(self.time_range))
        if self._min == self._max:
            self._axis.set_ylim(self._min - 1, self._max + 1)
        else:
            y_range = self._max - self._min
            y_tol = y_range/4
            self._axis.set_ylim(self._min-y_tol, self._max+y_tol)

    def clear(self):
        self.axis.cla()

    def cancel_selection_all(self):
        if self.selected_area:
            for range, line_obj in self.selected_area.items():
                line_obj.set_data([], [])
            self.selected_area = {}

    
    def cancel_selection(self, req_range):
        mid_point = ((req_range[1] - req_range[0])/2)+req_range[0]
        current_range = ()
        for range, line_obj in self.selected_area.items():
            if( mid_point >= range[0] and mid_point <= range[1]) or (range[0] >= req_range[0] and range[1] <= req_range[1]):
                current_range = range
                line_obj.set_data([], [])
                break
        if current_range != ():
            self.selected_area.pop(current_range)

    def remove_selected(self):
        x = self.whole_area.get_xdata()
        y = self.whole_area.get_ydata()
        for range, line_obj in self.selected_area.items():
            s_x = line_obj.get_xdata()
            s_y = line_obj.get_ydata()
            for item in zip(s_x,s_y):
                indices = np.where(x == item[0])[0]
                x = np.delete(x, indices)
                y = np.delete(y, indices)
        self.feed(x,y, self.color, mood=FeedMood.main_data)
        # self.canvas.draw()

    def on_xlims_change(self, event_ax):
        if event_ax.get_xlim() != self.time_show_range:
            x_start, x_end = event_ax.get_xlim()
            final_x_start = x_start
            final_x_end = x_end
            if x_start < self.time_range[0]:
                final_x_start = self.time_range[0]
            if x_end > self.time_range[1]:
                final_x_end = self.time_range[1]
            self.time_show_range = (final_x_start, final_x_end)
            self._axis.set_xlim([final_x_start, final_x_end])
            self._canvas.draw()


    def update_hist(self, data_list):
        self._hist_axis.clear()
        self._hist_axis.hist(data_list, bins=100, orientation='horizontal', color='#ADD8E6')


    def set_x_tick(self, title):
        self._axis.set_xlabel(title, fontsize=self.title_size, fontname=self.font_name,
                        fontweight=self.font_weight,
                        color=self.font_color)

    def is_multiple(self):
        return False

    def unit_detection(self, received_name):
        if "(" in received_name or ")" in received_name:
            mylist = received_name.split("(")
            name = mylist[0]
            unit = mylist[1].split(")")[0]
        else:
            name = received_name
            unit = ChannelUnit[name.translate(name.maketrans('', '', digits))] if ChannelUnit[name.translate(name.maketrans('', '', digits))] else ''
        return name, unit

    def replot(self, color):
        self.feed(self.time, self.val, color, mood="initilize")
            
