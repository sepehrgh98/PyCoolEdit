import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from visualization.GUI.signal.signalinformation import SignalInformationForm

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'signal', 'signalui.ui'))[0]


class SignalForm(QMainWindow, Form):
    data_info_is_ready = pyqtSignal(dict)

    def __init__(self):
        super(SignalForm, self).__init__()
        self.setupUi(self)

        # variables
        self.file_path = None
        self.signal_information = SignalInformationForm()
        self.channels = []

        # setup plot
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.plotLayout.addWidget(self.canvas)
        self.canvas.draw()

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

        self.setup_connections()

    def setup_connections(self):
        self.openFileBtn.clicked.connect(self.get_file_path)
        self.signal_information.file_info_is_ready.connect(self.setup_channels)
        self.signal_information.file_info_is_ready.connect(self.data_info_is_ready)

    def get_file_path(self):
        new_path = QFileDialog.getOpenFileName(self, "Open File", filter="Text files (*.DAT);")[0]
        if self.file_path != new_path:
            self.file_path = new_path
        self.signal_information.show()

    @pyqtSlot(dict)
    def setup_channels(self, data):
        axs = self.fig.subplots(data["number_of_channels"], 1)
        self.style_channels(axs)
        self.channels = axs
        self.canvas.draw()
        self.canvas.flush_events()

    def style_channels(self, axs):
        for axis in axs:
            axis.set_facecolor(self.axis_bg_color)
            axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
            axis.spines['bottom'].set_color(self.plot_detail_color)
            axis.spines['top'].set_color(self.plot_detail_color)
            axis.spines['right'].set_color(self.plot_detail_color)
            axis.spines['left'].set_color(self.plot_detail_color)
            axis.grid(axis='both', ls='--', alpha=0.4)
