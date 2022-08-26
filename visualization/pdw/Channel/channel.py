from PyQt5 import uic
from matplotlib.axes._axes import Axes
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread
import os
import matplotlib
import numpy as np
from visualization.visualizationparams import ChannelUnit

matplotlib.use("Qt5Agg")
Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'channelui.ui'))[0]

class Worker(QObject):
    new_data_is_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self, new_range, main_data):
        super().__init__()
        self.new_range = new_range
        self.main_data = main_data


    def run(self):
        """Long-running task."""
        new_val = np.array([])
        print(self.new_range)
        for item in self.main_data:
            if item <= self.new_range[1] and item >= self.new_range[0]:                
                arr = np.array((item,))
                new_val = np.concatenate([new_val, arr], axis=0)
        self.new_data_is_ready.emit(new_val)
        self.finished.emit()

class Channel:
    dataRequested = pyqtSignal(int, tuple, tuple)  # channel_id , x_range , y_range

    def __init__(self, _id, _name, _unit, axis, _canvas, _hist_axis, _hist_canvas):

        # initialize
        self._id = _id
        self._name = _name
        self._axis = axis
        self._canvas = _canvas
        self._hist_axis = _hist_axis
        self._hist_canvas = _hist_canvas
        self.unit = _unit

        # self._axis.callbacks.connect('xlim_changed', self.on_xlims_change)
        # self._axis.callbacks.connect('ylim_changed', self.on_ylims_change)
 
        # variables
        self.properties = dict()
        self.plot_method = None
        self.time = []
        self.val = []
        self._max = None
        self._min = None
        self.time_range = ()
        self.whole_area = None
        # self.selected_area = []
        self.selected_area = {}   # arange : line obj
        self.initial_plot = True
        self.time_show_range = ()

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

    @pyqtSlot(np.ndarray, list)
    def feed(self, x, data_list, color, mood="initilize"):
        if mood == "initilize" and self.whole_area:
            self.whole_area.set_data([], [])
            self._hist_axis.clear()
            self.cancel_selection()
            self.hist_canvas.draw()

        if len(data_list):
            self._max = max(data_list)
            self._min = min(data_list)
        
        self.val = data_list
        line, = self._axis.plot(x, data_list, 'o', markersize=0.5, color=color)
        if mood == "initilize":
            self.feed_time(x)
            self._hist_axis.hist(data_list, bins=100, orientation='horizontal', color=color)
        # self.update_hist(data_list)
        if mood == "selection" :
            self.selected_area[x[0], x[-1]] = line
        else:
            self.whole_area = line

    def feed_time(self, x):
        if len(x):
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
    def hist_canvas(self):
        return self._hist_canvas

    @hist_canvas.setter
    def hist_canvas(self, a):
        self._hist_canvas = a

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
        self._hist_axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self._hist_axis.spines['bottom'].set_color(self.plot_detail_color)
        self._hist_axis.spines['top'].set_color(self.plot_detail_color)
        self._hist_axis.spines['right'].set_color(self.plot_detail_color)
        self._hist_axis.spines['left'].set_color(self.plot_detail_color)
        self._hist_axis.set_xticks([])

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

        self._canvas.draw()

    def clear(self):
        self.axis.cla()

    def cancel_selection_all(self):
        for range, line_obj in self.selected_area.items():
            line_obj.set_data([], [])
        self.selected_area = {}
        self.canvas.draw()
        self.canvas.flush_events()
    
    def cancel_selection(self, req_range):
        mid_point = ((req_range[1] - req_range[0])/2)+req_range[0]
        current_range = ()
        for range, line_obj in self.selected_area.items():
            if mid_point >= range[0] and mid_point <= range[1]:
                current_range = range
                line_obj.set_data([], [])
                break
        if current_range != ():
            self.selected_area.pop(current_range)
        self.canvas.draw()
        self.canvas.flush_events()


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

    def on_ylims_change(self, event_ax):
        if len(self.val) and not self.initial_plot:
            new_range = event_ax.get_ylim()
            self.thread = QThread()
            self.worker = Worker(new_range, self.val)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.new_data_is_ready.connect(self.update_hist)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

        if self.initial_plot:
            self.initial_plot = False

    def update_hist(self, data_list):
        print("kk")
        self._hist_axis.clear()
        self._hist_axis.hist(data_list, bins=100, orientation='horizontal', color='#ADD8E6')
        self._hist_canvas.draw()
        self._hist_canvas.flush_events()

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