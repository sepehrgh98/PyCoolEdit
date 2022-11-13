import os
import re
from tokenize import Double
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QTableView
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import SpanSelector
from visualization.GUI.cursorline import CursorLine
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtCore import Qt
import numpy as np
from visualization.GUI.pdw.historicalzoom import HistoricalZoom

from visualization.pdw.capsulation.capsulator import find_nearest_value_indx

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'radar', 'radarchannelui.ui'))[0]


class RadarChannelForm(QWidget, Form):
    def __init__(self, _id, _name):
        super(RadarChannelForm, self).__init__()
        self.setupUi(self)

        # initialize
        self._id = _id
        self._name = _name

        # variables
        self.bin = None
        self.main_data = () # main input data
        self.spanned_data = () # spanned data
        self.time_req_range = ()
        self.val_req_range = ()
        self.h_span_data = ()
        self.time_range = [-1,-1]
        self.val_range = [-1,-1]
        self.main_layer = None
        self.hist_counts = None
        self.his_bins = None
        self.hist_bars = None
        self.row_counter = 0
        self.selected_bar_list = []
        self.min_bar_res = 10 
        self.period_lineEdit = None
        self.SCR_lineEdit = None
        self.zoom_history = []
        self.current_range_index = 0
        self.spanned_data = None

        # ui initialize
        self.channelLabel.setText(self._name + " :")

        # local table
        self.tableWidget.setColumnCount(6)
        table_header = [self._name, "Count", "Min", "Max", "Average", "STD"]
        self.tableWidget.setHorizontalHeaderLabels(table_header)
        # self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # setup figure
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        axs = self.fig.subplots(2, 1)
        self.main_plot = axs[0]
        self.hist_plot = axs[1]


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
        self.fig.subplots_adjust(left=0.061, bottom=0, right=0.9980, top=0.5, wspace=0, hspace=0.2)
        self.fig.tight_layout()
        self.fig.suptitle(self._name, fontsize=self.title_size
                          , fontname=self.font_name
                          , fontweight=self.font_weight
                          , color=self.font_color)

        # setup icons
        self.zoomBtn.setIcon(QIcon('visualization/Resources/icons/zoom.png'))
        self.cursorLineBtn.setIcon(QIcon('visualization/Resources/icons/linemarker.png'))
        self.backwardZoomBtn.setIcon(QIcon('visualization/Resources/icons/backward.png'))
        self.forwardZoomBtn.setIcon(QIcon('visualization/Resources/icons/forward.png'))
        self.verticalSpanBtn.setIcon(QIcon('visualization/Resources/icons/vertical_span.png'))
        self.horizontalSpanBtn.setIcon(QIcon('visualization/Resources/icons/horizontal_span.png'))
        self.resetBtn.setIcon(QIcon('visualization/Resources/icons/reset.png'))
        self.resetZoomBtn.setIcon(QIcon('visualization/Resources/icons/Home.png'))
        

        # span line
        self.horizontal_span = SpanSelector(
            self.main_plot,
            self.on_horizontal_span_selected,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:red"),
            interactive=True,
            drag_from_anywhere=True,
            handle_props=dict(color="red"),
            ignore_event_outside=True
        )
        self.horizontal_span.set_active(False)
        self.horizontal_span.set_visible(False)


        self.vertical_span = SpanSelector(
            self.main_plot,
            self.on_vertical_span_selected,
            "vertical",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True,
            handle_props=dict(color="blue"),
            ignore_event_outside=True

        )
        self.vertical_span.set_active(False)
        self.vertical_span.set_visible(False)

        # zoom
        self.historical_zoom = HistoricalZoom(self.fig, self.main_plot)
        self.historical_zoom.setup_rect()


        self.setup_main_plot()
        self.setup_hist_plot()
        self.plotLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.canvas.flush_events()
        self.setup_connections()
        self.initialize()

    def setup_connections(self):
        self.binSpinBox.valueChanged.connect(self.set_bin)
        self.add_tb_btn.clicked.connect(self.feed_local_table)
        self.zoomBtn.clicked.connect(self.enable_zoom_action)
        self.verticalSpanBtn.clicked.connect(self.enable_vertical_span)
        self.horizontalSpanBtn.clicked.connect(self.enable_horizontal_span)
        self.resetBtn.clicked.connect(self.reset_tools)
        self.remove_btn.clicked.connect(self.table_remove_last)
        self.cursorLineBtn.clicked.connect(self.setup_cursor_line)
        self.zoomBtn.clicked.connect(self.enable_zoom_action)
        self.backwardZoomBtn.clicked.connect(self.on_backward_zoom_req)
        self.forwardZoomBtn.clicked.connect(self.on_forward_zoom_req)
        self.historical_zoom.zoom_requested.connect(self.on_zoom_req)
        self.resetZoomBtn.clicked.connect(self.rescale)

    def rescale(self):
        self.main_plot.set_xlim(self.time_range)
        self.main_plot.set_ylim(self.val_range)
        self.canvas.draw()        

    def setup_main_plot(self):
        self.main_plot.set_facecolor(self.axis_bg_color)
        self.main_plot.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.main_plot.spines['bottom'].set_color(self.plot_detail_color)
        self.main_plot.spines['top'].set_color(self.plot_detail_color)
        self.main_plot.spines['right'].set_color(self.plot_detail_color)
        self.main_plot.spines['left'].set_color(self.plot_detail_color)
        self.main_plot.grid(axis='both', ls='--', alpha=0.4)

    def setup_hist_plot(self):
        self.hist_plot.set_facecolor(self.axis_bg_color)
        self.hist_plot.tick_params(axis='both', which='major', labelsize=self.tick_size, colors=self.plot_detail_color)
        self.hist_plot.spines['bottom'].set_color(self.plot_detail_color)
        self.hist_plot.spines['top'].set_color(self.plot_detail_color)
        self.hist_plot.spines['right'].set_color(self.plot_detail_color)
        self.hist_plot.spines['left'].set_color(self.plot_detail_color)
        self.hist_plot.grid(axis='both', ls='--', alpha=0.4)

    def feed(self, time, val):
        # set range
        self.time_range = (time[0], time[-1])
        self.val_range = (np.amin(val) , np.amax(val))
        self.time_req_range = self.time_range
        self.val_req_range = self.val_range
        
        # store data
        self.main_data = (time, val)
        self.spanned_data = (time, val)

        # plot
        self.zoom_history.append(self.main_data)
        self.update_mainplot(time, val)
        self.update_histogeram(val, self.bin, self.data_color)

        # rescale
        # self.rescale()
        # self.main_plot.set_xlim(self.time_range[0], self.time_range[1])

        # update plot
        self.canvas.draw()
        self.canvas.flush_events()

    def feed_local_table(self):
        for bar in self.selected_bar_list:
            val = round(bar._x0 + bar._width/2, 3)
            self.tableWidget.setRowCount(self.row_counter+1)
            self.tableWidget.setItem(self.row_counter, 0, QTableWidgetItem(str(val)))
            self.tableWidget.setItem(self.row_counter, 1, QTableWidgetItem(str(bar._height)))
            self.tableWidget.setItem(self.row_counter, 2, QTableWidgetItem(str(max(self.spanned_data[1]))))
            self.tableWidget.setItem(self.row_counter, 3, QTableWidgetItem(str(min(self.spanned_data[1]))))
            self.tableWidget.setItem(self.row_counter, 4, QTableWidgetItem(str(round(np.average(self.spanned_data[1]),2))))
            self.tableWidget.setItem(self.row_counter, 5, QTableWidgetItem(str(round(np.std(self.spanned_data[1]),2))))
            self.row_counter += 1
            self.channelLineEdit.setText(str(val))
        
    def set_thd(self, val):
        self.thdLineEdit.setText(str(val))
        for bar in self.hist_bars:
            if bar._height >= val:
                self.selected_bar_list.append(bar)


    @pyqtSlot(str, tuple, tuple)
    def on_zoom_req(self,ch_name, time_range, value_range):
        current_channel_time_list = self.main_data[0]
        current_channel_val_list = self.main_data[1]

        if time_range == (-1,) :
            first_x_index = 0
            last_x_index = len(current_channel_time_list) - 1
        else:
            may_first_x_index = find_nearest_value_indx(current_channel_time_list, time_range[0])
            f_ind_val = current_channel_time_list[may_first_x_index]
            f_indices = np.where(current_channel_time_list == f_ind_val)[0]
            first_x_index = f_indices[0]
            may_last_x_index = find_nearest_value_indx(current_channel_time_list, time_range[1])
            l_ind_val = current_channel_time_list[may_last_x_index]
            l_indices = np.where(current_channel_time_list == l_ind_val)[0]
            last_x_index = l_indices[-1]

        if value_range == (-1,):
            min_val = np.amin(current_channel_val_list)
            max_val = np.amax(current_channel_val_list)
            value_range = (min_val, max_val)


        req_time = current_channel_time_list[first_x_index:last_x_index+1]
        req_val = current_channel_val_list[first_x_index:last_x_index+1]

        final_key = []
        final_val = []
        for key, val in zip(req_time, req_val):
            if val >= value_range[0] and val <= value_range[1]:
                final_key.append(key)
                final_val.append(val)

        self.spanned_data = (final_key, final_val)
        self.zoom_history.append(self.spanned_data)
        self.current_range_index += 1
        self.update_mainplot(final_key, final_val)
        self.update_histogeram(final_val, self.bin, self.data_color)
        # set range
        time_edge = [-1,-1]
        val_edge = [-1,-1]
        time_edge[0] = min(final_key)
        time_edge[1] = max(final_key)
        val_edge[0] = min(final_val)
        val_edge[1] = max(final_val)
        self.time_req_range = time_edge
        self.val_req_range = val_edge

    def on_forward_zoom_req(self):
        req_index = self.current_range_index +1
        if req_index < len(self.zoom_history):
            data = self.zoom_history[req_index]
            self.update_mainplot(data[0], data[1])
            self.update_histogeram(data[1], self.bin, self.data_color)
            self.current_range_index += 1


    def on_backward_zoom_req(self):
        req_index = self.current_range_index - 1
        if req_index >= 0 :
            data = self.zoom_history[req_index]
            self.update_mainplot(data[0], data[1])
            self.update_histogeram(data[1], self.bin, self.data_color)
            self.current_range_index -= 1

            if self.current_range_index == 0:
                original_data  = self.zoom_history[0]
                self.zoom_history.clear()
                self.zoom_history.append(original_data)

        
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, _id):
        self._id = _id

    @pyqtSlot(int)
    def set_bin(self, value):
        if self.bin != value:
            self.bin = value
            if self.hist_bars:
            #     _ = [b.remove() for b in self.hist_bars]
                self.update_histogeram(self.spanned_data[1], self.bin, self.data_color)
            self.canvas.draw()
            self.canvas.flush_events()

    def initialize(self):
        self.set_bin(40)

    def setup_TimePeriod_SCR(self):
        period_label = QLabel(self.controlWidget)
        period_label.setText("Time Period(us):")
        self.period_lineEdit = QLineEdit(self.controlWidget)
        self.controlLayout.addRow(period_label, self.period_lineEdit)
        SCR_label = QLabel(self.controlWidget)
        SCR_label.setText("SCR(MHz) :")
        self.SCR_lineEdit = QLineEdit(self.controlWidget)
        self.controlLayout.addRow(SCR_label, self.SCR_lineEdit)

    def on_horizontal_span_selected(self, xmin, xmax):
        self.time_req_range = (xmin, xmax)
        self.prepare_histogeram_data()
        self.HSMinLineEdit.setText(str(round(xmin, 2)))
        self.HSMaxLineEdit.setText(str(round(xmax,2)))
        self.HSDeltaTLineEdit.setText(str(round(xmax-xmin,2)))
        if self.period_lineEdit and self.SCR_lineEdit:
            pr_us = round((xmax - xmin)/1e6, 3)
            self.period_lineEdit.setText(str(pr_us))
            self.SCR_lineEdit.setText(str(round(1e6 / pr_us,3)))

    def on_vertical_span_selected(self, ymin, ymax):
        self.val_req_range = (ymin, ymax)
        self.prepare_histogeram_data()
        self.VSMinLineEdit.setText(str(round(ymin, 2)))
        self.VSMaxLineEdit.setText(str(round(ymax, 2)))
        self.VSDeltaTLineEdit.setText(str(round(ymax-ymin, 2)))

    def enable_zoom_action(self, active):
        self.canvas.setCursor(QCursor(Qt.CrossCursor))
        self.historical_zoom.activate(active)
        self.vertical_span.set_active(False)
        self.horizontal_span.set_active(False)

    def enable_vertical_span(self):
        if self.historical_zoom.is_active:
            self.historical_zoom.activate(False)
        self.vertical_span.set_active(True)
        self.horizontal_span.set_active(False)
        self.canvas.setCursor(QCursor(Qt.SplitVCursor))

    def enable_horizontal_span(self):
        if self.historical_zoom.is_active:
            self.historical_zoom.activate(False)
        self.horizontal_span.set_active(True)
        self.vertical_span.set_active(False)
        self.canvas.setCursor(QCursor(Qt.SplitHCursor))

    def reset_tools(self):
        if self.historical_zoom.is_active:
            self.historical_zoom.activate(False)
        self.horizontal_span.set_active(False)
        self.vertical_span.set_active(False)
        self.horizontal_span.set_visible(False)
        self.vertical_span.set_visible(False)
        self.historical_zoom.reset()
        self.canvas.setCursor(QCursor(Qt.ArrowCursor))
        self.canvas.draw()

    def table_remove_last(self):
        last_index = self.tableWidget.rowCount()
        self.tableWidget.removeRow(last_index-1)

    def update_histogeram(self, data, bin, color):
        if self.hist_bars:
            _ = [b.remove() for b in self.hist_bars]
        [self.hist_counts,self.his_bins, self.hist_bars] = self.hist_plot.hist(data, bins=bin, color=color)
        self.canvas.draw()
        self.canvas.flush_events()

    def update_mainplot(self, time, data):
        self.main_plot.clear()
        self.main_layer, = self.main_plot.plot(time, data, 'o', markersize=0.8, color=self.data_color)
        self.canvas.draw()
        self.canvas.flush_events()

    def prepare_histogeram_data(self):
        full_time = self.main_data[0]
        full_data = self.main_data[1]

        start_time_index = find_nearest_value_indx(full_time, self.time_req_range[0])
        end_time_index = find_nearest_value_indx(full_time, self.time_req_range[1])

        req_index = set(full_time[start_time_index:end_time_index+1])
        limited_time = []
        limited_data = []
        for item in req_index:
            idxs = (np.where(full_time == item))[0]
            for ind in idxs:
                val = full_data[ind]
                if val >= self.val_req_range[0] and val <= self.val_req_range[1]: 
                    limited_time.append(full_time[ind])
                    limited_data.append(full_data[ind])
        limited_time = np.asarray(limited_time, dtype=object)
        limited_data = np.asarray(limited_data, dtype=object)
        self.update_histogeram(limited_data, self.bin, self.data_color)

        self.spanned_data = (limited_time, limited_data)

    def setup_cursor_line(self, active):
        if active:
            self.hist_line_cursor = CursorLine(self.hist_plot, "h")
            self.hist_line_cursor.set_pos(self.val_range[0])
            self.hist_plot.figure.canvas.mpl_connect('button_press_event', self.hist_line_cursor.on_mouse_pressed)
            self.hist_plot.figure.canvas.mpl_connect('button_release_event', self.hist_line_cursor.on_mouse_released)
            self.hist_line_cursor.data_selected.connect(self.set_thd)
        else:
            self.hist_line_cursor.remove()

    def setup_shared_table(self, model, header):
        # self.sharedTableWidget.setColumnCount(len(header.keys())+8)
        table_header = []
        for id , channel in header.items():
            table_header.append(channel[0]+'('+channel[1]+')')
        table_header.extend(['SCT(s)','SCP(Hz)','SCR(deg)','Emmiter','PLT','count', 'F.Time','L.Time'])

        # model.set(table_header)
        self.sharedTable = QTableView(self)
        self.sharedTable.setModel(model)
        self.sharedTableLayout.addWidget(self.sharedTable)
        
  