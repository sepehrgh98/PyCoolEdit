import numpy as np
from PyQt5.QtCore import pyqtSlot
from visualization.pdw.Channel import channel

class MultiChannels:
    def __init__(self):
        self.ids = []
        self.channels = []
        self._axis = None
        self._canvas = None
        self._hist_axis = None
        self._hist_canvas = None
        self.selected_area = []

        # style
        self.tick_size = 7
        self.title_size = 8
        self.font_name = "Times New Roman"
        self.font_weight = "bold"
        self.font_color = '#FFFCAD'
        self.plot_detail_color = 'w'
        self.axis_bg_color = '#222b2e'
        self.data_color = '#b0e0e6'
        self.fig_color = '#151a1e'

    def __repr__(self) -> str:
        rep = '{'
        for id in self.ids:
            rep += str(id)
            rep += ", "
        rep += '}'
        return rep

    def add_channel(self, ch):
        ch._axis.axis('off')
        self.channels.append(ch)
        self.ids.append(ch.id) 

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
        self._axis.set_ylabel("multi", fontsize=self.title_size, fontname=self.font_name,
                              fontweight=self.font_weight,
                              color=self.font_color)
        self._hist_axis.set_facecolor(self.axis_bg_color)
        self._hist_axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self._hist_axis.spines['bottom'].set_color(self.plot_detail_color)
        self._hist_axis.spines['top'].set_color(self.plot_detail_color)
        self._hist_axis.spines['right'].set_color(self.plot_detail_color)
        self._hist_axis.spines['left'].set_color(self.plot_detail_color)
        self._hist_axis.set_xticks([])

    def is_multiple(self):
        return True

    @pyqtSlot(np.ndarray, list)
    def feed(self, x, data_list, color, mood="initilize"):        
        # self.feed_time(x)
        # self.val = data_list
        line, = self._axis.plot(x, data_list, 'o', markersize=0.5, color=color)
        if mood == "initilize":
            self._hist_axis.hist(data_list, bins=100, orientation='horizontal', color=color)
        # self.update_hist(data_list)
        if mood == "selection":
            self.selected_area.append(line)

    def rescale(self):
        self._axis.set_xlim(list(self.time_range))
        if self._min == self._max:
            self._axis.set_ylim(self._min - 1, self._max + 1)
        else:
            y_range = self._max - self._min
            y_tol = y_range/4
            self._axis.set_ylim(self._min-y_tol, self._max+y_tol)

        self._canvas.draw()