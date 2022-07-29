import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QLabel, QLineEdit
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import SpanSelector

from visualization.GUI.cursorline import CursorLine

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
        self.data = None
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

        # ui initialize
        self.channelLabel.setText(self._name + " :")
            # local table
        self.tableWidget.setColumnCount(4)
        table_header = [self._name, "Count", "Min", "Max"]
        self.tableWidget.setHorizontalHeaderLabels(table_header)
        # self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            #shared table
        

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
        # self.fig.subplots_adjust(left=0.061, bottom=0.007, right=0.9980, top=0.98, wspace=0, hspace=0.2)
        # self.fig.tight_layout()
        self.fig.suptitle(self._name, fontsize=self.title_size
                          , fontname=self.font_name
                          , fontweight=self.font_weight
                          , color=self.font_color)

        # show line
        self.hist_line_cursor = CursorLine(self.hist_plot, "h")

        # span line
        self.span = SpanSelector(
            self.main_plot,
            self.on_span_selected,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True,
            handle_props=dict(color="red")
        )
        self.span.set_active(False)


        # plot control
        # self.navbar = NavigationToolbar(self.canvas, self.plotWidget)
        # self.plotControlLayout.addWidget(self.navbar)

        self.setup_main_plot()
        self.setup_hist_plot()
        self.plotLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.canvas.flush_events()
        self.setup_connections()
        self.initialize()

    def setup_connections(self):
        self.binSpinBox.valueChanged.connect(self.set_bin)
        self.hist_plot.figure.canvas.mpl_connect('button_press_event', self.hist_line_cursor.on_mouse_pressed)
        self.hist_plot.figure.canvas.mpl_connect('button_release_event', self.hist_line_cursor.on_mouse_released)
        self.hist_line_cursor.data_selected.connect(self.set_thd)
        self.add_tb_btn.clicked.connect(self.feed_local_table)

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
        self.time_range[0] = min(time)
        self.time_range[1] = max(time)
        self.val_range[0] = min(val)
        self.val_range[1] = max(val)

        # set line cursor
        self.hist_line_cursor.set_pos(self.val_range[0])

        # plot
        self.data = val
        self.main_layer, = self.main_plot.plot(time, val, 'o', markersize=0.8, color=self.data_color)
        [self.hist_counts,self.his_bins, self.hist_bars] = self.hist_plot.hist(val, bins=self.bin, color=self.data_color)

        # rescale
        self.main_plot.set_xlim(self.time_range[0], self.time_range[1])

        # update plot
        self.canvas.draw()
        self.canvas.flush_events()

    def feed_local_table(self):
        for bar in self.selected_bar_list:
            val = round(bar._x0 + bar._width/2, 3)
            self.tableWidget.setRowCount(self.row_counter+1)
            self.tableWidget.setItem(self.row_counter, 0, QTableWidgetItem(str(val)))
            self.tableWidget.setItem(self.row_counter, 1, QTableWidgetItem(str(bar._height)))
            self.tableWidget.setItem(self.row_counter, 2, QTableWidgetItem(str(self.val_range[0])))
            self.tableWidget.setItem(self.row_counter, 3, QTableWidgetItem(str(self.val_range[1])))
            self.row_counter += 1
            self.channelLineEdit.setText(str(val))
        
    def set_thd(self, val):
        self.thdLineEdit.setText(str(val))
        for bar in self.hist_bars:
            if bar._height >= val:
                self.selected_bar_list.append(bar)
        
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
                _ = [b.remove() for b in self.hist_bars]
                [self.hist_counts,self.his_bins, self.hist_bars] = self.hist_plot.hist(self.data, bins=self.bin, color=self.data_color)
            self.canvas.draw()
            self.canvas.flush_events()

    def initialize(self):
        self.set_bin(40)

    def set_span(self, active):
        self.span.set_active(active)
        if(active):
            period_label = QLabel(self.controlWidget)
            period_label.setText("Time Period(us):")
            self.period_lineEdit = QLineEdit(self.controlWidget)
            self.controlLayout.addRow(period_label, self.period_lineEdit)
            SCR_label = QLabel(self.controlWidget)
            SCR_label.setText("SCR(MHz) :")
            self.SCR_lineEdit = QLineEdit(self.controlWidget)
            self.controlLayout.addRow(SCR_label, self.SCR_lineEdit)


    def on_span_selected(self, xmin, xmax):
        if self.period_lineEdit and self.SCR_lineEdit:
            pr_us = round((xmax - xmin)/1e6, 3)
            self.period_lineEdit.setText(str(pr_us))
            self.SCR_lineEdit.setText(str(round(1e6 / pr_us,3)))
