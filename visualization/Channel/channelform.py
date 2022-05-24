from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
import os
from visualization.visualizationplot import VisualizationPlot
import matplotlib
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from visualization.visualizationparams import PlotInteraction, PlotMethods

matplotlib.use("Qt5Agg")
Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'channelui.ui'))[0]


class ChannelForm(QWidget, Form):
    def __init__(self, _id, _name):
        super(ChannelForm, self).__init__()
        self.setupUi(self)

        # variables
        self.tick_size = 7
        self.title_size = 12
        self.font_name = "Times New Roman"
        self.font_weight = "bold"
        self.font_color = '#FFFCAD'
        self.plot_detail_color = 'w'
        self.axis_bg_color = '#222b2e'
        self.data_color = '#b0e0e6'
        self.fig_color = '#151a1e'

        # define plot
        self.fig = VisualizationPlot(facecolor=self.fig_color)
        self.axis = self.fig.add_subplot()
        self.canvas = FigureCanvas(self.fig)

        # plot method
        self.plot_method = self.axis.plot

        # initialize
        self._id = _id
        self._name = _name

        # attributes
        self._data = None
        self.x_range = ()
        self.y_range = ()

        # style
        self.setup_style()

        # add plot to ui
        self.mainPlotLayout.addWidget(self.canvas)


    @pyqtSlot(np.ndarray, np.ndarray, list, list)
    def feed(self, x, y, x_limit=None):
        self._data = y
        self.set_x_range(x.min, x.max)
        self.set_y_range(y.min(), y.max())
        if x_limit is None:
            x_limit = [-1, -1]

        self.plot_method(x, y,
                         c=[self.data_color if not x_limit[0] <= item <= x_limit[1] else "y" for item in x]
                         ,
                         alpha=1,
                         s=5)
        # self.plot_method(x, y, c=self.data_color)
        self.canvas.draw()

    @pyqtSlot(PlotMethods)
    def set_plot_method(self, method):
        if method == PlotMethods.Plot:
            self.plot_method = self.axis.plot
        elif method == PlotMethods.Scatter:
            self.plot_method = self.axis.scatter
        elif method == PlotMethods.Bar:
            self.plot_method = self.axis.bar
        else:
            raise ValueError("plot method is not defined!")

    @pyqtSlot(PlotInteraction)
    def set_interaction(self, inter):
        if isinstance(inter, PlotInteraction):
            if inter == PlotInteraction.ZoomOnWheel:
                self.fig.set_zoom_on_wheel_interaction(True)
            elif inter == PlotInteraction.Drag:
                self.fig.set_drag_interaction(True)
            elif inter == PlotInteraction.DoubleClick:
                self.fig.set_double_click_interaction(True)
            elif inter == PlotInteraction.ZoomOnBox:
                self.fig.set_zoom_on_box_interaction(True)
            elif inter == PlotInteraction.Select:
                self.fig.set_select_interaction(True)
        else:
            print("It's not an interaction!")

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
        # self.fig.set_tight_layout(True)
        # self.axis.set_title(self._name, loc='right', fontsize=self.title_size, fontname=self.font_name,
        #                     fontweight=self.font_weight, color=self.font_color)
        self.axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.axis.set_facecolor(self.axis_bg_color)
        self.axis.spines['bottom'].set_color(self.plot_detail_color)
        self.axis.spines['top'].set_color(self.plot_detail_color)
        self.axis.spines['right'].set_color(self.plot_detail_color)
        self.axis.spines['left'].set_color(self.plot_detail_color)
        self.axis.grid(axis='both', ls='--', alpha=0.4)
        self.axis.xaxis.set_visible(False)
        self.axis.set_ylabel(self._name, fontsize=self.title_size, fontname=self.font_name, fontweight=self.font_weight,
                             color=self.font_color)
        self.fig.subplots_adjust(wspace=0, hspace=0)
        self.fig.tight_layout(pad=0.4, w_pad=0, h_pad=0)

    def get_data(self):
        return self._data

    def set_y_range(self, dmin, dmax):
        self.y_range = (dmin, dmax)

    def set_x_range(self, dmin, dmax):
        self.x_range = (dmin, dmax)
