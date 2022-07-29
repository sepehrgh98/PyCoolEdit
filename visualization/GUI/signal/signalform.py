import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
import matplotlib.gridspec
from visualization.GUI.signal.signalinformation import SignalInformationForm
from visualization.GUI.defaultview.defaultview import DefaultView
from matplotlib.backend_bases import MouseButton


Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'signal', 'signalui.ui'))[0]


class SignalForm(QMainWindow, Form):
    request_data = pyqtSignal(dict, tuple)

    def __init__(self):
        super(SignalForm, self).__init__()
        self.setupUi(self)

        # widgets
        self.default_view = DefaultView(icon_path = 
                    os.path.join(os.getcwd(), 'visualization', 'Resources', 'icons', 'signal.png')
                    , text='Signal'
                    , filter="Text files (*.DAT);")

        self.plotLayout.addWidget(self.default_view)    
        # variables
        self.file_path = None
        self.signal_information = SignalInformationForm()
        self.channels = []
        self.req_range = ()
        self.zoom_base_scale = 2
        self.x_limit_range = None
        self.y_limit_range = None
        self.x_control = None
        self.drag_mode = False
        self.draged_point = None
        self.span_list = []

        # setup plot
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        # self.plotLayout.addWidget(self.canvas)
        self.channels = []
        self.y_controls = []
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
        self.fig.patch.set_color(self.fig_color)
        self.fig.subplots_adjust(left=0.061, bottom=0.06, right=0.9980, top=0.993, wspace=0.05, hspace=0.1)
        self.fig.tight_layout()

        # table
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setup_connections()

    def setup_connections(self):
        self.openFileBtn.clicked.connect(self.get_file_path)
        self.signal_information.file_info_is_ready.connect(self.prepare_data_request)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('scroll_event',self.zoom_on_wheel)
        self.default_view.filePathChanged.connect(self.handle_file_path_changed)


    def get_file_path(self):
        new_path = QFileDialog.getOpenFileName(self, "Open File", filter="Text files (*.DAT);")[0]
        if self.file_path != new_path:
            self.file_path = new_path
        self.handle_file_path_changed(new_path)

    def setup_channels(self, data_info):
        height_ratios_list = [1.4 for _ in range(data_info["channels"])]
        height_ratios_list.append(0.09)
        gs = matplotlib.gridspec.GridSpec(data_info["channels"] + 1 ,2, width_ratios=[0.02,1.4], height_ratios=height_ratios_list)

        for i in range(data_info["channels"]):
            y_control = self.fig.add_subplot(gs[i,0]) 
            ax = self.fig.add_subplot(gs[i,1], sharey=y_control) 
            y_control.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
            y_control.axes.xaxis.set_ticks([])
            y_control.set_facecolor(self.axis_bg_color)
            # self.cursor_1 = CursorLine(ax, "v")
            self.style_channels(ax)
            self.channels.append(ax)
            self.y_controls.append(y_control)
            self.setup_span_selector(ax)
        self.x_control = self.fig.add_subplot(gs[data_info["channels"],1])
        self.x_control.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.x_control.axes.yaxis.set_ticks([])
        self.x_control.set_facecolor(self.axis_bg_color)
        self.x_control.get_shared_x_axes().join(self.x_control, *self.channels)

        self.canvas.draw()
        self.canvas.flush_events()

    def setup_span_selector(self, ax):
        span = SpanSelector(
            ax,
            self.on_span_selected,
            "horizontal",
            useblit=True,
            button = [1],
            props=dict(alpha=0.5, facecolor="tab:red"),
            interactive=True,
            drag_from_anywhere=True,
            handle_props=dict(color="yellow")
        )
        self.span_list.append(span)

    def style_channels(self, axis):
        axis.set_facecolor(self.axis_bg_color)
        axis.spines['bottom'].set_color(self.plot_detail_color)
        axis.spines['top'].set_color(self.plot_detail_color)
        axis.spines['right'].set_color(self.plot_detail_color)
        axis.spines['left'].set_color(self.plot_detail_color)
        axis.grid(axis='both', ls='--', alpha=0.4)
        axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.fig_color)
           
    def on_span_selected(self, xmin, xmax):
        print(xmin, xmax)

    @pyqtSlot(dict)
    def prepare_data_request(self, data_info):
        self.setup_channels(data_info)
        new_info = data_info
        new_info["file"] = self.file_path
        self.request_data.emit(new_info, self.req_range)

    @pyqtSlot(list)
    def feed(self, data_list):
        for item in zip(self.channels, data_list):
            item[0].plot(item[1].key, item[1].data, linestyle='-', marker='o', markersize=5, color="#00A36C")
            min_x = min(item[1].key)
            max_x = max(item[1].key)
            min_y = min(item[1].data)
            max_y = max(item[1].data)
            y_range = max_y - min_y
            x_tol = 0
            y_tol = y_range/2
            self.x_limit_range = [min_x - x_tol, max_x + x_tol]
            self.y_limit_range = [min_y - y_tol, max_y + y_tol]
            self.rescale()

        self.canvas.draw()
        self.canvas.flush_events()

    def on_mouse_press(self, event):
        if event.inaxes in self.channels:
            if event.dblclick:
                if event.button == 1:
                    self.rescale()
            # else:
            #     if len(self.span_list):
            #         if event.button == 3:
            #             for span in self.span_list:
            #                 span.set_active(False)
            #                 span.set_visible(False)
            #         elif event.button == 1:
            #             for span in self.span_list:
            #                 span.set_active(True)
            #                 span.set_visible(True)
            #         self.canvas.flush_events()
            #         self.canvas.draw()

        if event.inaxes == self.x_control:
            self.drag_mode = True
            self.draged_point = event.xdata

    def on_mouse_move(self, event):
        if event.inaxes == self.x_control and self.drag_mode:
            ax = event.inaxes
            diff = event.xdata - self.draged_point
            current_x_range = ax.get_xlim()
            new_x_range = (current_x_range[0] - diff, current_x_range[1] - diff)
            new_x_start, new_x_end = new_x_range
            if(new_x_start < self.x_limit_range[0]):
                new_x_start = self.x_limit_range[0]
            if(new_x_end > self.x_limit_range[1]):
                new_x_end = self.x_limit_range[1]
            ax.set_xlim([new_x_start, new_x_end])
            self.canvas.draw()


    def on_mouse_release(self, event):
        self.drag_mode = False
            

    def rescale(self):
        for axis in self.channels:
            axis.set_xlim(self.x_limit_range)
            axis.set_ylim(self.y_limit_range)
        self.canvas.draw()

    def zoom_on_wheel(self, event):
        if event.inaxes in self.channels:
            for ax in self.channels:
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
        if event.inaxes in self.y_controls:
            ax = event.inaxes
            # get the current x and y limits
            cur_ylim = ax.get_ylim()
            cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
            ydata = event.ydata # get event y location
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
            new_y_start = ydata - cur_yrange*scale_factor
            new_y_end = ydata + cur_yrange*scale_factor
            if(new_y_start < self.y_limit_range[0]):
                new_y_start = self.y_limit_range[0]
            if(new_y_end > self.y_limit_range[1]):
                new_y_end = self.y_limit_range[1]

            ax.set_ylim([new_y_start,
                        new_y_end])
        self.canvas.draw() # force re-draw

    def handle_file_path_changed(self, file_path):
        if self.file_path != file_path:
            self.file_path = file_path
        if self.default_view:
            self.plotLayout.removeWidget(self.default_view)
            self.default_view.deleteLater()
            self.default_view = None
            self.plotLayout.addWidget(self.canvas)
        self.signal_information.show()


