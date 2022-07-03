import os
from select import select

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

from visualization.GUI.signal.signalinformation import SignalInformationForm

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'signal', 'signalui.ui'))[0]


class SignalForm(QMainWindow, Form):
    request_data = pyqtSignal(dict, tuple)

    def __init__(self):
        super(SignalForm, self).__init__()
        self.setupUi(self)

        # variables
        self.file_path = None
        self.signal_information = SignalInformationForm()
        self.channels = []
        self.req_range = ()
        self.zoom_base_scale = 2
        self.x_limit_range = None
        self.y_limit_range = None

        # setup plot
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.plotLayout.addWidget(self.canvas)
        self.axs = None
        self.canvas.draw()

        # nav bar
        # self.navbar = NavigationToolbar(self.canvas, self)
        # self.plotControllerWidgetLayout.addWidget(self.navbar)

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

        # table
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # zoom on wheel
        self.canvas.mpl_connect('scroll_event',self.zoom_fun)

        self.setup_connections()

    def setup_connections(self):
        self.openFileBtn.clicked.connect(self.get_file_path)
        self.signal_information.file_info_is_ready.connect(self.prepare_data_request)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)

    def get_file_path(self):
        new_path = QFileDialog.getOpenFileName(self, "Open File", filter="Text files (*.DAT);")[0]
        if self.file_path != new_path:
            self.file_path = new_path
        self.signal_information.show()

    def setup_channels(self, data_info):
        self.axs = self.fig.subplots(data_info["channels"], 1, sharex='all')
        if not isinstance(self.axs, np.ndarray):
            print("kir", type(self.axs))
            self.axs = [self.axs]
        self.style_channels(self.axs)
        self.channels = self.axs
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

    @pyqtSlot(dict)
    def prepare_data_request(self, data_info):
        self.setup_channels(data_info)
        new_info = data_info
        new_info["file"] = self.file_path
        self.request_data.emit(new_info, self.req_range)

    @pyqtSlot(list)
    def feed(self, data_list):
        for item in zip(self.channels, data_list):
            item[0].plot(item[1].key, item[1].data, markersize=0.8)
            self.x_limit_range = [min(item[1].key)-2, max(item[1].key)+2]
            self.y_limit_range = [min(item[1].data)-2, max(item[1].data)+2]

        self.canvas.draw()
        self.canvas.flush_events()

    def on_mouse_press(self, event):
        if event.dblclick:
            for axis in self.axs:
                axis.set_xlim(self.x_limit_range)
                # axis.set_ylim(self.y_limit_range)


        self.canvas.draw()

    def zoom_fun(self, event):
        for ax in self.axs:
            # get the current x and y limits
            cur_xlim = ax.get_xlim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
            xdata = event.xdata # get event x location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1/self.zoom_base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = self.zoom_base_scale
            else: 
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)
            # set new limits
            new_x_start = xdata - cur_xrange*scale_factor
            new_x_end = xdata + cur_xrange*scale_factor
            if(new_x_start < self.x_limit_range[0]):
                new_x_start = self.x_limit_range[0]
            if(new_x_end > self.x_limit_range[1]):
                new_x_end = self.x_limit_range[1]

            ax.set_xlim([new_x_start,
                        new_x_end])
        self.canvas.draw() # force re-draw

