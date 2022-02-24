from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot
import os
from visualization.visualizationplot import VisualizationPlot
import matplotlib
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from visualization.visualizationparams import PlotInteraction

matplotlib.use("Qt5Agg")
Form = uic.loadUiType(os.path.join(os.getcwd(), 'GUI', 'channelui.ui'))[0]


class ChannelForm(QWidget, Form):
    def __init__(self, _id, _name):
        super(ChannelForm, self).__init__()
        self.setupUi(self)
        # initialize
        self._id = _id
        self._name = _name

        # define plot
        self.fig = VisualizationPlot()
        self.axis = self.fig.add_subplot(111)
        self.canv = FigureCanvas(self.fig)

        # add plot to ui
        self.mainPlotLayout.addWidget(self.canv)

    @pyqtSlot(np.ndarray, np.ndarray)
    def feed(self, x, y):
        self.axis.plot(x, y)

    @pyqtSlot(PlotInteraction)
    def set_interaction(self, inter):
        if isinstance(inter, PlotInteraction):
            if inter == PlotInteraction.Zoom:
                self.fig.set_zoom_on_wheel_interaction(True)
            elif inter == PlotInteraction.Drag:
                self.fig.set_drag_interaction(True)
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
