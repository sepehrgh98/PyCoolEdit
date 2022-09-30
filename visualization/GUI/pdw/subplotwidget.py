from PyQt5.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QAction, QMenu, QActionGroup
from PyQt5.QtCore import QTimer
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from visualization.GUI.customnavigationtoolbar import MyCustomToolbar as NavigationToolbar
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from matplotlib.widgets import RectangleSelector
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon, QCursor
from visualization.GUI.pdw.historicalzoom import HistoricalZoom
from matplotlib.widgets import MultiCursor
from visualization.visualizationparams import ChannelUnit

from visualization.visualizationparams import ShowPolicy



class SubPlotWidget(QWidget):
    selectionRangeHasBeenSet = pyqtSignal(str, tuple, tuple)
    # selectionRangeHasBeenSet = pyqtSignal(tuple)
    unselectAllRequested = pyqtSignal()
    unselectSpecialArea = pyqtSignal(tuple)
    forwardZoomRequested = pyqtSignal()
    backeardZoomRequested = pyqtSignal()
    resetZoomRequested = pyqtSignal()
    lineCursorDataRequested = pyqtSignal(float)
    pointMarkerDataReady = pyqtSignal(tuple)
    zoom_requested = pyqtSignal(str,tuple,tuple)


    def __init__(self):
        QWidget.__init__(self)
        self.setLayout(QHBoxLayout())

        # variables
        self.mouse_press_ev = None
        self.channel_plot_size = 100
        self.selection_area = []
        # self.selection_area_y = (-1, -1)
        self.show_policy = ShowPolicy.scroll
        self.annote_container = []

        # setup figure
        self.fig = Figure()
        self.fig.patch.set_color('#151a1e')
        self.fig.subplots_adjust(left=0.061, bottom=0.06, right=0.9980, top=0.98, wspace=0.01, hspace=0.1)
        self.fig.tight_layout()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.draw()



        # navtollbar
        self.mpl_toolbar = NavigationToolbar(self.canvas, None)
        self.historical_zoom = HistoricalZoom(self.fig)


        # menu items
        self.available_action = []
        self.canvasMenu = QMenu(self)

        # creating QAction Instances
        self.lineMarkerAction = QAction("Line Marker", self)
        self.pointMarkerAction = QAction("Point Marker", self)
 
        # making actions checkable
        self.lineMarkerAction.setCheckable(True)
        self.pointMarkerAction.setCheckable(True)
 
        # adding these actions to the selection menu
        self.canvasMenu.addAction(self.lineMarkerAction)
        self.canvasMenu.addAction(self.pointMarkerAction)
 
        # creating a action group
        action_group = QActionGroup(self)
 
        # adding these action to the action group
        action_group.addAction(self.lineMarkerAction)
        action_group.addAction(self.pointMarkerAction)

 
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.canvas.customContextMenuRequested.connect(self.exec_canvas_menu)

        self.scroll = QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.plot_container = QWidget()
        layout = QHBoxLayout(self.plot_container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        # self.hist_canvas.setMaximumWidth(150)
        layout.addWidget(self.canvas)
        # layout.addWidget(self.hist_canvas)       
        self.scroll.setWidget(self.plot_container)

        self.layout().addWidget(self.scroll)

        # list to store the axis last used with a mouseclick
        self.curr_ax = []
        self.list_of_select_box = []

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_point_marker_data)
        self.timer.setSingleShot(True)
        

        self.setup_connections()

    def setup_connections(self):
        self.historical_zoom.zoom_requested.connect(self.zoom_requested)
        # self.forwardZoomRequested.connect(self.historical_zoom.next_range)
        # self.backeardZoomRequested.connect(self.historical_zoom.previous_range)
        self.resetZoomRequested.connect(self.historical_zoom.reset)
        self.resetZoomRequested.connect(self.reset_annotates)
        # action connections
        self.lineMarkerAction.triggered.connect(self.setup_line_marker)

    def enable_select_action(self, active):
        if active:
            self.canvas.setCursor(QCursor(Qt.PointingHandCursor))
            if self.historical_zoom.is_active:
                self.historical_zoom.activate(False)
            if self.mpl_toolbar.is_pan():
                self.mpl_toolbar.pan(False)
            [rect.set_active(True) for rect in self.list_of_select_box]
            self.mouse_press_ev = self.canvas.mpl_connect('button_press_event', self.on_mouse_click)

        else:
            self.canvas.setCursor(QCursor(Qt.ArrowCursor))
            [rect.set_active(False) for rect in self.list_of_select_box]
            self.canvas.mpl_disconnect(self.mouse_press_ev)
    
    def enable_normal_action(self, active):
        if active:
            self.enable_select_action(False)
            if self.mpl_toolbar.is_zoom():
                self.mpl_toolbar.zoom(False)
            if self.mpl_toolbar.is_pan():
                self.mpl_toolbar.pan(False)

    def enable_zoom_action(self, active):
        if active:
            self.enable_select_action(False)
            self.enable_select_action(False)
            if self.mpl_toolbar.is_pan():
                self.mpl_toolbar.pan(False)
        self.canvas.setCursor(QCursor(Qt.CrossCursor))
        # self.zoomAction.setChecked(active)
        self.historical_zoom.activate(active)
    
    def enable_pan_action(self, active):
        # self.dragAction.setChecked(active)
        self.mpl_toolbar.pan(active)

    def on_mouse_click(self, event):
        if event.inaxes:
            if event.button == MouseButton.LEFT:
                self.curr_ax[:] = [event.inaxes]
                if self.point_marker.active and event.inaxes in self.fig.axes:
                    self.marked_point = (event.xdata, event.ydata)
                    self.curr_ax[:] = [event.inaxes]
                    x_unit = ChannelUnit['TOA']
                    u = (((self.curr_ax[:])[-1].get_ylabel()).split('('))[-1]
                    y_unit = u[:-1]
                    self.prepare_marked_point(x_unit, y_unit)
            if event.dblclick:
                self.unselectAllRequested.emit()

    def onselect(self, eclick, erelease):
        label = (((self.curr_ax[:])[-1].get_ylabel()).split('('))[0]
        pre_coor = (eclick.xdata, eclick.ydata)
        rel_coor = (erelease.xdata, erelease.ydata)
        if eclick.button == MouseButton.LEFT and erelease.button == MouseButton.LEFT:
            self.selection_area.append((pre_coor[0], rel_coor[0]))
            self.selectionRangeHasBeenSet.emit(label ,(pre_coor[0], rel_coor[0]), (pre_coor[1], rel_coor[1]))
        elif eclick.button == MouseButton.RIGHT and erelease.button == MouseButton.RIGHT:
            f_point = eclick.xdata
            l_point = erelease.xdata
            m_point = (erelease.xdata - eclick.xdata)/2
            for area in self.selection_area:
                if (f_point >= area[0] and f_point <= area[1]) or (l_point >= area[0] and l_point <= area[1]) or (m_point >= area[0] and m_point <= area[1]):
                    self.selection_area.remove(area)
                    self.unselectSpecialArea.emit(area)
                    break

    def get_figure(self):
        return self.fig

    def get_nav_tool(self):
        return self.mpl_toolbar


    @pyqtSlot()
    def setup_rect(self):
        if self.fig.axes:
            self.list_of_select_box = [RectangleSelector(
                ax,
                self.onselect,
                drawtype='box',
                useblit=True,
                button=[1,3],
                minspanx=5, minspany=5,
                spancoords='pixels',
                interactive=False,
            ) for ax in self.fig.axes]
            [rect.set_active(False) for rect in self.list_of_select_box]
        self.historical_zoom.setup_rect()

    def set_fig_size(self):
        if self.show_policy == ShowPolicy.scroll:
            number_of_channels = len(self.fig.axes)
            self.plot_container.setMinimumHeight(number_of_channels*self.channel_plot_size)
            self.plot_container.setMaximumHeight(number_of_channels*self.channel_plot_size) 
        elif self.show_policy == ShowPolicy.non_scroll:
            widget_size = self.parentWidget().size()
            self.plot_container.setMinimumHeight(widget_size.height())
            self.plot_container.setMaximumHeight(widget_size.height()) 

    def exec_canvas_menu(self, point):
        self.last_point = point
        self.canvasMenu.exec_(self.canvas.mapToGlobal(point))

    def clear(self):
        self.fig.clear()
        # self.hist_fig.clear()
        self.curr_ax = []
        self.list_of_select_box = []
        self.canvas.draw()
        # self.hist_canvas.draw()

    def has_selected_area(self):
        return len(self.selection_area)

    def clear_selection_area(self):
        self.selection_area.clear()

    def set_show_policy(self, policy):
        if self.show_policy != policy:
            self.show_policy = policy
            self.set_fig_size()

    @pyqtSlot()
    def setup_line_marker(self):
        self.line_cursor = MultiCursor(self.canvas, tuple(self.fig.axes), color = 'r', lw=1,horizOn=False, vertOn=True, linestyle='--', useblit=True)
        self.line_cursor.set_active(False)

    @pyqtSlot(bool)
    def activate_line_marker(self, active):
        if active:
            self.line_cursor.set_active(True)
            self.point_marker.set_active(False)
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        else:
            self.line_cursor.set_active(False)
        self.canvas.flush_events()
        self.canvas.draw()

    @pyqtSlot()
    def setup_point_marker(self):
        self.point_marker = MultiCursor(self.canvas, tuple(self.fig.axes), color = 'r', lw=1,horizOn=True, vertOn=True, linestyle='--', useblit=True)
        self.point_marker.set_active(False)
        

    @pyqtSlot(bool)
    def activate_point_marker(self, active):
        if active:
            self.point_marker.set_active(True)
            self.line_cursor.set_active(False)
            self.mouse_press_ev = self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        else:
            self.point_marker.set_active(False)
            self.canvas.mpl_disconnect(self.mouse_press_ev)

        self.canvas.flush_events()
        self.canvas.draw()

    def on_mouse_move(self, event):
        if self.line_cursor.active and event.inaxes in self.fig.axes:
            self.lineCursorDataRequested.emit(event.xdata)

        if self.point_marker.active and event.inaxes in self.fig.axes:
            self.marked_point = (event.xdata, event.ydata)
            self.curr_ax[:] = [event.inaxes]
            self.timer.start(500)


    def prepare_marked_point(self, x_unit, y_unit):
        text = str(round(self.marked_point[0],2)) + " " + x_unit +"\n"+ str(round(self.marked_point[1],2)) + " " + y_unit
        annot = (self.curr_ax[:])[-1].annotate("", xy=(self.marked_point[0], self.marked_point[1]), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))

        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)
        self.annote_container.append(annot)
        self.canvas.draw()

    def send_point_marker_data(self):
        self.pointMarkerDataReady.emit(self.marked_point)

    def reset_annotates(self):
        ann_list = self.annote_container
        for ann in ann_list:
            ann.remove()
        self.annote_container.clear()
        self.canvas.draw()









