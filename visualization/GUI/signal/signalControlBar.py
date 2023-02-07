import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QFileDialog, QHeaderView, QGroupBox, QFormLayout, QLabel, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
import matplotlib.gridspec
from visualization.GUI.signal.signalinformation import SignalInformationForm
from visualization.GUI.defaultview.defaultview import DefaultView
import numpy as np

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'signal', 'signalControlBar.ui'))[0]


class SignalControlBar(QWidget, Form):
    def __init__(self):
        super(SignalControlBar, self).__init__()
        self.setupUi(self)
