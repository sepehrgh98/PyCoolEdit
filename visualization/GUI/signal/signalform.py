import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView, QGroupBox, QFormLayout, QLabel, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
import matplotlib.gridspec
from visualization.GUI.signal.signalinformation import SignalInformationForm
from visualization.GUI.defaultview.defaultview import DefaultView
import numpy as np

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'signal', 'signalui.ui'))[0]


class SignalForm(QMainWindow, Form):
    fileInfoReceived = pyqtSignal(dict, tuple)
    request_data = pyqtSignal(tuple)

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
        self.zoom_base_scale = 0.75
        self.first_feed = True
        self.x_limit_range = None
        self.y_limit_range = None
        self.x_control = None
        self.drag_mode = False
        self.draged_point = None
        self.vertical_span_list = []
        self.hor_span = None
        self.hor_span_2 = None
        self.current_axis = None
        self.span_result_widgets = [] # list of (id, min_lineEdit, max_lineEdit, diff_lineEdit)
        self.zoom_timer = QTimer(self)
        self.zoom_timer.timeout.connect(self.on_zoom_timer_timeout)
        self.zoom_timer.setSingleShot(True)
        self.x_show_range = ()
        self.plot_containers = []

        # setup plot
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
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
        self.clear()
        new_path = QFileDialog.getOpenFileName(self, "Open File", filter="Text files (*.DAT);")[0]
        if self.file_path != new_path:
            self.file_path = new_path
        self.handle_file_path_changed(new_path)

    def clear(self):
        self.fig.clear()
        for i in reversed(range(self.verticalSpanResultLayout.count())): 
            self.verticalSpanResultLayout.itemAt(i).widget().setParent(None)
        self.span_result_widgets.clear()
        self.canvas.draw()


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
            self.setup_vertical_span_selector(y_control, ax)
            self.style_channels(ax)
            self.channels.append(ax)
            self.y_controls.append(y_control)
            self.setup_span_widgets(i)
        self.setup_horizontal_span_selector()
        self.x_control = self.fig.add_subplot(gs[data_info["channels"],1])
        self.x_control.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.x_control.axes.yaxis.set_ticks([])
        self.x_control.set_facecolor(self.axis_bg_color)
        self.x_control.get_shared_x_axes().join(self.x_control, *self.channels)
        # self.setup_vertical_span_selector(self.x_control)

        self.canvas.draw()
        self.canvas.flush_events()

    def setup_span_widgets(self, ch_ind):
        group_box = QGroupBox(self.verticalSpanResultWidget)
        group_box.setTitle("channel " + str(ch_ind+1))
        layout = QFormLayout()
        min_lineEdit = QLineEdit()
        max_lineEdit = QLineEdit()
        diff_lineEdit = QLineEdit()
        min_lineEdit.setReadOnly(True)
        max_lineEdit.setReadOnly(True)
        diff_lineEdit.setReadOnly(True)
        self.span_result_widgets.append((ch_ind+1,min_lineEdit, max_lineEdit, diff_lineEdit))
        layout.addRow(QLabel("min : "), min_lineEdit)
        layout.addRow(QLabel("max : "), max_lineEdit)
        layout.addRow(QLabel("diff : "), diff_lineEdit)
        group_box.setLayout(layout)
        self.verticalSpanResultLayout.addWidget(group_box)

    def setup_horizontal_span_selector(self):
        self.hor_span = SpanSelector(
        self.channels[0],
        self.on_horizontal_span_selected,
        "horizontal",
        useblit=True,
        props=dict(alpha=0.5, facecolor="tab:red"),
        interactive=True,
        drag_from_anywhere=True,
        ignore_event_outside=True
        )
        self.hor_span_2 = SpanSelector(
            self.channels[-1],
            lambda : print(),
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:red"),
            interactive=True,
            drag_from_anywhere=True,
            ignore_event_outside=True
            # span_stays=True,  # Add this to make SpanSelector persistent
        )
        self.hor_span_2.set_active(False)
        self.hor_span_2.set_visible(False)

    def setup_vertical_span_selector(self,controller, ax):
        ver_span_on_controller = SpanSelector(
                controller,
                self.on_vertical_span_selected,
                "vertical",
                useblit=True,
                props=dict(alpha=0.5, facecolor="tab:blue"),
                interactive=True,
                drag_from_anywhere=True,
                ignore_event_outside=True
                )
        # ver_span = ax.axhspan(0, 0.01, facecolor ='blue', alpha = 0.5, zorder=10)
        ver_span = SpanSelector(
            ax,
            lambda : print(),
            "vertical",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True,
            ignore_event_outside=True
            # span_stays=True,  # Add this to make SpanSelector persistent
        )
        ver_span.set_active(False)
        ver_span.set_visible(False)
        self.vertical_span_list.append((controller,ver_span_on_controller,ver_span))

    def style_channels(self, axis):
        axis.set_facecolor(self.axis_bg_color)
        axis.spines['bottom'].set_color(self.plot_detail_color)
        axis.spines['top'].set_color(self.plot_detail_color)
        axis.spines['right'].set_color(self.plot_detail_color)
        axis.spines['left'].set_color(self.plot_detail_color)
        axis.grid(axis='both', ls='--', alpha=0.4)
        axis.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.fig_color)
           
    def on_horizontal_span_selected(self, xmin, xmax):
        # feed widgets
        self.HSMinLineEdit.setText(str(round(xmin, 2)))
        self.HSMaxLineEdit.setText(str(round(xmax, 2)))
        self.HSDiffLineEdit.setText(str(round(xmax - xmin, 2)))

        # second span
        self.hor_span_2.set_visible(True)
        self.hor_span_2.extents = (xmin, xmax)


    def on_vertical_span_selected(self, ymin, ymax):
        ver_span = None
        index = 0
        for item in self.vertical_span_list:
            if item[0] == self.current_axis:
                index = self.vertical_span_list.index(item) + 1
                ver_span = item[2]
                break
            
         # feed widgets
        for wid in self.span_result_widgets:
            if index == wid[0]:
                wid[1].setText(str(round(ymin, 2)))
                wid[2].setText(str(round(ymax, 2)))
                wid[3].setText(str(round(ymax - ymin, 2)))
                break

        # second span
        # ver_span.set_active(False)
        ver_span.set_visible(True)
        if ver_span:
            ver_span.extents = (ymin, ymax)



    @pyqtSlot(dict)
    def prepare_data_request(self, data_info):
        self.setup_channels(data_info)
        new_info = data_info
        new_info["file"] = self.file_path
        self.fileInfoReceived.emit(new_info, self.req_range)

    @pyqtSlot(list)
    def feed(self, data_list):
        if len(self.plot_containers) != 0:
            for line in self.plot_containers:
                line.set_data([], [])
        for item in zip(self.channels, data_list):
            line , =item[0].plot(item[1].key, item[1].data, linestyle='-', marker='o', markersize=2, color="#00A36C")
            self.plot_containers.append(line)
            min_x = np.amin(item[1].key) if len(item[1].key) > 1 else (item[1].key)[0]
            max_x = np.amax(item[1].key) if len(item[1].key) > 1 else (item[1].key)[0]
            min_y = np.amin(item[1].data) if len(item[1].data) > 1 else (item[1].data)[0]
            max_y = np.amax(item[1].data) if len(item[1].data) > 1 else (item[1].data)[0]
            y_range = max_y - min_y
            x_tol = 0
            y_tol = y_range/2
            if self.first_feed:
                self.x_limit_range = (min_x - x_tol, max_x + x_tol)
                self.y_limit_range = (min_y - y_tol, max_y + y_tol)
                self.first_feed = False
            self.rescale((min_x - x_tol, max_x + x_tol),(min_y - y_tol, max_y + y_tol))

        self.canvas.draw()
        self.canvas.flush_events()

    def on_mouse_press(self, event):
        self.current_axis = event.inaxes
        if event.inaxes in self.channels:
            if event.dblclick:
                if event.button == 1:
                    self.x_show_range = self.x_limit_range
                    self.zoom_timer.start(100)
                elif event.button == 3:
                    self.hor_span.set_active(False)
                    self.hor_span.set_visible(False)
                    # self.hor_span_2.remove()
                    self.hor_span_2.set_active(False)
                    self.hor_span_2.set_visible(False)
                    for item in self.vertical_span_list:
                        item[1].set_active(False)
                        item[1].set_visible(False)
                        item[2].set_active(False)
                        item[2].set_visible(False)
                        # item[2].remove()
                    self.canvas.flush_events()
                    self.canvas.draw()
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
            self.x_show_range = (new_x_start,new_x_end)
            self.zoom_timer.start(1)

    def on_mouse_release(self, event):
        self.drag_mode = False       

    def rescale(self, x_range = -1, y_range = -1):
        if x_range == -1 or y_range == -1 :
            x_range = self.x_limit_range
            y_range = self.y_limit_range
        for axis in self.channels:
            axis.set_xlim(x_range)
            axis.set_ylim(y_range)
        # self.canvas.draw()
        # self.canvas.flush_events()

    def zoom_on_wheel(self, event):
        if event.inaxes in self.channels:
            xdata = event.xdata
            cur_xlim = self.channels[0].get_xlim()
            dis_start = xdata - cur_xlim[0]
            dis_end = cur_xlim[1] - xdata
            zoom_margin = min(dis_start, dis_end)

            if event.button == 'up':
                scale_factor = self.zoom_base_scale
            elif event.button == 'down':
                # scale_factor = 1 + (1 - self.zoom_base_scale)
                scale_factor = 1 + self.zoom_base_scale
            else: 
                scale_factor = 1
                print(event.button)

            new_x_start = xdata - zoom_margin*scale_factor
            new_x_end = xdata + zoom_margin*scale_factor

            if(new_x_start < self.x_limit_range[0]):
                new_x_start = self.x_limit_range[0]
            if(new_x_end > self.x_limit_range[1]):
                new_x_end = self.x_limit_range[1]

            self.x_show_range = (new_x_start,new_x_end)
            self.zoom_timer.start(10)

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
            file_name = os.path.basename(file_path)
            self.FileNameLabel.setText(file_name)
        if self.default_view:
            self.plotLayout.removeWidget(self.default_view)
            self.default_view.deleteLater()
            self.default_view = None
            self.plotLayout.addWidget(self.canvas)
        self.signal_information.show()

    def on_zoom_timer_timeout(self):
        self.request_data.emit(self.x_show_range)


