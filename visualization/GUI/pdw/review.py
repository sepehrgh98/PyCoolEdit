import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSlot
from visualization.visualizationparams import DataPacket
import numpy as np

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'reviewui.ui'))[0]


class PDWReviewForm(QWidget, Form):

    def __init__(self):
        super(PDWReviewForm, self).__init__()
        self.setupUi(self)

        # variable
        self.showed_channel = 1
        self.marked_areas = {} # arange : stem obj(markerline, stemline, baseline)

        # setup plot
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.verticalLayout.addWidget(self.canvas)


        # style
        self.tick_size = 7
        self.title_size = 12
        self.font_name = "Times New Roman"
        self.font_weight = "bold"
        self.font_color = '#FFFCAD'
        self.plot_detail_color = 'w'
        self.axis_bg_color = '#222b2e'
        self.data_color = '#b0e0e6'
        self.fig_color = '#232430'
        self.axis_color = '#a73631'
        self.axis_circle_color = '#b5bc35'
        self.axis_marked_color = '#d70a01'
        self.axis_marked_circle_color = '#e3f001'


        # style fig
        self.fig.patch.set_color('#151a1e')
        self.fig.subplots_adjust(left=0.06, right=0.903)
        self.fig.tight_layout()

        # plot
        self.main_plot = self.fig.subplots()
        self.main_plot.tick_params(left = False, labelleft = False , labelbottom = False, bottom = False)

        self.setup_plot()
        self.canvas.draw()

    def setup_plot(self):
        self.main_plot.set_facecolor(self.axis_bg_color)
        # self.main_plot.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.main_plot.spines['bottom'].set_color(self.plot_detail_color)
        self.main_plot.spines['top'].set_color(self.plot_detail_color)
        self.main_plot.spines['right'].set_color(self.plot_detail_color)
        self.main_plot.spines['left'].set_color(self.plot_detail_color)
        # For X-axis
        self.main_plot.axes.xaxis.set_ticklabels([])
        # For Y-axis
        self.main_plot.axes.yaxis.set_ticklabels([])
        # self.main_plot.grid(axis='both', ls='--', alpha=0.4)


    @pyqtSlot(DataPacket)
    def feed(self, data_packet, mood="initilize"):
        if data_packet.id == self.showed_channel:
            if mood == "initilize":
                self.clear()
                # self.marked_areas = {}
                # self.main_plot.clear()
            # min_val = min(data_packet.data)
            min_val = np.amin(data_packet.data)
            self.main_plot.stem(data_packet.key
                                , data_packet.data
                                , use_line_collection = True
                                , linefmt=self.axis_color
                                , bottom = min_val
                                , markerfmt=self.axis_circle_color
                                # , markerfmt=" "
                                ,basefmt=" "
                                )
            self.rescale(data_packet)
            self.canvas.draw()
            self.canvas.flush_events()

    def rescale(self, pack):
        time_range = (pack.key[0], pack.key[-1])
        self.main_plot.set_xlim(list(time_range))
    
    def clear(self):
        self.marked_areas = {}
        self.main_plot.clear()
        self.canvas.draw()

    @pyqtSlot(int)   
    def showed_channel(self, ch_id):
        self.showed_channel = ch_id

    @pyqtSlot(DataPacket)
    def feed_marked(self, data_packet):
        if len(data_packet.key) < 2 :
            return
        if data_packet.id == self.showed_channel:
            min_val = min(data_packet.data)
            markerline, stemline, baseline =self.main_plot.stem(data_packet.key
                                , data_packet.data
                                , use_line_collection = True
                                , linefmt=self.axis_marked_color
                                , bottom = min_val
                                , markerfmt=self.axis_marked_circle_color
                                , basefmt=" ")
            self.marked_areas[(data_packet.key[0],data_packet.key[-1])] = (markerline, stemline, baseline)
            self.canvas.draw()
            self.canvas.flush_events()

    @pyqtSlot(tuple) # ranges
    def unmark(self, req_range):
        mid_point = ((req_range[1] - req_range[0])/2)+req_range[0]
        current_range = ()
        for range, stem_obj in self.marked_areas.items():
            if mid_point >= range[0] and mid_point <= range[1]:
                current_range = range
                stem_obj[0].remove() # markerline
                stem_obj[1].remove() # stemline
                stem_obj[2].remove() # baseline
                break
        if current_range != ():
            self.marked_areas.pop(current_range)

        self.canvas.draw()
        self.canvas.flush_events()

 

    @pyqtSlot() # list of ranges
    def unmark_all(self):
        for range, stem_obj in self.marked_areas.items():
            stem_obj[0].remove() # markerline
            stem_obj[1].remove() # stemline
            stem_obj[2].remove() # baseline
        self.marked_areas = {}

        self.canvas.draw()
        self.canvas.flush_events()

